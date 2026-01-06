#!/usr/bin/env python3
"""
Validation script for Jason's Travel Agent Demo setup
Run this before executing the notebook to verify configuration
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if .env file exists and has required variables"""
    print("🔍 Checking environment configuration...\n")
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print(f"   Expected location: {env_file}")
        print("\n📝 Action: Copy .env.template to .env and fill in your values")
        return False
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # Check required variables
    required_vars = {
        "PROJECT_ENDPOINT": "Azure AI Foundry project endpoint",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "Model deployment name"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith("your-"):
            print(f"❌ {var}: Not configured")
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:50]}...")
    
    if missing_vars:
        print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
        print("\n📝 Action: Edit .env file and set these values")
        return False
    
    print("\n✅ All environment variables configured!")
    return True


def check_azure_auth():
    """Check if Azure authentication is working"""
    print("\n🔐 Checking Azure authentication...\n")
    
    try:
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        
        # Try to get a token (this validates az login)
        token = credential.get_token("https://management.azure.com/.default")
        print("✅ Azure authentication successful!")
        print(f"   Token expires: {token.expires_on}")
        return True
    except Exception as e:
        print(f"❌ Azure authentication failed: {e}")
        print("\n📝 Action: Run 'az login' to authenticate")
        return False


def check_packages():
    """Check if required packages are installed"""
    print("\n📦 Checking required packages...\n")
    
    required_packages = [
        "agent_framework",
        "azure.ai.projects",
        "azure.identity",
        "dotenv",
        "pydantic",
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_").replace(".", "/").split("/")[0])
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}: Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("\n📝 Action: Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("\n✅ All required packages installed!")
    return True


def check_foundry_connection():
    """Try to connect to Azure AI Foundry project"""
    print("\n🌐 Testing Azure AI Foundry connection...\n")
    
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        from dotenv import load_dotenv
        
        load_dotenv()
        
        project_endpoint = os.getenv("PROJECT_ENDPOINT")
        
        print(f"   Connecting to: {project_endpoint}")
        
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential()
        )
        
        # Try to get default connection
        connection = project_client.connections.get_default(connection_type="AzureOpenAI")
        print(f"✅ Connected to Foundry project!")
        print(f"   Connection: {connection.name}")
        return True
    except Exception as e:
        print(f"❌ Foundry connection failed: {e}")
        print("\n📝 Action: Verify PROJECT_ENDPOINT is correct")
        print("   Get it from: https://ai.azure.com → Your Project → Settings")
        return False


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("   Jason's Travel Agent Demo - Setup Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Environment Variables", check_environment),
        ("Azure Authentication", check_azure_auth),
        ("Python Packages", check_packages),
        ("Foundry Connection", check_foundry_connection),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("   VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run the notebook.")
        print("\n📓 Next step: Open 14-handoffjdv.ipynb and run all cells")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n📝 Common fixes:")
        print("   1. Run: az login")
        print("   2. Copy .env.template to .env and fill in values")
        print("   3. Install packages: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
