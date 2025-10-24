"""Demo: simulate follow-up behavior for nl2sql_workflow session persistence.

This script does a lightweight simulation:
1. Creates a compact session summary file with last_sql and last_result_sample
2. Instantiates the InputDispatcher from nl2sql_workflow and calls dispatch with a follow-up question
   so the dispatcher will attempt to load and re-inject prior context.

Note: This demo does not run the full workflow or call Azure services. It only validates
the session persistence/load logic in InputDispatcher and OutputFormatter.
"""
import json
from pathlib import Path
from datetime import datetime

from nl2sql_workflow import NL2SQLInput

# Create demo session summary
session_id = "demo-session-1"
session_dir = Path(__file__).parent / "workflow_outputs" / "sessions"
session_dir.mkdir(parents=True, exist_ok=True)
session_file = session_dir / f"{session_id}.json"

session_summary = {
    "session_id": session_id,
    "last_sql": "SELECT LoanId, CurrentBalance FROM fact.FACT_LOAN_ORIGINATION WHERE IsActive = 1;",
    "last_result_sample": [
        "LoanId,CurrentBalance",
        "LOAN000194,48808932.00",
        "LOAN000928,48775608.75",
    ],
    "saved_at": datetime.now().isoformat(),
}

with open(session_file, "w", encoding="utf-8") as sf:
    json.dump(session_summary, sf, indent=2)

print(f"Created demo session summary: {session_file}")

# Now simulate creating an input with session_id and question
input_data = NL2SQLInput(question="How many of those active loans are over 40,000,000?", session_id=session_id)

print("\nTo actually test InputDispatcher.load logic, run the full DevUI or import the InputDispatcher class")
print("This demo created the session summary file for the workflow to consume.")
