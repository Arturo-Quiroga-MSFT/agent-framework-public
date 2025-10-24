#!/usr/bin/env python3
"""
Script to automatically add dotenv loading to Azure AI sample files.

This script updates Python files in the azure_ai samples directory to load
environment variables from the AQ-CODE/.env file.

Usage:
    python add_dotenv_to_samples.py
    
    Or make it executable and run:
    chmod +x add_dotenv_to_samples.py
    ./add_dotenv_to_samples.py
"""

import re
from pathlib import Path


def has_dotenv_import(content: str) -> bool:
    """Check if the file already has dotenv import."""
    return "from dotenv import load_dotenv" in content or "import dotenv" in content


def has_dotenv_load(content: str) -> bool:
    """Check if the file already loads dotenv."""
    return "load_dotenv" in content and ".env" in content


def add_dotenv_to_file(file_path: Path) -> bool:
    """
    Add dotenv loading to a Python file if not already present.
    
    Returns True if file was modified, False otherwise.
    """
    print(f"Processing: {file_path.name}")
    
    # Read the file
    content = file_path.read_text()
    
    # Check if already has dotenv loading
    if has_dotenv_import(content) and has_dotenv_load(content):
        print(f"  ✓ Already has dotenv loading, skipping")
        return False
    
    # Split content into lines
    lines = content.split('\n')
    
    # Find the copyright comment and the first import
    copyright_end = 0
    first_import = -1
    
    for i, line in enumerate(lines):
        if line.startswith('# Copyright'):
            # Find where copyright block ends
            for j in range(i, len(lines)):
                if lines[j].strip() and not lines[j].startswith('#'):
                    copyright_end = j
                    break
        
        if line.startswith('import ') or line.startswith('from '):
            if first_import == -1:
                first_import = i
    
    if first_import == -1:
        print(f"  ✗ No imports found, skipping")
        return False
    
    # Check if Path is already imported
    has_path_import = False
    path_import_line = -1
    
    for i, line in enumerate(lines):
        if 'from pathlib import' in line:
            has_path_import = True
            path_import_line = i
            break
    
    # Build the new content
    new_lines = []
    dotenv_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add imports after the last import in the first import block
        if not dotenv_added and i >= first_import:
            # Check if this is the last import before a blank line or docstring
            next_line_idx = i + 1
            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                # If next line is blank or starts with docstring, insert here
                if not next_line or next_line.startswith('"""') or next_line.startswith("'''"):
                    # Add Path import if not present
                    if not has_path_import and 'from pathlib import' not in line:
                        new_lines.append('from pathlib import Path')
                    
                    # Add dotenv import
                    if not has_dotenv_import(content):
                        new_lines.append('from dotenv import load_dotenv')
                    
                    # Add blank line
                    new_lines.append('')
                    
                    # Add the dotenv loading code
                    new_lines.append('# Load environment variables from AQ-CODE/.env')
                    new_lines.append('env_path = Path(__file__).parent.parent.parent.parent.parent / "AQ-CODE" / ".env"')
                    new_lines.append('load_dotenv(dotenv_path=env_path)')
                    
                    dotenv_added = True
    
    if not dotenv_added:
        print(f"  ✗ Could not find appropriate location to add dotenv, skipping")
        return False
    
    # Write the modified content back
    file_path.write_text('\n'.join(new_lines))
    print(f"  ✓ Added dotenv loading")
    return True


def main():
    """Main function to process all Python files in the azure_ai samples directory."""
    # Get the script directory and navigate to the samples directory
    script_dir = Path(__file__).parent
    samples_dir = script_dir.parent / "python" / "samples" / "getting_started" / "agents" / "azure_ai"
    
    if not samples_dir.exists():
        print(f"Error: Samples directory not found: {samples_dir}")
        return
    
    print(f"Processing Python files in: {samples_dir}")
    print("=" * 60)
    
    # Get all Python files (excluding __init__.py)
    python_files = [f for f in samples_dir.glob("*.py") if f.name != "__init__.py"]
    
    if not python_files:
        print("No Python files found to process")
        return
    
    modified_count = 0
    skipped_count = 0
    
    for py_file in sorted(python_files):
        if add_dotenv_to_file(py_file):
            modified_count += 1
        else:
            skipped_count += 1
        print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  Modified: {modified_count} file(s)")
    print(f"  Skipped:  {skipped_count} file(s)")
    print(f"  Total:    {len(python_files)} file(s)")


if __name__ == "__main__":
    main()
