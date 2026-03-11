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
import json
import os
import re
import tempfile
import traceback
from pathlib import Path
from typing import AsyncIterator

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import MessageRole
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from pptx import Presentation

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
CONTENT_MODEL    = os.getenv("CONTENT_MODEL", "gpt-5.4")        # slide content
CODE_MODEL       = os.getenv("CODE_MODEL",    "gpt-5.3-codex")  # python-pptx code

CONTENT_SYSTEM = """\
You are an expert presentation designer and content strategist.
Given a topic or brief, produce a complete slide deck outline as JSON.

Output ONLY valid JSON — no markdown fences, no explanation — in this exact schema:

{
  "title": "Presentation Title",
  "theme": "professional|modern|minimal|bold",
  "slides": [
    {
      "index": 1,
      "layout": "title|content|two_column|image_text|blank",
      "title": "Slide Title",
      "subtitle": "Optional subtitle (title slides only)",
      "bullets": ["point 1", "point 2"],
      "notes": "Speaker notes for this slide"
    }
  ]
}

Rules:
- 8-15 slides for a typical presentation
- Vary layouts (don't use content for every slide)
- Bullets should be punchy, 8-12 words max
- Include speaker notes on every slide
- The JSON must be parseable by Python's json.loads()
"""

CODE_SYSTEM = """\
You are an expert Python developer specialising in python-pptx.
Given a JSON slide deck specification, generate a complete, runnable Python script
that creates the presentation using python-pptx.

Requirements:
- Use python-pptx Presentation, Slide layouts, text frames, paragraphs properly
- Apply consistent font sizes: title=36pt, content=18pt, bullets=16pt
- Use the theme hint in the JSON to choose appropriate RGB colours:
    professional = navy (#003366) headers, white bg
    modern       = dark (#1A1A2E) headers, light grey bg
    minimal      = black headers, white bg
    bold         = deep purple (#4A0080) headers, white bg
- Set slide dimensions to widescreen 16:9 (13.33in x 7.5in)
- Save to OUTPUT_PATH (a variable injected at runtime — do NOT hardcode a filename)
- Import only: pptx, pptx.util, pptx.dml.color, pptx.enum.text — nothing else
- The last line must be: presentation.save(OUTPUT_PATH)
- Output ONLY the Python code — no markdown fences, no explanation
"""


class PPTXBuilder:
    """Two-model pipeline: content (gpt-5.4) → code (gpt-5.3-codex) → file."""

    def __init__(self):
        self.credential = DefaultAzureCredential()

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

        async with AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=self.credential,
        ) as client:

            # ── STEP 1: Generate slide content JSON with gpt-5.4 ──────────
            yield {"type": "status", "message": "Step 1/3 — Generating slide content with gpt-5.4…"}

            content_agent = await client.agents.create_agent(
                model=CONTENT_MODEL,
                name="pptx-content-planner",
                instructions=CONTENT_SYSTEM,
            )
            thread1 = await client.agents.create_thread()
            await client.agents.create_message(
                thread_id=thread1.id,
                role=MessageRole.USER,
                content=f"Create a presentation on the following brief:\n\n{brief}",
            )

            content_json_raw = ""
            async with client.agents.create_stream(
                thread_id=thread1.id,
                agent_id=content_agent.id,
            ) as stream:
                async for _, event_data, _ in stream:
                    if hasattr(event_data, "delta") and hasattr(event_data.delta, "content"):
                        for block in event_data.delta.content or []:
                            if hasattr(block, "text") and block.text:
                                content_json_raw += block.text.value or ""

            await client.agents.delete_agent(content_agent.id)

            # Parse JSON — strip any accidental fences
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", content_json_raw.strip(), flags=re.MULTILINE)
            try:
                slide_spec = json.loads(clean_json)
            except json.JSONDecodeError as exc:
                yield {"type": "error", "message": f"Content model returned invalid JSON: {exc}\n\nRaw output:\n{content_json_raw[:500]}"}
                return

            yield {"type": "content", "json": slide_spec}
            yield {"type": "status", "message": f"Step 1 complete — {len(slide_spec.get('slides', []))} slides planned."}

            # ── STEP 2: Generate python-pptx code with gpt-5.3-codex ──────
            yield {"type": "status", "message": "Step 2/3 — Generating python-pptx code with gpt-5.3-codex…"}

            code_agent = await client.agents.create_agent(
                model=CODE_MODEL,
                name="pptx-code-generator",
                instructions=CODE_SYSTEM,
            )
            thread2 = await client.agents.create_thread()
            await client.agents.create_message(
                thread_id=thread2.id,
                role=MessageRole.USER,
                content=f"Generate the python-pptx script for this slide spec:\n\n{json.dumps(slide_spec, indent=2)}",
            )

            python_code = ""
            async with client.agents.create_stream(
                thread_id=thread2.id,
                agent_id=code_agent.id,
            ) as stream:
                async for _, event_data, _ in stream:
                    if hasattr(event_data, "delta") and hasattr(event_data.delta, "content"):
                        for block in event_data.delta.content or []:
                            if hasattr(block, "text") and block.text:
                                python_code += block.text.value or ""

            await client.agents.delete_agent(code_agent.id)

            # Strip accidental fences
            python_code = re.sub(r"^```(?:python)?\s*|\s*```$", "", python_code.strip(), flags=re.MULTILINE)
            yield {"type": "code", "python": python_code}
            yield {"type": "status", "message": "Step 2 complete — python-pptx code generated."}

            # ── STEP 3: Execute the generated code locally ─────────────────
            yield {"type": "status", "message": "Step 3/3 — Executing code to build the PPTX file…"}

            safe_title = re.sub(r"[^\w\s-]", "", slide_spec.get("title", "presentation"))
            safe_title = re.sub(r"\s+", "_", safe_title.strip())[:60]
            output_path = output_dir / f"{safe_title}.pptx"

            namespace = {"OUTPUT_PATH": str(output_path)}
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
