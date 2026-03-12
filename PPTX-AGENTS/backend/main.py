"""
backend/main.py
---------------
FastAPI backend for PPTX Agents.

Endpoints:
  POST /api/analyse       → SSE stream of analysis text
  POST /api/build         → SSE stream of build progress events
  GET  /api/download/{id} → download a generated PPTX file
  GET  /api/health        → health check
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# Ensure backend/ is on sys.path so shared/ and agents/ resolve
import sys
sys.path.insert(0, str(Path(__file__).parent))

from agents.pptx_analyst import PPTXAnalyst
from agents.pptx_builder import PPTXBuilder

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="PPTX Agents API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR  = Path("/tmp/pptx_agents/uploads")
OUTPUT_DIR  = Path("/tmp/pptx_agents/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# In-memory registry of generated files: { file_id → Path }
_generated_files: dict[str, Path] = {}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "pptx-agents"}


# ---------------------------------------------------------------------------
# Analyse endpoint  (multipart: file + question)
# ---------------------------------------------------------------------------

@app.post("/api/analyse")
async def analyse(
    file: UploadFile = File(...),
    question: str    = Form(default="Please provide a full analysis of this presentation."),
):
    """
    Upload a PPTX file and stream back the analysis as SSE.

    SSE event format:
      data: <text chunk>          (type=message, ongoing analysis text)
      data: [DONE]                (stream complete)
    """
    if not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are supported.")

    # Save upload to temp dir
    upload_id   = uuid.uuid4().hex
    upload_path = UPLOAD_DIR / f"{upload_id}_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    analyst = PPTXAnalyst()

    async def event_generator() -> AsyncIterator[dict]:
        try:
            async for chunk in analyst.analyse(upload_path, question):
                if isinstance(chunk, dict) and chunk.get("__telemetry__"):
                    yield {"data": json.dumps({"type": "telemetry",
                                              "model": chunk["model"],
                                              "elapsed_s": chunk["elapsed_s"],
                                              "input_tokens": chunk["input_tokens"],
                                              "output_tokens": chunk["output_tokens"],
                                              "total_tokens": chunk["total_tokens"]})}
                else:
                    yield {"data": chunk}
        except Exception as exc:
            yield {"data": json.dumps({"error": str(exc)}), "event": "error"}
        finally:
            yield {"data": "[DONE]"}
            upload_path.unlink(missing_ok=True)

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Build endpoint  (JSON body: brief)
# ---------------------------------------------------------------------------

class BuildRequest(BaseModel):
    brief: str


@app.post("/api/build")
async def build(req: BuildRequest):
    """
    Stream PPTX build progress as SSE.

    SSE events (JSON payloads on the data field):
      {"type": "status",  "message": "..."}
      {"type": "content", "json": {...}}
      {"type": "code",    "python": "..."}
      {"type": "done",    "file_id": "...", "filename": "..."}
      {"type": "error",   "message": "..."}
    """
    builder  = PPTXBuilder()
    file_id  = uuid.uuid4().hex

    async def event_generator() -> AsyncIterator[dict]:
        try:
            async for event in builder.build(req.brief, output_dir=OUTPUT_DIR):
                if event["type"] == "done":
                    file_path = Path(event["file_path"])
                    _generated_files[file_id] = file_path
                    yield {
                        "data": json.dumps({
                            "type": "done",
                            "file_id": file_id,
                            "filename": file_path.name,
                        })
                    }
                else:
                    yield {"data": json.dumps(event)}
        except Exception as exc:
            yield {
                "data": json.dumps({"type": "error", "message": str(exc)}),
                "event": "error",
            }
        finally:
            yield {"data": "[DONE]"}

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Download endpoint
# ---------------------------------------------------------------------------

@app.get("/api/download/{file_id}")
async def download(file_id: str):
    """Download a previously generated PPTX file by its file_id."""
    file_path = _generated_files.get(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found or expired.")
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=file_path.name,
    )


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )
