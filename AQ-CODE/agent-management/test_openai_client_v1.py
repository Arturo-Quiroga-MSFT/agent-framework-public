#!/usr/bin/env python3
"""
Attempt to access V1 classic agents using OpenAI client.
"""

import os
import sys
from pathlib import Path

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

# Load environment
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

endpoint = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
if not endpoint:
    print("Error: AZURE_AI_PROJECT_ENDPOINT not set")
    sys.exit(1)

print(f"🔄 Connecting to: {endpoint}\n")
credential = DefaultAzureCredential()
client = AIProjectClient(endpoint=endpoint, credential=credential)

print("="*80)
print("ATTEMPTING TO ACCESS V1 CLASSIC AGENTS VIA OPENAI CLIENT")
print("="*80)

try:
    print("\n📦 Method 1: Get OpenAI Client and list assistants...")
    openai_client = client.get_openai_client()
    print(f"✅ Got OpenAI client: {type(openai_client)}")
    
    # Try to list assistants (V1 classic agents)
    print("\n🔍 Listing assistants via openai_client.beta.assistants.list()...")
    assistants = list(openai_client.beta.assistants.list())
    
    if assistants:
        print(f"✅ SUCCESS! Found {len(assistants)} V1 classic assistants!")
        print("\nFirst 10 assistants:")
        print("-"*80)
        for idx, asst in enumerate(assistants[:10], 1):
            print(f"{idx}. {asst.name or 'Unnamed'}")
            print(f"   ID: {asst.id}")
            print(f"   Model: {asst.model}")
            if hasattr(asst, 'created_at'):
                from datetime import datetime
                dt = datetime.fromtimestamp(asst.created_at)
                print(f"   Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        if len(assistants) > 10:
            print(f"... and {len(assistants) - 10} more assistants")
        
        print("\n" + "="*80)
        print(f"TOTAL FOUND: {len(assistants)} V1 classic agents")
        print("="*80)
    else:
        print("⚠️  No assistants found")
        
except AttributeError as e:
    print(f"❌ AttributeError: {e}")
    print("\nThe OpenAI client might not have beta.assistants API")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    print("\nThis approach might not be supported")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("If V1 agents were found above, we can create management scripts!")
print("If not, V1 agents may require REST API access or Portal-only management.")
