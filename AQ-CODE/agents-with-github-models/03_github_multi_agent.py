#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Multi-Agent Workflow with GitHub Models

This example demonstrates orchestrating multiple AI agents using MAF workflows
with GitHub Models as the LLM provider.

Demonstrates:
    - Multiple specialized agents
    - Sequential workflow execution
    - Agent-to-agent handoffs
    - State management across agents

Workflow:
    User Query → Research Agent → Analysis Agent → Writer Agent → Final Report

Prerequisites:
    - GITHUB_TOKEN environment variable
    - agent-framework package

Usage:
    python 03_github_multi_agent.py
"""

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

load_dotenv()


async def main():
    """Run a multi-agent workflow using GitHub Models."""
    
    # Configuration
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    model_id = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
    base_url = os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com")
    
    print("=" * 70)
    print("🚀 Multi-Agent Workflow - GitHub Models")
    print("=" * 70)
    print(f"\n🔧 Configuration:")
    print(f"   Model: {model_id}")
    print(f"   Agents: 3 specialized agents")
    print(f"   Workflow: Research → Analysis → Writing")
    print()
    
    # Create shared client
    def create_client():
        return OpenAIChatClient(
            model_id=model_id,
            api_key=github_token,
            base_url=base_url
        )
    
    # ========================================================================
    # AGENT 1: Research Agent
    # ========================================================================
    print("🤖 Creating Research Agent...")
    research_agent = ChatAgent(
        chat_client=create_client(),
        instructions=(
            "You are a research specialist. Your job is to gather key facts "
            "and information on a given topic. Focus on accuracy and "
            "comprehensiveness. Provide your findings in a structured format."
        ),
        name="ResearchAgent"
    )
    
    # ========================================================================
    # AGENT 2: Analysis Agent
    # ========================================================================
    print("🤖 Creating Analysis Agent...")
    analysis_agent = ChatAgent(
        chat_client=create_client(),
        instructions=(
            "You are an analytical expert. You receive research findings and "
            "identify patterns, insights, and implications. Provide clear "
            "analysis with supporting evidence."
        ),
        name="AnalysisAgent"
    )
    
    # ========================================================================
    # AGENT 3: Writer Agent
    # ========================================================================
    print("🤖 Creating Writer Agent...")
    writer_agent = ChatAgent(
        chat_client=create_client(),
        instructions=(
            "You are a professional technical writer. You receive research "
            "and analysis and create clear, well-structured reports. Use "
            "markdown formatting and maintain a professional tone."
        ),
        name="WriterAgent"
    )
    
    print()
    
    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================
    
    # User's initial request
    user_topic = "The benefits and challenges of using AI agents in enterprise software development"
    
    print("=" * 70)
    print("📋 WORKFLOW EXECUTION")
    print("=" * 70)
    print(f"\n🎯 Topic: {user_topic}")
    print()
    
    # ------------------------------------------------------------------------
    # Step 1: Research
    # ------------------------------------------------------------------------
    print("📚 STEP 1: Research Phase")
    print("-" * 70)
    print(f"Agent: {research_agent.name}")
    print(f"Task:  Gather information on the topic")
    print()
    
    research_prompt = (
        f"Research the following topic and provide key findings:\n\n"
        f"{user_topic}\n\n"
        f"Structure your response with clear sections for benefits and challenges."
    )
    
    try:
        research_response = await research_agent.run(research_prompt)
        research_result = str(research_response)  # Convert AgentRunResponse to string
        print(f"✅ Research completed ({len(research_result)} chars)")
        print(f"\nFindings preview:\n{research_result[:300]}...\n")
    except Exception as e:
        print(f"❌ Research failed: {e}")
        return
    
    print("⏳ Waiting 5 seconds before next agent...\n")
    await asyncio.sleep(5)
    
    # ------------------------------------------------------------------------
    # Step 2: Analysis
    # ------------------------------------------------------------------------
    print("📊 STEP 2: Analysis Phase")
    print("-" * 70)
    print(f"Agent: {analysis_agent.name}")
    print(f"Task:  Analyze research findings")
    print()
    
    analysis_prompt = (
        f"Analyze the following research findings and provide insights:\n\n"
        f"{research_result}\n\n"
        f"Identify key patterns, trade-offs, and actionable insights."
    )
    
    try:
        analysis_response = await analysis_agent.run(analysis_prompt)
        analysis_result = str(analysis_response)  # Convert AgentRunResponse to string
        print(f"✅ Analysis completed ({len(analysis_result)} chars)")
        print(f"\nAnalysis preview:\n{analysis_result[:300]}...\n")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return
    
    print("⏳ Waiting 5 seconds before final agent...\n")
    await asyncio.sleep(5)
    
    # ------------------------------------------------------------------------
    # Step 3: Writing
    # ------------------------------------------------------------------------
    print("✍️  STEP 3: Writing Phase")
    print("-" * 70)
    print(f"Agent: {writer_agent.name}")
    print(f"Task:  Create final report")
    print()
    
    writing_prompt = (
        f"Create a professional report combining this research and analysis:\n\n"
        f"RESEARCH:\n{research_result}\n\n"
        f"ANALYSIS:\n{analysis_result}\n\n"
        f"Format as a markdown document with title, sections, and conclusion."
    )
    
    try:
        report_response = await writer_agent.run(writing_prompt)
        final_report = str(report_response)  # Convert AgentRunResponse to string
        print(f"✅ Report completed ({len(final_report)} chars)\n")
    except Exception as e:
        print(f"❌ Writing failed: {e}")
        return
    
    # ------------------------------------------------------------------------
    # Display Final Result
    # ------------------------------------------------------------------------
    print("=" * 70)
    print("📄 FINAL REPORT")
    print("=" * 70)
    print()
    print(final_report)
    print()
    print("=" * 70)
    
    # Summary
    print("\n✅ Multi-Agent Workflow Completed!")
    print()
    print("📊 Workflow Summary:")
    print(f"   • Research output: {len(research_result)} characters")
    print(f"   • Analysis output: {len(analysis_result)} characters")
    print(f"   • Final report:    {len(final_report)} characters")
    print(f"   • Total agents:    3 specialized agents")
    print()
    print("💡 Key Concepts Demonstrated:")
    print("   ✓ Multiple specialized agents")
    print("   ✓ Sequential workflow execution")
    print("   ✓ Context passing between agents")
    print("   ✓ Collaborative problem-solving")
    print()
    print("📚 Next Steps:")
    print("   - Try parallel agent execution")
    print("   - Add conditional routing between agents")
    print("   - Implement feedback loops")
    print("   - See notebooks/github_models_walkthrough.ipynb")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
