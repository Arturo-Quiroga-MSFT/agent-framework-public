"""
agents/pptx_builder.py
----------------------
PPTX Builder Agent — two-model pipeline:

  Step 1  gpt-5.4           → generate structured slide content (JSON)
  Step 2  gpt-5.3-codex     → generate python-pptx code from that JSON
  Step 3  local Python exec → run the generated code to produce the .pptx file

Streams progress events back to the caller.
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import re
import traceback
from pathlib import Path
from typing import AsyncIterator
from urllib.parse import urlparse

import requests as _requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
from dotenv import load_dotenv
from .slide_helpers import (
    ALLOWED_IMAGE_HOSTS,
    make_presentation,
    add_title_slide,
    add_content_slide,
    add_content_slide_with_image,
    add_two_column_slide,
    add_section_break_slide,
    add_references_slide,
    add_closing_slide,
)

load_dotenv(Path(__file__).parent.parent / ".env")

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
CONTENT_MODEL         = os.getenv("CONTENT_MODEL", "gpt-5.4")       # slide content
CODE_MODEL            = os.getenv("CODE_MODEL",    "gpt-5.3-codex") # python-pptx code
TAVILY_API_KEY        = os.getenv("TAVILY_API_KEY", "")


def _search_image_for_slide(query: str) -> tuple[str, str] | None:
    """
    Call Tavily Search with include_images=True; return (image_url, source_url)
    for the first PNG/JPG from an allowed Microsoft host, or None.
    """
    if not TAVILY_API_KEY:
        return None
    try:
        r = _requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "include_images": True,
                "max_results": 5,
                "search_depth": "basic",
            },
            timeout=12,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        results = data.get("results", [])
        for img_url in data.get("images", []):
            host = urlparse(img_url).hostname or ""
            is_allowed = any(host == h or host.endswith("." + h) for h in ALLOWED_IMAGE_HOSTS)
            is_raster  = img_url.lower().split("?")[0].endswith((".png", ".jpg", ".jpeg"))
            if is_allowed and is_raster:
                # Find the source page URL from search results (best-effort)
                source_url = next(
                    (res.get("url", "") for res in results
                     if urlparse(res.get("url", "")).hostname and
                     urlparse(res.get("url", "")).hostname.split(".")[-2:] == ["microsoft", "com"]),
                    ""
                )
                return img_url, source_url
    except Exception:
        pass
    return None


def _make_client() -> OpenAI:
    """Responses API client: base_url /openai/v1/, token provider as api_key."""
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return OpenAI(
        base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/v1/",
        api_key=token_provider,
    )

CONTENT_SYSTEM = """\
You are a senior presentation strategist and visual storyteller.
Given a topic or brief, produce a polished, complete slide deck outline as JSON.

Output ONLY valid JSON — no markdown fences, no explanation.

Top-level schema:
{
  "title": "Deck Title",
  "theme": "professional|modern|minimal|bold",
  "slides": [ ...slide objects... ]
}

Slide object schemas by layout:

1. layout = "title"  (opening slide — always slide 1)
   { "index":1, "layout":"title", "title":"...", "subtitle":"...", "notes":"..." }

2. layout = "section_break"  (used between major sections, 2-3 per deck)
   { "index":N, "layout":"section_break", "title":"...", "subtitle":"One sentence framing the section", "notes":"..." }

3. layout = "content"  (single-column bullets — most common body slide)
   { "index":N, "layout":"content", "title":"...", "bullets":["...","..."], "notes":"..." }

4. layout = "two_column"  (side-by-side comparison or contrast)
   { "index":N, "layout":"two_column", "title":"...",
     "left_title":"...", "left_bullets":["..."],
     "right_title":"...", "right_bullets":["..."],
     "notes":"..." }

6. layout = "content_with_image"  (content slide + image from an approved Microsoft source)
   { "index":N, "layout":"content_with_image", "title":"...",
     "bullets":["...","..."],
     "image_search_query": "specific search query to find a diagram or screenshot on learn.microsoft.com",
     "notes":"..." }
   Use this for 1-3 slides where an official architecture diagram, screenshot, or
   concept illustration from learn.microsoft.com or devblogs.microsoft.com would
   genuinely improve comprehension. Only use when a real diagram exists.

7. layout = "references"  (second-to-last slide — always include when web sources were used)
   { "index":N, "layout":"references", "title":"Sources & References",
     "links":[{"text":"Display title of the source","url":"https://..."},...],
     "notes":"..." }

8. layout = "closing"  (last slide — call to action or thank you)
   { "index":N, "layout":"closing", "title":"...", "subtitle":"CTA or contact info", "notes":"..." }

Content rules:
- 10-14 slides total (references + closing count toward total)
- ALWAYS start with layout=title and end with layout=closing
- ALWAYS include a layout=references slide as the second-to-last slide; populate links with every web source you consulted
- Use content_with_image for 1-3 slides where an official Microsoft diagram would help (architecture, flow, concept)
- Use section_break to open each major section (every 3-4 content slides)
- Use two_column for comparisons, before/after, pros/cons (at least 2 per deck)
- Bullets: outcome-focused, 8-12 words, use concrete numbers/metrics where plausible
- left_bullets and right_bullets: 3-5 items each
- content bullets: 4-6 items
- Speaker notes: 2-3 sentences expanding on the slide, not just repeating it
- Choose theme to match the subject: professional=corporate, modern=tech/startup,
  minimal=design/creative, bold=sales/impact
- The JSON must be parseable by Python json.loads() — no trailing commas
"""

CODE_SYSTEM = """\
You are a Python code generator for presentation building.
You will receive a JSON slide deck spec and must output a complete Python script.

The following functions are ALREADY available in the execution scope — do NOT import anything:

    make_presentation()                         → returns a new Presentation
    add_title_slide(prs, title, subtitle="", notes="", theme_name=THEME)
    add_content_slide(prs, title, bullets=[], notes="", theme_name=THEME)
    add_two_column_slide(prs, title,
                         left_title="", left_bullets=[],
                         right_title="", right_bullets=[],
                         notes="", theme_name=THEME)
    add_section_break_slide(prs, title, subtitle="", notes="", theme_name=THEME)
    add_content_slide_with_image(prs, title, bullets=[], image_url="", image_caption="", notes="", theme_name=THEME)
    add_references_slide(prs, title, links=[], notes="", theme_name=THEME)
    # links = list of {"text": "Source display title", "url": "https://..."} dicts
    add_closing_slide(prs, title, cta="", notes="", theme_name=THEME)

Two variables are also pre-set:
    THEME       — theme name string from the JSON spec (e.g. "professional")
    OUTPUT_PATH — absolute path where the .pptx file must be saved

Layout → function mapping:
    "title"        → add_title_slide
    "section_break"→ add_section_break_slide
    "content"      → add_content_slide
    "two_column"   → add_two_column_slide
    "references"   → add_references_slide
    "content_with_image" → add_content_slide_with_image
    "closing"      → add_closing_slide
    anything else  → add_content_slide

Script structure (always exactly this pattern):

    prs = make_presentation()
    # one function call per slide, in order
    add_title_slide(prs, "Title Here", subtitle="Subtitle", theme_name=THEME)
    add_section_break_slide(prs, "Section Name", subtitle="Framing sentence", theme_name=THEME)
    add_content_slide(prs, "Slide Title", bullets=["Point one", "Point two"], theme_name=THEME)
    add_two_column_slide(prs, "Compare",
                         left_title="A", left_bullets=["x", "y"],
                         right_title="B", right_bullets=["x", "y"],
                         theme_name=THEME)
    add_closing_slide(prs, "Thank You", cta="Next steps...", theme_name=THEME)
    prs.save(OUTPUT_PATH)

Rules:
- Do NOT import anything
- Do NOT call Presentation() directly — use make_presentation()
- Always pass theme_name=THEME to every slide function
- The last line must be: prs.save(OUTPUT_PATH)
- Output ONLY the Python code — no markdown fences, no explanation
"""


class PPTXBuilder:
    """Two-model pipeline: content (gpt-5.4) → code (gpt-5.3-codex) → file."""

    def __init__(self):
        pass  # client created per-request

    async def build(
        self,
        brief: str,
        output_dir: str | Path = "/tmp",
    ) -> AsyncIterator[dict]:
        """
        Async generator yielding progress events as dicts:

            {"type": "status",   "message": "..."}
            {"type": "content",  "json": {...}}       # after step 1
            {"type": "code",     "python": "..."}     # after step 2
            {"type": "done",     "file_path": "..."}  # on success
            {"type": "error",    "message": "..."}    # on failure
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        loop = asyncio.get_event_loop()

        import time as _time
        t_start = _time.monotonic()
        _token_usage: list[dict] = []

        def _call_responses(model: str, system: str, user: str) -> str:
            """Call Responses API synchronously in executor, return full text."""
            client = _make_client()
            result = []
            stream = client.responses.create(
                model=model,
                instructions=system,
                input=[{"role": "user", "content": user}],
                tools=[{"type": "web_search_preview"}],
                stream=True,
            )
            for event in stream:
                if event.type == "response.output_text.delta":
                    result.append(event.delta)
                elif event.type == "response.completed":
                    u = getattr(event.response, "usage", None)
                    if u:
                        _token_usage.append({
                            "model": model,
                            "input_tokens":  getattr(u, "input_tokens",  0),
                            "output_tokens": getattr(u, "output_tokens", 0),
                            "total_tokens":  getattr(u, "total_tokens",  0),
                        })
            return "".join(result)

        # ── STEP 1: Generate slide content JSON with gpt-5.4 ──────────────
        yield {"type": "status", "message": "Step 1/3 — Generating slide content with gpt-5.4…"}

        content_json_raw = await loop.run_in_executor(
            None, _call_responses,
            CONTENT_MODEL, CONTENT_SYSTEM,
            f"Create a presentation on the following brief:\n\n{brief}",
        )

        # Parse JSON — strip any accidental fences
        clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", content_json_raw.strip(), flags=re.MULTILINE)
        try:
            slide_spec = json.loads(clean_json)
        except json.JSONDecodeError as exc:
            yield {"type": "error", "message": f"Content model returned invalid JSON: {exc}\n\nRaw output:\n{content_json_raw[:500]}"}
            return

        yield {"type": "content", "json": slide_spec}
        yield {"type": "status", "message": f"Step 1 complete — {len(slide_spec.get('slides', []))} slides planned."}

        # ── STEP 1.5: Enrich content_with_image slides via Tavily ─────────
        image_slides = [
            s for s in slide_spec.get("slides", [])
            if s.get("layout") == "content_with_image" and s.get("image_search_query")
        ]
        if image_slides and TAVILY_API_KEY:
            yield {"type": "status", "message": f"Step 1.5 — Searching for {len(image_slides)} slide image(s)…"}
            for slide in image_slides:
                query  = slide.pop("image_search_query")
                result = await loop.run_in_executor(None, _search_image_for_slide, query)
                if result:
                    img_url, src_url = result
                    slide["image_url"]     = img_url
                    slide["image_caption"] = src_url or urlparse(img_url).hostname
                else:
                    # Downgrade to plain content if no image found
                    slide["layout"] = "content"
                    slide.pop("image_url", None)
                    slide.pop("image_caption", None)
        elif image_slides:
            # No Tavily key — downgrade all gracefully
            for slide in image_slides:
                slide["layout"] = "content"
                slide.pop("image_search_query", None)

        # ── STEP 2: Generate python-pptx code with gpt-5.3-codex ──────────
        yield {"type": "status", "message": "Step 2/3 — Generating python-pptx code with gpt-5.3-codex…"}

        python_code = await loop.run_in_executor(
            None, _call_responses,
            CODE_MODEL, CODE_SYSTEM,
            f"Generate the python-pptx script for this slide spec:\n\n{json.dumps(slide_spec, indent=2)}",
        )

        # Strip accidental fences
        python_code = re.sub(r"^```(?:python)?\s*|\s*```$", "", python_code.strip(), flags=re.MULTILINE)
        yield {"type": "code", "python": python_code}
        yield {"type": "status", "message": "Step 2 complete — python-pptx code generated."}

        # ── STEP 3: Execute the generated code locally ─────────────────────
        yield {"type": "status", "message": "Step 3/3 — Executing code to build the PPTX file…"}

        safe_title = re.sub(r"[^\w\s-]", "", slide_spec.get("title", "presentation"))
        safe_title = re.sub(r"\s+", "_", safe_title.strip())[:60]
        output_path = output_dir / f"{safe_title}.pptx"

        namespace = {
            "OUTPUT_PATH":              str(output_path),
            "THEME":                    slide_spec.get("theme", "professional"),
            "make_presentation":        make_presentation,
            "add_title_slide":          add_title_slide,
            "add_content_slide":        add_content_slide,            "add_content_slide_with_image": add_content_slide_with_image,            "add_two_column_slide":     add_two_column_slide,
            "add_section_break_slide":  add_section_break_slide,
            "add_references_slide":     add_references_slide,
            "add_closing_slide":        add_closing_slide,
        }
        try:
            exec(compile(python_code, "<generated>", "exec"), namespace)  # noqa: S102
        except Exception:
            yield {
                "type": "error",
                "message": f"Code execution failed:\n{traceback.format_exc()}",
            }
            return

        if not output_path.exists():
            yield {"type": "error", "message": f"Code ran but no file was created at {output_path}"}
            return

        yield {"type": "done", "file_path": str(output_path)}

        elapsed = round(_time.monotonic() - t_start, 1)
        total_in  = sum(u["input_tokens"]  for u in _token_usage)
        total_out = sum(u["output_tokens"] for u in _token_usage)
        yield {
            "type": "telemetry",
            "elapsed_s": elapsed,
            "total_tokens": total_in + total_out,
            "input_tokens": total_in,
            "output_tokens": total_out,
            "calls": _token_usage,
        }
