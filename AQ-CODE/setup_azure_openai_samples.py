#!/usr/bin/env python3
"""
Script to automatically configure Azure AI sample files for local development.

This script sets up Azure AI samples with:
1. Environment variable loading from .env files
2. Real weather API integration (replaces fake functions with OpenWeatherMap)
3. Required imports (httpx, os, dotenv)

Features:
- Idempotent: Safe to run multiple times
- Smart detection: Only modifies files that need updates
- Comprehensive: Handles both dotenv setup and weather API replacement

Usage:
    python setup_azure_ai_samples.py
    
    Or make it executable and run:
    chmod +x setup_azure_ai_samples.py
    ./setup_azure_ai_samples.py
"""

import re
from pathlib import Path


def has_dotenv_import(content: str) -> bool:
    """Check if the file already has dotenv import."""
    return "from dotenv import load_dotenv" in content or "import dotenv" in content


def has_dotenv_load(content: str) -> bool:
    """Check if the file already loads dotenv."""
    return "load_dotenv" in content and ".env" in content


def has_real_weather_function(content: str) -> bool:
    """Check if the file has the real weather function (uses OpenWeatherMap API)."""
    return "def get_weather" in content and "openweathermap.org" in content


def has_fake_weather_function(content: str) -> bool:
    """Check if the file has the fake weather function (uses random data)."""
    return "def get_weather" in content and "randint" in content and "conditions = [" in content


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
                    new_lines.append('# Load environment variables from getting_started/.env')
                    new_lines.append('env_path = Path(__file__).parent.parent.parent / ".env"')
                    new_lines.append('load_dotenv(dotenv_path=env_path)')
                    
                    dotenv_added = True
    
    if not dotenv_added:
        print(f"  ✗ Could not find appropriate location to add dotenv, skipping")
        return False
    
    # Write the modified content back
    file_path.write_text('\n'.join(new_lines))
    print(f"  ✓ Added dotenv loading")
    return True


def replace_fake_weather_function(file_path: Path) -> bool:
    """
    Replace fake weather function with real OpenWeatherMap API implementation.
    
    Returns True if file was modified, False otherwise.
    """
    print(f"  Checking weather function in: {file_path.name}")
    
    # Read the file
    content = file_path.read_text()
    
    # Check if already has real weather function
    if has_real_weather_function(content):
        print(f"    ✓ Already has real weather function, skipping")
        return False
    
    # Check if it has fake weather function
    if not has_fake_weather_function(content):
        print(f"    ℹ No weather function found, skipping")
        return False
    
    # Define the real weather function implementation
    real_weather_function = '''def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return f"Error: OPENWEATHER_API_KEY not found in environment variables."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        return f"The weather in {location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"Error: {str(e)}"'''
    
    # Pattern to match the fake weather function (more robust regex)
    fake_weather_pattern = r'def get_weather\([^)]+\)\s*->\s*str:\s*"""[^"]*"""\s*conditions\s*=\s*\[[^\]]+\]\s*return\s+f"[^"]*\{[^}]*randint[^"]*"'
    
    # Try to find and replace the fake function
    new_content = re.sub(fake_weather_pattern, real_weather_function, content, flags=re.DOTALL)
    
    if new_content == content:
        # Pattern didn't match, try a simpler approach by finding the function definition
        lines = content.split('\n')
        new_lines = []
        i = 0
        replaced = False
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is the start of the fake weather function
            if 'def get_weather(' in line and not replaced:
                # Found the function, now find where it ends
                function_start = i
                function_end = i + 1
                indent_level = len(line) - len(line.lstrip())
                
                # First, skip past the function signature (which might span multiple lines until we find the colon)
                signature_complete = ':' in line
                while function_end < len(lines) and not signature_complete:
                    if ':' in lines[function_end]:
                        signature_complete = True
                    function_end += 1
                
                # Now find the actual end of the function body
                while function_end < len(lines):
                    next_line = lines[function_end]
                    
                    # If we hit another function/class at the same or lower indent, stop
                    if next_line.strip():
                        if (next_line.strip().startswith('def ') or 
                            next_line.strip().startswith('async def ') or
                            next_line.strip().startswith('class ')):
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= indent_level:
                                break
                    
                    function_end += 1
                    
                    # Safety: don't go more than 20 lines
                    if function_end - function_start > 20:
                        break
                
                # Check if this is the fake weather function
                function_body = '\n'.join(lines[function_start:function_end])
                if 'randint' in function_body and 'conditions = [' in function_body:
                    # Replace with real function
                    new_lines.append(real_weather_function)
                    replaced = True
                    i = function_end
                    print(f"    ✓ Replaced fake weather function with real API implementation")
                    continue
            
            new_lines.append(line)
            i += 1
        
        if not replaced:
            print(f"    ✗ Could not find or replace fake weather function")
            return False
        
        new_content = '\n'.join(new_lines)
    else:
        print(f"    ✓ Replaced fake weather function with real API implementation")
    
    # Ensure httpx and os are imported
    if 'import httpx' not in new_content or 'import os' not in new_content:
        lines = new_content.split('\n')
        new_lines = []
        imports_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add imports right after 'import asyncio' line
            if not imports_added and 'import asyncio' in line:
                if 'import os' not in new_content:
                    new_lines.append('import os')
                if 'import httpx' not in new_content:
                    new_lines.append('import httpx')
                imports_added = True
        
        new_content = '\n'.join(new_lines)
    
    # Write the modified content back
    file_path.write_text(new_content)
    print(f"    ✓ Updated imports (httpx, os)")
    return True


def main():
    """Main function to process all Python files in the azure_openai samples directory."""
    # Get the script directory and navigate to the samples directory
    script_dir = Path(__file__).parent
    samples_dir = script_dir.parent / "python" / "samples" / "getting_started" / "agents" / "azure_openai"
    
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
    
    dotenv_modified = 0
    dotenv_skipped = 0
    weather_modified = 0
    weather_skipped = 0
    
    for py_file in sorted(python_files):
        # Add dotenv loading
        if add_dotenv_to_file(py_file):
            dotenv_modified += 1
        else:
            dotenv_skipped += 1
        
        # Replace weather function
        if replace_fake_weather_function(py_file):
            weather_modified += 1
        else:
            weather_skipped += 1
        
        print()
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  Dotenv:")
    print(f"    Modified: {dotenv_modified} file(s)")
    print(f"    Skipped:  {dotenv_skipped} file(s)")
    print(f"  Weather Function:")
    print(f"    Modified: {weather_modified} file(s)")
    print(f"    Skipped:  {weather_skipped} file(s)")
    print(f"  Total files processed: {len(python_files)}")


if __name__ == "__main__":
    main()
