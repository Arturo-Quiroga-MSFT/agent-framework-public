

### What the model cards actually reveal

| | gpt-5.4 | gpt-5.4-pro | gpt-5.3-codex |
|---|---|---|---|
| **Version** | 2026-03-05 | 2026-03-05 | 2026-02-24 |
| **Type** | Chat completion + Responses | Chat completion + Responses | Responses only |
| **Multimodal** | text + image ✅ | text + image ✅ | text + image ✅ |
| **Context in** | 200k | 200k | **272k** |
| **Context out** | 100k | 100k | **228k** |
| **Positioning** | Capable frontier, balanced | Highest performance version of 5.4 | Steerability, front-end dev, interactivity |
| **Explicitly mentions** | Document/spreadsheet creation, agentic workflows | Same as 5.4, maximum capability | **Design comps, UI states, architecture diagrams**, repo-aware, async execution |

---

### Revised recommendations — the model cards change my earlier advice

**Task A — Analyze a PPTX:**
**gpt-5.3-codex is actually the best fit here**, and I didn't expect that. The reasons:
- Largest context by far (272k in / 228k out) — lets you feed an entire deck as images without chunking
- Explicitly calls out **"architecture diagrams and design comps"** in its multimodal reasoning description — that's exactly what slides are
- "Asynchronous execution with state retention" suits a multi-slide sequential analysis workflow
- The "steerability" positioning means it responds well to structured analytical prompts

**Task B — Create a PPTX:**
**gpt-5.4 is the right call here**, not 5.4-pro. The reasons:
- Explicitly lists **"document and spreadsheet creation"** as a primary use case — that phrasing is deliberate
- Better token efficiency (listed as a capability) → faster generation loop, lower cost per slide iteration
- The python-pptx code generation part also benefits from gpt-5.3-codex specifically (repo-aware, code quality) — worth splitting if you want optimal results

**gpt-5.4-pro** is the right choice when you need maximum reasoning depth on a complex, high-stakes task — e.g., analyzing a confidential business deck and producing executive-level synthesis. It's the quality ceiling, not the default horse.

---

### Updated agent model assignment

| Agent | Model | Why |
|---|---|---|
| `pptx_analyst` | **gpt-5.3-codex** | Largest context, visual/design multimodal reasoning, state retention across slides |
| `pptx_builder` (content + structure) | **gpt-5.4** | Document creation use case, token efficiency, good generation quality |
| `pptx_builder` (python-pptx code gen) | **gpt-5.3-codex** | Code-first model, async execution, steerability for precise code output |
| Escalation / deep analysis | **gpt-5.4-pro** | Reserve for complex synthesis or when quality must be maximized |

The most practical single-agent approach if you want to keep it simple: **gpt-5.3-codex for analysis, gpt-5.4 for creation** — and wire gpt-5.4-pro as an optional "deep mode" flag.

---

Ready to scaffold the folder? I'd suggest:
```
PPTX-AGENTS/
  pptx_analyst/    → gpt-5.3-codex, multimodal, slide-by-slide analysis
  pptx_builder/    → gpt-5.4 for content, gpt-5.3-codex for code, python-pptx as tool
  shared/          → common utilities (slide renderer, markitdown extractor)
  sample_files/    → test PPTX inputs
```

