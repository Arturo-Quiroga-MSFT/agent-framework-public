#!/usr/bin/env python3
"""
Deploy New Agents to Azure AI Foundry

This script deploys the DataAnalysisAgent and ResearchAgent to your Azure AI project.
Run this before using exercise_agents_v2.py to generate telemetry for these agents.

USAGE:
    python deploy_new_agents.py

PREREQUISITES:
    - Azure CLI authenticated: az login
    - .env file configured with AZURE_AI_PROJECT_ENDPOINT
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()


async def deploy_agents():
    """Deploy the new agents to Azure AI."""
    print("=" * 70)
    print("🚀 Deploying New Agents to Azure AI Foundry")
    print("=" * 70)
    
    # Check prerequisites
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT not set in .env")
        return False
    
    print(f"\n📍 Target: {endpoint[:50]}...")
    
    try:
        # Import the agents (this will create them)
        print("\n1️⃣ Deploying DataAnalysisAgent...")
        from agents.data_analysis_agent import agent as data_agent
        print(f"   ✅ DataAnalysisAgent created: {data_agent.name if hasattr(data_agent, 'name') else 'DataAnalysisAgent'}")
        
        print("\n2️⃣ Deploying ResearchAgent...")
        from agents.research_agent import agent as research_agent
        print(f"   ✅ ResearchAgent created: {research_agent.name if hasattr(research_agent, 'name') else 'ResearchAgent'}")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS - Both agents deployed!")
        print("=" * 70)
        print("\n📊 You can now run the exercise script to generate telemetry:")
        print("   python exercise_agents_v2.py")
        print("\n💡 The Fleet Health Dashboard will show these agents once they have runs.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error deploying agents: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    success = asyncio.run(deploy_agents())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
