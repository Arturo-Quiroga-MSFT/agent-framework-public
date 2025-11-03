"""Fan-out / Fan-in example: demonstrates mapping from SK Process Framework to MAF-style workflow.

This example intentionally does not require `agent_framework` to run. If the real
`agent_framework` package is available, the example will prefer it; otherwise a
small local mock is used so the example and tests can run in isolated CI.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import util
import asyncio
from typing import List
from pathlib import Path


@dataclass
class ItemResult:
    source: str
    value: int


def _mock_process_item(value: int, source: str) -> ItemResult:
    return ItemResult(source=source, value=value * 2)


def _mock_workflow(items: List[int]) -> int:
    partials = [_mock_process_item(i, f"child-{idx}") for idx, i in enumerate(items)]
    return sum(p.value for p in partials)


def _load_af_workflow() -> object | None:
    """Dynamically load the Agent Framework workflow sample from the repo.

    Loads `python/samples/semantic-kernel-migration/processes/fan_out_fan_in_process.py`
    and returns the module if successful.
    """
    # Prefer the local AF wrapper module (lighter imports) if available
    try:
        from migration_research.examples.fan_out_fan_in import af_workflow

        return af_workflow
    except Exception:
        pass

    repo_root = Path(__file__).resolve().parents[4]
    target = repo_root / "python" / "samples" / "semantic-kernel-migration" / "processes" / "fan_out_fan_in_process.py"
    if not target.exists():
        return None

    spec = util.spec_from_file_location("fan_out_fan_in_process", str(target))
    if spec is None or spec.loader is None:
        return None
    module = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore
        return module
    except Exception:
        return None


def run(items: List[int]) -> int:
    """Run the fan-out/fan-in workflow using a real Agent Framework sample if available,
    otherwise fall back to local mock behaviour.
    """
    module = _load_af_workflow()
    if module is not None and hasattr(module, "run_agent_framework_workflow_example"):
        # The sample exposes an async function `run_agent_framework_workflow_example`.
        coro = module.run_agent_framework_workflow_example()
        try:
            result = asyncio.get_event_loop().run_until_complete(coro)
        except RuntimeError:
            # No running loop; create a new one
            result = asyncio.run(coro)

        # The AF sample returns a status string like "Completed 3 cycles".
        # We expose an aggregated numeric value to maintain the earlier contract.
        if isinstance(result, str) and "Completed" in result:
            # Extract cycle count
            try:
                n = int(result.split()[-2]) if len(result.split()) >= 2 else 0
                return n
            except Exception:
                return 0
        # If it returns None or unexpected, fall back to mock aggregation
        return _mock_workflow(items)

    # Fallback: mock workflow
    return _mock_workflow(items)


if __name__ == "__main__":
    sample = [1, 2, 3]
    print("Input:", sample)
    print("Aggregated output:", run(sample))
