#!/usr/bin/env python3
"""
Example 09: Group Chat Workflow with DevUI Visualization (Collaborative Discussion)

This example demonstrates the GROUP CHAT orchestration pattern using MAF's GroupChatBuilder.
Unlike sequential (07) or parallel (08) patterns, this showcases multi-agent CONVERSATION
where agents collaborate iteratively, managed by an orchestrator that selects speakers.

Key Differences from Examples 07 & 08:
- Agents have a CONVERSATION (not just sequential/parallel execution)
- Manager/Orchestrator dynamically selects who speaks next
- Iterative refinement through multiple discussion rounds
- Agents build on each other's contributions conversationally
- Perfect for collaborative problem-solving and decision-making

Group Chat Visualization:
┌──────────────────────────────────────────────────────────────┐
│  User Question → Product Manager (initial proposal)          │
│                   ↓                                           │
│  [Orchestrator decides] → Technical Architect (feasibility)  │
│                   ↓                                           │
│  [Orchestrator decides] → UX Designer (user experience)      │
│                   ↓                                           │
│  [Orchestrator decides] → Business Analyst (ROI analysis)    │
│                   ↓                                           │
│  [Orchestrator decides] → Final synthesis or more rounds     │
└──────────────────────────────────────────────────────────────┘

Orchestrator controls conversation flow based on context!

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
3. Install DevUI: pip install agent-framework-devui --pre

Usage:
    python 09_github_groupchat_workflow.py
    
    Opens DevUI at http://localhost:8084 with group chat visualization!

Example Features:
- "AI-powered personalized learning platform for corporate training"
- "Blockchain-based supply chain transparency system"
- "Telemedicine platform with AI diagnostics"
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agent_framework import (
    ChatAgent,
    ChatMessage,
    GroupChatBuilder,
    GroupChatStateSnapshot,
    WorkflowAgent,
)
from agent_framework.openai import OpenAIChatClient

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please set it first.")


class FeatureReviewInput(BaseModel):
    """Input model for product feature review group chat."""

    feature_idea: str = Field(
        ...,
        description="Describe the product feature or idea you want the team to review collaboratively",
        examples=[
            "AI-powered personalized learning platform that adapts to each employee's skill level and learning pace",
            "Blockchain-based supply chain transparency system for ethical sourcing verification",
            "Mental health app with AI therapy chatbot and anonymous peer support groups",
            "Telemedicine platform with AI-assisted diagnostics and virtual specialist consultations",
            "Smart city traffic management using IoT sensors and predictive ML algorithms",
            "Voice-activated smart home system with privacy-first local processing",
            "Carbon footprint tracking app with gamification and marketplace for offsets",
            "Collaborative design tool with real-time AI suggestions and version control",
        ],
    )


def select_next_speaker(state: GroupChatStateSnapshot) -> str | None:
    """Intelligent speaker selector for multi-round product feature review discussions.

    Creates a dynamic multi-round conversation:
    
    Round 1-4: Initial perspectives (each agent speaks once)
      1. Product Manager proposes the feature
      2. Technical Architect evaluates feasibility
      3. UX Designer assesses user experience
      4. Business Analyst reviews market viability
    
    Round 5-8: Iterative refinement (agents respond to each other)
      5. Product Manager addresses technical/UX concerns
      6. Technical Architect proposes solutions to concerns
      7. UX Designer refines design based on feedback
      8. Business Analyst provides final recommendation

    Args:
        state: Current group chat state with conversation history

    Returns:
        Name of next speaker, or None to finish
    """
    round_idx = state["round_index"]
    history = state["history"]
    
    # Define speaker rotation for multi-round discussion
    speakers = ["ProductManager", "TechnicalArchitect", "UXDesigner", "BusinessAnalyst"]
    
    # Maximum 8 rounds (2 full cycles for iterative refinement)
    if round_idx >= 8:
        return None
    
    # Get last speaker from history
    last_speaker = None
    if history:
        for entry in reversed(history):
            if hasattr(entry, 'speaker') and entry.speaker in speakers:
                last_speaker = entry.speaker
                break
    
    # Round 1-4: Initial discussion (each agent once)
    if round_idx < 4:
        if last_speaker is None:
            return speakers[0]  # Start with PM
        elif last_speaker in speakers:
            current_idx = speakers.index(last_speaker)
            next_idx = current_idx + 1
            if next_idx < len(speakers):
                return speakers[next_idx]
    
    # Round 5-8: Refinement cycle (agents respond to feedback)
    elif round_idx < 8:
        if last_speaker in speakers:
            current_idx = speakers.index(last_speaker)
            next_idx = current_idx + 1
            if next_idx < len(speakers):
                return speakers[next_idx]
            else:
                # After BA speaks, return to PM for next round
                return speakers[0]
    
    return None


def format_conversation_summary(history, feature_idea: str) -> str:
    """Format the group chat conversation into a readable summary.
    
    Args:
        history: Conversation history from the group chat
        feature_idea: The original feature idea
    
    Returns:
        Formatted markdown summary
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = f"""# Product Feature Review - Group Chat Summary

**Generated:** {timestamp}
**Feature Idea:** {feature_idea}

---

## Discussion Summary

"""
    
    # Group messages by speaker
    speakers_contributions = {}
    for entry in history:
        if hasattr(entry, 'speaker') and hasattr(entry, 'content'):
            speaker = entry.speaker
            if speaker not in speakers_contributions:
                speakers_contributions[speaker] = []
            speakers_contributions[speaker].append(entry.content)
    
    # Format each speaker's contributions
    speaker_titles = {
        "ProductManager": "💡 Product Manager",
        "TechnicalArchitect": "🔧 Technical Architect",
        "UXDesigner": "🎨 UX Designer",
        "BusinessAnalyst": "📊 Business Analyst"
    }
    
    for speaker in ["ProductManager", "TechnicalArchitect", "UXDesigner", "BusinessAnalyst"]:
        if speaker in speakers_contributions:
            summary += f"\n### {speaker_titles.get(speaker, speaker)}\n\n"
            for i, contribution in enumerate(speakers_contributions[speaker], 1):
                if len(speakers_contributions[speaker]) > 1:
                    summary += f"**Round {i}:**\n{contribution}\n\n"
                else:
                    summary += f"{contribution}\n\n"
    
    summary += "\n---\n\n## Conversation Flow\n\n"
    for i, entry in enumerate(history, 1):
        if hasattr(entry, 'speaker') and hasattr(entry, 'content'):
            speaker_emoji = {
                "ProductManager": "💡",
                "TechnicalArchitect": "🔧",
                "UXDesigner": "🎨",
                "BusinessAnalyst": "📊"
            }.get(entry.speaker, "💬")
            summary += f"{i}. {speaker_emoji} **{entry.speaker}**: {entry.content[:150]}...\n"
    
    return summary


def save_conversation_output(history, feature_idea: str) -> str:
    """Save the group chat conversation to a file.
    
    Args:
        history: Conversation history from the group chat
        feature_idea: The original feature idea
    
    Returns:
        Path to the saved file
    """
    # Create output directory
    output_dir = Path("workflow_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groupchat_feature_review_{timestamp}.md"
    filepath = output_dir / filename
    
    # Format and save
    summary = format_conversation_summary(history, feature_idea)
    filepath.write_text(summary)
    
    return str(filepath)


async def create_groupchat_workflow():
    """Create the group chat workflow with 4 specialist agents."""

    # Create OpenAI-compatible chat client
    client = OpenAIChatClient(
        model_id=GITHUB_MODEL,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )

    # Create 4 specialized product team agents
    product_manager = ChatAgent(
        name="ProductManager",
        description="Product strategy expert who champions user needs and business goals",
        instructions="""You are a product manager reviewing feature proposals. 
        
Your role:
- Articulate the user value proposition clearly
- Identify target user segments
- Outline key features and success metrics
- Consider competitive landscape
- Be enthusiastic but realistic
- IN SECOND ROUND: Respond to technical/UX concerns raised and refine proposal

Keep your analysis to 3-4 key points. You're speaking to technical and business colleagues.""",
        chat_client=client,
    )

    technical_architect = ChatAgent(
        name="TechnicalArchitect",
        description="Technical feasibility expert who evaluates implementation complexity",
        instructions="""You are a technical architect assessing feature feasibility.

Your role:
- Evaluate technical implementation challenges
- Identify required technologies and integrations
- Estimate development complexity and timeline
- Flag potential scalability or security concerns
- Suggest technical approaches
- IN SECOND ROUND: Propose solutions to concerns and address UX feedback

Keep your analysis to 3-4 key points. Be honest about challenges but solution-oriented.""",
        chat_client=client,
    )

    ux_designer = ChatAgent(
        name="UXDesigner",
        description="User experience expert who champions intuitive and accessible design",
        instructions="""You are a UX designer evaluating user experience implications.

Your role:
- Assess usability and accessibility considerations
- Identify potential user friction points
- Suggest interaction patterns and design principles
- Consider inclusive design for diverse users
- Balance functionality with simplicity
- IN SECOND ROUND: Refine design based on technical and business feedback

Keep your analysis to 3-4 key points. Focus on the user journey and experience.""",
        chat_client=client,
    )

    business_analyst = ChatAgent(
        name="BusinessAnalyst",
        description="Business viability expert who evaluates market fit and ROI",
        instructions="""You are a business analyst assessing market viability and ROI.

Your role:
- Evaluate market opportunity and target market size
- Assess competitive positioning and differentiation
- Estimate revenue potential and business model
- Identify go-to-market considerations
- Synthesize team input into recommendation
- IN SECOND ROUND: Provide final go/no-go recommendation with action items

Keep your analysis to 3-4 key points. Provide a clear recommendation (go/no-go/iterate).""",
        chat_client=client,
    )

    # Build group chat workflow with orchestrator
    workflow = (
        GroupChatBuilder()
        .set_select_speakers_func(
            select_next_speaker,
            display_name="Orchestrator"
        )
        .participants([
            product_manager,
            technical_architect,
            ux_designer,
            business_analyst,
        ])
        .build()
    )

    return workflow


def main():
    """Launch the group chat workflow in DevUI with visual representation."""
    from agent_framework.devui import serve

    # Create output directory
    output_dir = Path("workflow_outputs")
    output_dir.mkdir(exist_ok=True)

    print("\n" + "="*80)
    print("💬 Group Chat Workflow - Collaborative Product Feature Review")
    print("="*80)
    print("\n📋 Team Structure:")
    print("   Product Manager → Technical Architect → UX Designer → Business Analyst")
    print("   (Orchestrator manages conversation flow)")
    print("\n🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("🎨 Feature: GroupChatBuilder with conversational orchestration")
    print("\n🌐 Starting DevUI server...")

    # Create the workflow
    workflow = asyncio.run(create_groupchat_workflow())

    print("\n✅ Group chat workflow created")
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8084")
    print("📡 API:     http://localhost:8084/v1/*")
    print("🔍 Entity:  workflow")
    print("📊 Feature: Group chat conversation visualization")

    print("\n" + "="*80)
    print("💡 How Group Chat Works")
    print("="*80)
    print("\n1. Open http://localhost:8084 in your browser")
    print("2. Select 'workflow' from dropdown")
    print("3. You'll see the group chat participants")
    print("4. Enter your feature idea")
    print("5. Watch the orchestrated conversation:")
    print("   • Product Manager: Proposes feature vision (~15s)")
    print("   • Technical Architect: Evaluates feasibility (~15s)")
    print("   • UX Designer: Reviews user experience (~15s)")
    print("   • Business Analyst: Assesses viability & recommends (~15s)")
    print("6. Total time: ~60s for complete 4-person discussion")

    print("\n" + "="*80)
    print("📝 Example Feature Ideas")
    print("="*80)
    print("\n🤖 AI/Tech Products:")
    print("   • AI-powered code review assistant with learning capabilities")
    print("   • Real-time language translation earbuds for travelers")
    print("   • Smart home energy optimizer with AI demand prediction")

    print("\n🏥 Healthcare:")
    print("   • Telemedicine platform with AI symptom triage")
    print("   • Mental health chatbot with crisis detection")
    print("   • Wearable health monitor with predictive analytics")

    print("\n🌱 Sustainability:")
    print("   • Blockchain carbon credit marketplace")
    print("   • Food waste tracking and donation platform")
    print("   • Electric vehicle charging network optimizer")

    print("\n" + "="*80)
    print("✨ Group Chat vs Sequential/Parallel")
    print("="*80)
    print("\n🎨 Key Differences:")
    print("   • Sequential (07): A→B→C (linear pipeline)")
    print("   • Parallel (08): All agents simultaneously")
    print("   • Group Chat (09): Orchestrated CONVERSATION")
    print("\n💡 Group Chat Advantages:")
    print("   • Agents reference each other's contributions")
    print("   • Orchestrator adapts flow based on discussion")
    print("   • Natural for collaborative decision-making")
    print("   • Mimics real team discussions")
    print("   • Iterative refinement possible")

    print("\n" + "="*80)
    print("📊 Architecture Comparison")
    print("="*80)
    print("\nExample 07 (Sequential):")
    print("   Input → [A] → [B] → [C] → Output")
    print("   • Fixed pipeline")
    print("   • Each agent waits for previous")

    print("\nExample 08 (Parallel):")
    print("   Input → [A,B,C,D simultaneously] → Aggregate → Output")
    print("   • All execute at once")
    print("   • Independent analyses")

    print("\nExample 09 (Group Chat):")
    print("   Input → [Orchestrator selects] → [Agent responds]")
    print("           ↓")
    print("         [Orchestrator selects] → [Next agent responds]")
    print("           ↓")
    print("         [Continues until done]")
    print("   • Dynamic conversation flow")
    print("   • Agents build on each other")
    print("   • Manager controls discussion")

    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")

    # Launch DevUI server with tracing enabled
    serve(
        entities=[workflow],
        port=8084,
        auto_open=True,
        tracing_enabled=True,  # Enable OpenTelemetry tracing
    )


if __name__ == "__main__":
    main()
