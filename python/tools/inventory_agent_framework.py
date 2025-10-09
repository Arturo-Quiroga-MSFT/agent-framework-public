#!/usr/bin/env python
"""Inventory all installed agent_framework* Python packages.

Features:
- Discovers distributions whose name starts with 'agent-framework' and modules/packages whose import name starts with 'agent_framework'.
- Imports each module safely (errors captured).
- Extracts public classes & functions (respects __all__ if present, else filters by leading underscore).
- Captures first docstring line and (for functions) signature.
- Outputs Markdown (default) or JSON summary; optionally writes to file.

Usage:
  python inventory_agent_framework.py --format markdown --output agent_framework_inventory.md
  python inventory_agent_framework.py --format json

Exit codes: 0 success, 1 if an unexpected exception bubbles up.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata as md
import inspect
import json
import pkgutil
import sys
import textwrap
from dataclasses import dataclass, asdict
from types import ModuleType
from typing import Any, Dict, List, Optional

# ---------------- Data models -----------------
@dataclass
class FunctionInfo:
    name: str
    signature: str
    doc: str

@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    doc: str

@dataclass
class ModuleReport:
    module: str
    file: Optional[str]
    import_error: Optional[str]
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    all_names: Optional[List[str]]

@dataclass
class DistributionReport:
    dist_name: str
    version: str
    summary: Optional[str]
    modules: List[ModuleReport]

# --------------- Discovery helpers ---------------

def discover_distributions(prefix: str = "agent-framework") -> List[md.Distribution]:
    dists = []
    for dist in md.distributions():  # type: ignore[attr-defined]
        name = dist.metadata.get("Name") or dist.metadata.get("Summary") or ""
        if dist.metadata.get("Name", "").startswith(prefix):
            dists.append(dist)
    return sorted(dists, key=lambda d: d.metadata.get("Name", ""))

def discover_modules(prefix: str = "agent_framework") -> List[str]:
    names = []
    for mod_info in pkgutil.iter_modules():
        if mod_info.name.startswith(prefix):
            names.append(mod_info.name)
    # Walk subpackages of each top-level match
    discovered = set(names)
    for name in list(names):
        try:
            pkg = importlib.import_module(name)
        except Exception:
            continue
        if not hasattr(pkg, "__path__"):
            continue
        for sub in pkgutil.walk_packages(pkg.__path__, prefix=f"{name}."):
            discovered.add(sub.name)
    return sorted(discovered)

# --------------- Introspection helpers ---------------

def is_public(name: str) -> bool:
    return not name.startswith("_")

def safe_signature(obj: Any) -> str:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return "(…)"

def first_line(doc: Optional[str]) -> str:
    if not doc:
        return ""
    return doc.strip().splitlines()[0][:240]

MAX_ITEMS_PER_CATEGORY = 200  # prevent runaway huge dumps

def inspect_module(module_name: str) -> ModuleReport:
    classes: List[ClassInfo] = []
    functions: List[FunctionInfo] = []
    import_error: Optional[str] = None
    all_names: Optional[List[str]] = None
    file: Optional[str] = None
    mod: Optional[ModuleType] = None
    try:
        mod = importlib.import_module(module_name)
        file = getattr(mod, "__file__", None)
        if hasattr(mod, "__all__") and isinstance(mod.__all__, (list, tuple)):
            all_names = list(mod.__all__)
        # Choose candidate names
        if all_names:
            candidates = [n for n in all_names if is_public(n)]
        else:
            candidates = [n for n in dir(mod) if is_public(n)]
        for name in candidates:
            if len(classes) >= MAX_ITEMS_PER_CATEGORY and len(functions) >= MAX_ITEMS_PER_CATEGORY:
                break
            try:
                obj = getattr(mod, name)
            except Exception:
                continue
            if inspect.isclass(obj) and obj.__module__ and obj.__module__.startswith(module_name):
                classes.append(
                    ClassInfo(
                        name=name,
                        bases=[b.__name__ for b in getattr(obj, "__mro__", [])[1:3]],
                        doc=first_line(inspect.getdoc(obj)),
                    )
                )
            elif (inspect.isfunction(obj) or inspect.ismethod(obj)) and getattr(obj, "__module__", "").startswith(module_name):
                functions.append(
                    FunctionInfo(
                        name=name,
                        signature=safe_signature(obj),
                        doc=first_line(inspect.getdoc(obj)),
                    )
                )
    except Exception as e:  # noqa: BLE001
        import_error = f"{type(e).__name__}: {e}".strip()
    return ModuleReport(
        module=module_name,
        file=file,
        import_error=import_error,
        classes=classes,
        functions=functions,
        all_names=all_names,
    )

# --------------- Rendering ---------------

def build_reports() -> Dict[str, Any]:
    dist_reports: List[DistributionReport] = []
    dists = discover_distributions()
    module_names = discover_modules()

    # Map module -> dist (best effort using files location)
    dist_by_location: Dict[str, md.Distribution] = {}
    for dist in dists:
        try:
            files = list(dist.files or [])
        except Exception:
            files = []
        for f in files:
            # crude heuristic: record top-level directory
            parts = str(f).split("/")
            if parts and parts[0].startswith("agent_framework"):
                dist_by_location[parts[0]] = dist

    # Group modules into distributions
    modules_for_dist: Dict[str, List[str]] = {dist.metadata.get("Name", ""): [] for dist in dists}
    unassigned: List[str] = []
    for mod_name in module_names:
        top = mod_name.split(".")[0]
        dist = dist_by_location.get(top)
        if dist:
            modules_for_dist[dist.metadata.get("Name", "")].append(mod_name)
        else:
            unassigned.append(mod_name)

    for dist in dists:
        name = dist.metadata.get("Name", "")
        version = dist.version  # type: ignore[attr-defined]
        summary = dist.metadata.get("Summary")
        reports: List[ModuleReport] = []
        for m in sorted(set(modules_for_dist.get(name, []))):
            reports.append(inspect_module(m))
        dist_reports.append(
            DistributionReport(
                dist_name=name,
                version=version,
                summary=summary,
                modules=reports,
            )
        )

    data = {
        "distributions": [asdict(dr) for dr in dist_reports],
        "unassigned_modules": unassigned,
    }
    return data


def render_markdown(data: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Agent Framework Package Inventory\n")
    lines.append("Generated by inventory_agent_framework.py\n")
    for dist in data["distributions"]:
        lines.append(f"## {dist['dist_name']} ({dist['version']})\n")
        if dist.get("summary"):
            lines.append(f"_Summary:_ {dist['summary']}\n")
        if not dist["modules"]:
            lines.append("(No modules discovered)\n")
            continue
        for mod in dist["modules"]:
            lines.append(f"### Module `{mod['module']}`\n")
            if mod.get("import_error"):
                lines.append(f"Import error: `{mod['import_error']}`\n")
                continue
            if mod.get("file"):
                lines.append(f"File: `{mod['file']}`\n")
            if mod.get("all_names"):
                lines.append(f"__all__ size__: {len(mod['all_names'])}\n")
            # Classes
            if mod["classes"]:
                lines.append("#### Classes\n")
                for cls in mod["classes"][:25]:  # show first 25
                    bases = ", ".join(cls.get("bases") or [])
                    doc = cls.get("doc") or ""
                    lines.append(f"- **{cls['name']}**({bases}) - {doc}")
                if len(mod["classes"]) > 25:
                    lines.append(f"… {len(mod['classes']) - 25} more classes hidden\n")
            # Functions
            if mod["functions"]:
                lines.append("#### Functions\n")
                for fn in mod["functions"][:25]:
                    sig = fn.get("signature")
                    doc = fn.get("doc") or ""
                    lines.append(f"- `{fn['name']}{sig}` - {doc}")
                if len(mod["functions"]) > 25:
                    lines.append(f"… {len(mod['functions']) - 25} more functions hidden\n")
            lines.append("")
    if data.get("unassigned_modules"):
        lines.append("## Unassigned Modules\n")
        for m in data["unassigned_modules"]:
            lines.append(f"- {m}")
    return "\n".join(lines) + "\n"

# --------------- Main ---------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory agent_framework packages")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="Write output to file instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args(argv)

    data = build_reports()
    if args.format == "json":
        text = json.dumps(data, indent=2 if args.pretty else None, sort_keys=True)
    else:
        text = render_markdown(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
