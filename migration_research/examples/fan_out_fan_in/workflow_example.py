"""Package copy of the fan-out/fan-in example to allow test imports.

This mirrors the runnable example under `migration-research/examples/...` so that
tests can import it using a valid package path.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ItemResult:
    source: str
    value: int


def real_maf_workflow(items: List[int]) -> int:
    # Simulate fan-out: process each item (as if each item is a child executor)
    partials = [process_item(i, f"child-{idx}") for idx, i in enumerate(items)]
    # Fan-in: aggregate
    total = sum(p.value for p in partials)
    return total


def process_item(value: int, source: str) -> ItemResult:
    # Simulate an executor doing some computation
    return ItemResult(source=source, value=value * 2)


def mock_workflow(items: List[int]) -> int:
    return real_maf_workflow(items)


def run(items: List[int]) -> int:
    try:
        import agent_framework  # type: ignore
        return mock_workflow(items)
    except Exception:
        return mock_workflow(items)


if __name__ == "__main__":
    sample = [1, 2, 3]
    print("Input:", sample)
    print("Aggregated output:", run(sample))
