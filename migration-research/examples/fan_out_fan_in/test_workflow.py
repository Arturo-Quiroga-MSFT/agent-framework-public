import sys
from pathlib import Path

# Ensure repo root is on sys.path so the migration_research package is importable
# file path is: <repo>/migration-research/examples/fan_out_fan_in/test_workflow.py
# repo root is parents[3]
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root))

from migration_research.examples.fan_out_fan_in.workflow_example import run


def test_fan_out_fan_in_simple():
    # items: [1,2,3] -> each processed as value*2 -> [2,4,6] -> aggregated sum = 12
    items = [1, 2, 3]
    result = run(items)
    assert result == 12
