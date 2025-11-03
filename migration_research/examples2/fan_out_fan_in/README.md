# Fan-out / Fan-in example

This folder contains a minimal Python example demonstrating how a Semantic Kernel Process (fan-out / fan-in) maps to a Microsoft Agent Framework (MAF) style workflow.

Files:
- `workflow_example.py` - runnable example. If `agent_framework` isn't installed, uses a local mock implementation that mirrors the same input/output contract.
- `test_workflow.py` - pytest smoke test validating the example returns the expected aggregated result.

Run the smoke test (quick, mock-based):

```bash
python -m pip install -r requirements-test.txt   # installs local packages in editable mode + pytest
pytest -q migration-research/examples/fan_out_fan_in/test_workflow.py
```

Run parity tests (attempts to run both SK and AF paths):

```bash
python -m pip install -r requirements-test.txt
# Ensure Semantic Kernel deps are available if you want SK parity checks (optional)
pytest -q migration-research/examples/fan_out_fan_in/test_parity.py
```

Notes:
- The test harness will import and run the AF sample from `python/samples/semantic-kernel-migration/processes/fan_out_fan_in_process.py` when the local packages are installed (editable) and the sample module is importable. If dependencies are missing, the SK parity checks will be skipped.

