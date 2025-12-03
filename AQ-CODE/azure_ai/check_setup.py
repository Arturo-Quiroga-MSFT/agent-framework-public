#!/usr/bin/env python3
"""
Quick Setup Script for Azure AI V2 Examples
Checks environment and provides setup guidance
"""

import os
import sys
from pathlib import Path

def check_env_var(var_name: str, required: bool = False) -> tuple[bool, str]:
    """Check if environment variable is set."""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if 'KEY' in var_name or 'SECRET' in var_name:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            return True, f"✅ {var_name}: {masked}"
        return True, f"✅ {var_name}: {value[:50]}..."
    else:
        status = "❌" if required else "⚠️ "
        message = "REQUIRED" if required else "Optional"
        return False, f"{status} {var_name}: Not set ({message})"

def main():
    print("=" * 80)
    print("Azure AI V2 Examples - Environment Setup Check")
    print("=" * 80)
    print()
    
    # Load .env file if exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"✅ Found .env file at: {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print(f"⚠️  No .env file found at: {env_file}")
        print(f"   Copy .env.example to .env and configure it")
    
    print()
    print("=" * 80)
    print("Required Configuration")
    print("=" * 80)
    
    required_vars = [
        ("AZURE_AI_PROJECT_ENDPOINT", True),
        ("AZURE_AI_MODEL_DEPLOYMENT_NAME", False),
    ]
    
    all_required_set = True
    for var_name, required in required_vars:
        is_set, message = check_env_var(var_name, required)
        print(message)
        if required and not is_set:
            all_required_set = False
    
    print()
    print("=" * 80)
    print("Optional Configuration (for enhanced features)")
    print("=" * 80)
    
    optional_vars = [
        "OPENWEATHER_API_KEY",
        "NEWS_API_KEY",
        "BING_CONNECTION_ID",
        "FILE_SEARCH_VECTOR_STORE_ID",
    ]
    
    for var_name in optional_vars:
        is_set, message = check_env_var(var_name, required=False)
        print(message)
    
    print()
    print("=" * 80)
    print("Authentication")
    print("=" * 80)
    
    # Check if Azure CLI is logged in
    import subprocess
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Azure CLI authentication: Logged in")
            # Try to parse subscription
            import json
            try:
                account = json.loads(result.stdout)
                sub_name = account.get('name', 'Unknown')
                print(f"   Subscription: {sub_name}")
            except:
                pass
        else:
            print("❌ Azure CLI authentication: Not logged in")
            print("   Run: az login")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Azure CLI: Not found or not responding")
        print("   Install: https://docs.microsoft.com/cli/azure/install-azure-cli")
    
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    if all_required_set:
        print("✅ All required variables are set!")
        print()
        print("Ready to run:")
        print("  python azure_ai_with_function_tools_v2.py")
        print("  python azure_ai_with_multiple_tools_v2.py")
    else:
        print("❌ Missing required configuration!")
        print()
        print("Setup steps:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and set AZURE_AI_PROJECT_ENDPOINT")
        print("3. Run 'az login' for authentication")
        print("4. Optionally add API keys for weather and news")
    
    print()
    print("=" * 80)
    print("API Key Resources (Optional)")
    print("=" * 80)
    print("OpenWeatherMap: https://openweathermap.org/api (free tier)")
    print("NewsAPI: https://newsapi.org/register (free tier)")
    print("=" * 80)

if __name__ == "__main__":
    main()
