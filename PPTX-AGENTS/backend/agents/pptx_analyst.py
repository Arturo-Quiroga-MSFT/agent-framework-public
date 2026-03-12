"""
agents/pptx_analyst.py
----------------------
PPTX Analyst Agent — powered by gpt-5.3-codex.

Accepts a file path + optional user question.
Analyses the presentation using:
  1. Full-text extraction (markitdown) for rich text context
  2. Slide images (base64 PNG) for visual / diagram understanding

Streams its response back via an async generator.
Uses azure-ai-projects 2.0.0 via get_openai_client() → streaming chat completions.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import AsyncIterator

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
from dotenv import load_dotenv

from shared.pptx_utils import extract_text, render_slides_to_images, slide_count, slide_titles

load_dotenv(Path(__file__).parent.parent / ".env")

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
ANALYST_MODEL         = os.getenv("ANALYST_MODEL", "gpt-5.3-codex")

SYSTEM_PROMPT = """\
You are an expert presentation analyst. You receive a PowerPoint presentation —
both its extracted text content and visual slide images — and produce structured,
insightful analysis.

CRITICAL — OUTPUT FORMAT RULES (follow exactly):
- Each section MUST start with a clean level-2 heading on its own line: ## Section Title
- The heading line must contain ONLY the section title — never any content after it.
- Leave one blank line after each heading before the content begins.
- Use bullet points (- item) for lists, each on its own separate line.
- For numbered lists (recommendations) use 1. 2. 3. on separate lines.
- Bold key terms with **term** inside sentences — never bold entire sentences.
- Leave one blank line between paragraphs and between bullet points groups.
- Never concatenate multiple points onto a single line separated by dashes.

Always produce exactly these seven sections in this order:

## Executive Summary

One paragraph: what is this presentation about, what is its goal, and who commissioned it?

## Key Messages

A bullet list of the 3–5 most important points being made.

## Narrative Structure

Describe how the story flows across slides. Reference specific slide numbers or ranges.

## Data & Evidence Quality

Assess the strength of data, statistics, and claims. Call out what is evidence-based vs assertion-based.

## Gaps & Weaknesses

A bullet list of what is missing, unclear, or unsupported.

## Audience & Tone

Who is this for? What is the communication style? Is the tone appropriate?

## Actionable Recommendations

A numbered list of concrete improvements, ordered by impact.

If the user asks a specific question, answer it first in a ## Response to Your Question
section, then produce the full structured analysis below it.
Be direct, precise, and business-focused.
"""


def _make_client() -> OpenAI:
    """Responses API sync client: base_url /openai/v1/, token provider as api_key."""
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return OpenAI(
        base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/v1/",
        api_key=token_provider,
    )


class PPTXAnalyst:
    """Streams analysis of a PPTX file using gpt-5.3-codex."""

    def __init__(self):
        pass  # client created per-request (token provider is async-safe)

    async def analyse(
        self,
        pptx_path: str | Path,
        user_question: str = "Please provide a full analysis of this presentation.",
    ) -> AsyncIterator[str]:
        """
        Async generator — yields text chunks as the model streams them.
        """
        pptx_path = Path(pptx_path)
        if not pptx_path.exists():
            raise FileNotFoundError(f"PPTX not found: {pptx_path}")

        # --- Build context ---
        n_slides   = slide_count(pptx_path)
        titles     = slide_titles(pptx_path)
        text_md    = extract_text(pptx_path)
        images_b64 = render_slides_to_images(pptx_path)

        # Build the multimodal input list
        input_content: list[dict] = [
            {
                "type": "input_text",
                "text": (
                    f"**Presentation:** `{pptx_path.name}`\n"
                    f"**Slides:** {n_slides}\n"
                    f"**Slide titles:** {', '.join(t for t in titles if t) or 'N/A'}\n\n"
                    f"---\n\n"
                    f"## Extracted text content\n\n{text_md}\n\n"
                    f"---\n\n"
                    f"## User request\n\n{user_question}"
                ),
            }
        ]

        for img_b64 in images_b64:
            input_content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{img_b64}",
            })

        import asyncio
        import time as _time
        loop = asyncio.get_event_loop()
        t_start = _time.monotonic()

        usage_box: list = []

        def _stream_sync():
            """Run the synchronous Responses API stream in a thread."""
            client = _make_client()
            stream = client.responses.create(
                model=ANALYST_MODEL,
                instructions=SYSTEM_PROMPT,
                input=[{"role": "user", "content": input_content}],
                stream=True,
            )
            chunks = []
            for event in stream:
                if event.type == "response.output_text.delta":
                    chunks.append(event.delta)
                elif event.type == "response.completed":
                    u = getattr(event.response, "usage", None)
                    if u:
                        usage_box.append({
                            "input_tokens":  getattr(u, "input_tokens",  0),
                            "output_tokens": getattr(u, "output_tokens", 0),
                            "total_tokens":  getattr(u, "total_tokens",  0),
                        })
            return chunks

        chunks = await loop.run_in_executor(None, _stream_sync)
        elapsed = round(_time.monotonic() - t_start, 1)
        full_text = "".join(chunks)

        # Normalize Responses API streaming artifacts:
        # Each token delta ends with \n — collapse single \n → space, preserve \n\n.
        full_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', full_text)
        full_text = re.sub(r' {2,}', ' ', full_text)          # collapse double spaces
        full_text = re.sub(r'(\d+) \.', r'\1.', full_text)   # fix "1 ." → "1."
        full_text = re.sub(r'\*\* +', '**', full_text)        # fix "** text" → "**text"
        full_text = re.sub(r' +\*\*', '**', full_text)        # fix "text **" → "text**"
        full_text = full_text.strip()

        yield full_text

        usage = usage_box[0] if usage_box else {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        yield {"__telemetry__": True, "model": ANALYST_MODEL,
               "elapsed_s": elapsed, **usage}

        # Extract actionable recommendations as a structured list
        recs_match = re.search(
            r'##\s+Actionable Recommendations\s*\n(.*?)(?=\n##\s|\Z)',
            full_text, re.DOTALL
        )
        recs = []
        if recs_match:
            items = re.findall(
                r'^\d+\.\s+(.+?)(?=\n\d+\.\s|\Z)',
                recs_match.group(1), re.MULTILINE | re.DOTALL
            )
            recs = [{"id": i + 1, "text": item.strip().replace('\n', ' ')}
                    for i, item in enumerate(items)]
        if recs:
            yield {"__recommendations__": True, "items": recs}
