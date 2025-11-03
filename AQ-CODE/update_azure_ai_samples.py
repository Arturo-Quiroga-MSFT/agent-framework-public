#!/usr/bin/env python3
"""
Script to add dotenv loading to Azure AI samples
"""
import re
from pathlib import Path

# Files that need updating
files_to_update = [
    "azure_ai_with_code_interpreter.py",
    "azure_ai_with_local_mcp.py",
    "azure_ai_with_file_search.py",
    "azure_ai_with_thread.py",
    "azure_ai_with_openapi_tools.py",
    "azure_ai_with_hosted_mcp.py",
    "azure_ai_with_bing_grounding.py",
]

azure_ai_dir = Path("python/samples/getting_started/agents/azure_ai")

dotenv_imports = """from pathlib import Path

from dotenv import load_dotenv

"""

dotenv_load = """
# Load environment variables from .env file in the agents directory
load_dotenv(Path(__file__).parent.parent / ".env")
"""

prerequisites_note = """
Prerequisites:
- Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME in .env file
- Run 'az login' for Azure CLI authentication"""

for filename in files_to_update:
    filepath = azure_ai_dir / filename
    if not filepath.exists():
        print(f"⚠️  {filename} not found, skipping")
        continue
    
    content = filepath.read_text()
    
    # Check if already has dotenv
    if "from dotenv import load_dotenv" in content:
        print(f"✓ {filename} already has dotenv")
        continue
    
    # Find the import section and docstring
    # Pattern: Copyright -> imports -> """docstring"""
    
    # Insert Path import if not present
    if "from pathlib import Path" not in content:
        # Find first import after copyright
        import_match = re.search(r'(# Copyright.*?\n\n)(import|from)', content, re.DOTALL)
        if import_match:
            content = content[:import_match.end(1)] + dotenv_imports + content[import_match.start(2):]
    else:
        # Just add dotenv import after pathlib
        content = content.replace(
            "from pathlib import Path\n",
            "from pathlib import Path\n\nfrom dotenv import load_dotenv\n"
        )
    
    # Find the location right after imports and before docstring
    # Add the load_dotenv call
    docstring_match = re.search(r'((?:^import.*\n|^from.*\n)+)\n(""")', content, re.MULTILINE)
    if docstring_match:
        content = content[:docstring_match.end(1)] + dotenv_load + "\n" + content[docstring_match.start(2):]
    
    # Add prerequisites to docstring if not present
    if "Prerequisites:" not in content and '"""' in content:
        # Find the docstring and add prerequisites before the closing """
        content = re.sub(
            r'("""[^"]*?)(\n""")',
            r'\1\n' + prerequisites_note + r'\2',
            content,
            count=1
        )
    
    # Write back
    filepath.write_text(content)
    print(f"✓ Updated {filename}")

print("\n✨ All files updated!")
