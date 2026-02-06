#!/usr/bin/env python3
"""
Deploy New Agents to Azure AI Foundry

This script deploys 8 diverse V2 agents to your Azure AI project.
These agents cover various use cases: data analysis, research, customer support,
financial analysis, technical documentation, HR assistance, marketing, and project management.

Agents are created via AIProjectClient.agents.create_version() (V2 API)
and show in the NEW Microsoft Foundry portal at ai.azure.com.
Existing agents with the same name are skipped (not duplicated).

USAGE:
    python deploy_new_agents.py

PREREQUISITES:
    - Azure CLI authenticated: az login
    - .env file configured with AZURE_AI_PROJECT_ENDPOINT

UPDATED: February 2026
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment variables
load_dotenv()

# Agent configurations - 8 diverse agents to create
AGENTS_TO_CREATE: List[Dict[str, Any]] = [
    {
        "name": "DataAnalysisAgent",
        "model": "gpt-4.1-mini",
        "instructions": """You are a data analysis expert specializing in statistical analysis and data visualization.
        
Your capabilities include:
- Statistical analysis (mean, median, standard deviation, correlation, regression)
- Data visualization recommendations
- Dataset exploration and insights
- Trend analysis and forecasting
- A/B test analysis

Always explain your methodology clearly and provide actionable insights from the data.
When discussing visualizations, describe what type of chart would best represent the data and why.""",
        "tools": [{"type": "code_interpreter"}],
        "description": "Expert data analyst for statistical analysis, visualization, and insights"
    },
    {
        "name": "ResearchAgent",
        "model": "gpt-4.1",
        "instructions": """You are a research specialist with expertise in gathering, synthesizing, and presenting information.

Your capabilities include:
- Literature review and summarization
- Competitive analysis
- Market research synthesis
- Technical research on emerging technologies
- Citation and source evaluation

Always provide well-structured research summaries with clear sections.
Cite your reasoning and acknowledge limitations in available information.
Present balanced perspectives on complex topics.""",
        "tools": [{"type": "file_search"}],
        "description": "Research specialist for comprehensive information gathering and analysis"
    },
    {
        "name": "CustomerSupportAgent",
        "model": "gpt-4.1-mini",
        "instructions": """You are a friendly and efficient customer support specialist.

Your capabilities include:
- Answering product and service questions
- Troubleshooting common issues
- Guiding users through processes step-by-step
- Escalation recommendations when needed
- Collecting feedback and suggestions

Always maintain a helpful, empathetic tone.
Provide clear, actionable solutions.
If you cannot resolve an issue, explain what information is needed for escalation.
Never make promises about refunds, credits, or policy exceptions without explicit authorization.""",
        "tools": [],
        "description": "Friendly customer support specialist for product questions and troubleshooting"
    },
    {
        "name": "FinancialAnalystAgent",
        "model": "gpt-4.1",
        "instructions": """You are a financial analyst expert specializing in business metrics and financial modeling.

Your capabilities include:
- Financial statement analysis
- KPI calculation and interpretation
- Budget variance analysis
- ROI and NPV calculations
- Cost-benefit analysis
- Financial forecasting

Always show your calculations step by step.
Provide context for financial metrics (industry benchmarks, historical trends).
Highlight risks and assumptions in your analysis.
Present findings in a clear, executive-friendly format when appropriate.""",
        "tools": [{"type": "code_interpreter"}],
        "description": "Financial analyst for metrics, modeling, and business intelligence"
    },
    {
        "name": "TechnicalWriterAgent",
        "model": "gpt-4.1-mini",
        "instructions": """You are a technical documentation specialist focused on creating clear, accurate documentation.

Your capabilities include:
- API documentation
- User guides and tutorials
- README files and quick start guides
- Architecture documentation
- Code comments and docstrings
- Release notes and changelogs

Write in a clear, concise style appropriate for the target audience.
Use consistent formatting and structure.
Include practical examples where helpful.
Follow documentation best practices (progressive disclosure, scannable content).""",
        "tools": [],
        "description": "Technical writer for documentation, guides, and API references"
    },
    {
        "name": "HRAssistantAgent",
        "model": "gpt-4.1-mini",
        "instructions": """You are an HR assistant specializing in employee support and HR processes.

Your capabilities include:
- Policy questions and clarifications
- Benefits information
- Onboarding guidance
- Leave and time-off inquiries
- Performance review process support
- Training and development resources

Always maintain confidentiality and professionalism.
Provide accurate policy information but recommend HR consultation for complex situations.
Be supportive and empathetic when employees have concerns.
Never make commitments on behalf of HR leadership.""",
        "tools": [{"type": "file_search"}],
        "description": "HR assistant for employee support, policies, and benefits questions"
    },
    {
        "name": "MarketingStrategistAgent",
        "model": "gpt-4.1",
        "instructions": """You are a marketing strategist with expertise in digital marketing and brand development.

Your capabilities include:
- Campaign strategy development
- Content marketing planning
- Social media strategy
- SEO and SEM recommendations
- Marketing analytics interpretation
- Brand messaging and positioning

Provide data-driven recommendations when possible.
Consider target audience and buyer personas in your strategies.
Balance creativity with measurable outcomes.
Stay current with marketing trends and best practices.""",
        "tools": [{"type": "code_interpreter"}],
        "description": "Marketing strategist for campaigns, content, and brand development"
    },
    {
        "name": "ProjectManagerAgent",
        "model": "gpt-4.1-mini",
        "instructions": """You are a project management expert skilled in planning, execution, and team coordination.

Your capabilities include:
- Project planning and scheduling
- Risk assessment and mitigation
- Resource allocation recommendations
- Status reporting and dashboards
- Agile and waterfall methodology guidance
- Stakeholder communication templates

Use structured approaches (WBS, RACI, Gantt concepts) in your recommendations.
Focus on actionable next steps and clear ownership.
Identify dependencies and potential blockers proactively.
Adapt your approach based on project size and methodology.""",
        "tools": [],
        "description": "Project manager for planning, tracking, and team coordination"
    },
]


def create_agent(client: AIProjectClient, config: Dict[str, Any]) -> bool:
    """Create a single agent with the given configuration.
    
    Args:
        client: Azure AI Project client
        config: Agent configuration dictionary
        
    Returns:
        True if agent was created successfully, False otherwise
    """
    try:
        # Check if agent already exists
        existing_agents = list(client.agents.list())
        for existing in existing_agents:
            if getattr(existing, 'name', None) == config["name"]:
                print(f"   ⏭️  Agent '{config['name']}' already exists, skipping...")
                return True
        
        # Create the agent using correct V2 API
        agent = client.agents.create_version(
            agent_name=config["name"],
            definition=PromptAgentDefinition(
                model=config["model"],
                instructions=config["instructions"],
                tools=config.get("tools", []),
            ),
            description=config.get("description", ""),
        )
        
        agent_id = getattr(agent, 'id', 'unknown')
        print(f"   ✅ Created '{config['name']}' (ID: {agent_id[:20]}...)")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create '{config['name']}': {e}")
        return False


def deploy_agents():
    """Deploy all agents to Azure AI."""
    print("=" * 70)
    print("🚀 Deploying 8 New Agents to Azure AI Foundry")
    print("=" * 70)
    
    # Check prerequisites
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT not set in .env")
        return False
    
    print(f"\n📍 Target: {endpoint}")
    print(f"📦 Agents to deploy: {len(AGENTS_TO_CREATE)}")
    
    # Initialize client
    try:
        credential = DefaultAzureCredential()
        client = AIProjectClient(endpoint=endpoint, credential=credential)
    except Exception as e:
        print(f"❌ Failed to initialize Azure AI client: {e}")
        return False
    
    # List existing agents
    print("\n📋 Checking existing agents...")
    try:
        existing = list(client.agents.list())
        print(f"   Found {len(existing)} existing agent(s)")
        for agent in existing:
            print(f"   - {getattr(agent, 'name', 'Unknown')} ({getattr(agent, 'model', 'unknown')})")
    except Exception as e:
        print(f"   ⚠️ Could not list existing agents: {e}")
    
    # Deploy new agents
    print("\n" + "-" * 70)
    print("🔧 Creating new agents...")
    print("-" * 70)
    
    success_count = 0
    for i, config in enumerate(AGENTS_TO_CREATE, 1):
        print(f"\n{i}/{len(AGENTS_TO_CREATE)} {config['name']} ({config['model']})")
        if create_agent(client, config):
            success_count += 1
    
    # Final summary
    print("\n" + "=" * 70)
    if success_count == len(AGENTS_TO_CREATE):
        print(f"✅ SUCCESS - All {success_count} agents deployed!")
    else:
        print(f"⚠️ PARTIAL SUCCESS - {success_count}/{len(AGENTS_TO_CREATE)} agents deployed")
    print("=" * 70)
    
    # Show final agent count
    print("\n📊 Final Agent Inventory:")
    try:
        final_agents = list(client.agents.list())
        print(f"   Total agents in project: {len(final_agents)}")
        for agent in final_agents:
            print(f"   - {getattr(agent, 'name', 'Unknown')} ({getattr(agent, 'model', 'unknown')})")
    except Exception as e:
        print(f"   Could not list agents: {e}")
    
    print("\n💡 Next steps:")
    print("   1. Restart the Fleet Health Dashboard to see the new agents")
    print("   2. Run exercise_agents_v2.py to generate telemetry data")
    print("      python exercise_agents_v2.py --list              # list exercisable agents")
    print("      python exercise_agents_v2.py --agents 5          # exercise first 5")
    print("   3. View the dashboard at http://127.0.0.1:8099")
    
    return success_count > 0


def main():
    """Main entry point."""
    success = deploy_agents()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
