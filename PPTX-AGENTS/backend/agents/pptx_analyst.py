"""
agents/pptx_analyst.py
----------------------
PPTX Analyst Agent — powered by gpt-5.3-codex.

Accepts a file path + optional user question.
Analyses the presentation using:
  1. Full-text extraction (markitdown) for rich text context
  2. Slide images (base64 PNG) for visual / diagram understanding

Streams its response back via an async generator.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncIterator

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AgentsApiResponseFormatOption,
    MessageRole,
)
from dotenv import load_dotenv

from shared.pptx_utils import extract_text, render_slides_to_images, slide_count, slide_titles

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
ANALYST_MODEL    = os.getenv("ANALYST_MODEL", "gpt-5.3-codex")

SYSTEM_PROMPT = """\
You are an expert presentation analyst. You receive a PowerPoint presentation —
both its extracted text content and visual slide images — and produce structured,
insightful analysis.

When analysing, always cover:
1. **Executive summary** — what is this presentation about and what is its goal?
2. **Key messages** — the 3-5 most important points being made
3. **Narrative structure** — how the story flows across slides
4. **Data & evidence** — key statistics, charts, or claims (and their strength)
5. **Gaps & weaknesses** — what is missing, unclear, or unsupported?
6. **Audience & tone** — who is this for and what is the communication style?
7. **Actionable recommendations** — concrete improvements if asked

If the user asks a specific question, answer it first, then provide the above
structured analysis. Be direct, precise, and business-focused.
"""


class PPTXAnalyst:
    """Streams analysis of a PPTX file using gpt-5.3-codex."""

    def __init__(self):
        self.credential = DefaultAzureCredential()

    async def analyse(
        self,
        pptx_path: str | Path,
        user_question: str = "Please provide a full analysis of this presentation.",
    ) -> AsyncIterator[str]:
        """
        Async generator — yields text chunks as the model streams them.

        Usage:
            async for chunk in analyst.analyse("deck.pptx"):
                print(chunk, end="", flush=True)
        """
        pptx_path = Path(pptx_path)
        if not pptx_path.exists():
            raise FileNotFoundError(f"PPTX not found: {pptx_path}")

        # --- Build context ---
        n_slides  = slide_count(pptx_path)
        titles    = slide_titles(pptx_path)
        text_md   = extract_text(pptx_path)
        images_b64 = render_slides_to_images(pptx_path)

        # Build the multimodal message content
        content: list[dict] = [
            {
                "type": "text",
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

        # Attach slide images (model card confirms gpt-5.3-codex is multimodal)
        for i, img_b64 in enumerate(images_b64, 1):
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
            })

        async with AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=self.credential,
        ) as client:
            agent = await client.agents.create_agent(
                model=ANALYST_MODEL,
                name="pptx-analyst",
                instructions=SYSTEM_PROMPT,
            )
            thread = await client.agents.create_thread()

            await client.agents.create_message(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=content,
            )

            # Stream the response
            async with client.agents.create_stream(
                thread_id=thread.id,
                agent_id=agent.id,
            ) as stream:
                async for event_type, event_data, _ in stream:
                    if hasattr(event_data, "delta") and hasattr(event_data.delta, "content"):
                        for block in event_data.delta.content or []:
                            if hasattr(block, "text") and block.text:
                                yield block.text.value or ""

            # Clean up ephemeral agent
            await client.agents.delete_agent(agent.id)
