"""
Example 04: Parallel Agent Execution with GitHub Models

This example demonstrates how to run multiple agents in parallel using asyncio.gather(),
which can significantly reduce total execution time compared to sequential execution (example 03).

Use Case: Analyze a topic from multiple perspectives simultaneously
- Technical Analyst: Evaluates technical feasibility
- Business Analyst: Assesses market and business viability  
- Risk Analyst: Identifies potential risks and challenges
- Creative Consultant: Proposes innovative approaches

Comparison:
- Sequential (03): Agent1 → Agent2 → Agent3 → ~45-60 seconds
- Parallel (04): Agent1 + Agent2 + Agent3 → ~15-20 seconds

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
"""

import asyncio
import os
import time
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please set it first.")


def create_github_client(model_id: str = GITHUB_MODEL) -> OpenAIChatClient:
    """
    Creates an OpenAI-compatible client configured for GitHub Models.
    
    Args:
        model_id: The GitHub model to use (default: gpt-4o-mini)
    
    Returns:
        OpenAIChatClient configured for GitHub Models API
    """
    return OpenAIChatClient(
        model_id=model_id,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )


async def create_specialized_agent(
    role: str,
    expertise: str,
    focus_areas: str,
    client: OpenAIChatClient
) -> ChatAgent:
    """
    Creates a specialized agent with specific expertise.
    
    Args:
        role: The agent's role title
        expertise: Description of the agent's expertise
        focus_areas: Specific areas the agent should focus on
        client: The OpenAIChatClient to use
    
    Returns:
        ChatAgent configured with specialized instructions
    """
    instructions = f"""You are a {role} with deep expertise in {expertise}.

Your role is to analyze topics from your unique perspective and provide insights on:
{focus_areas}

Guidelines:
1. Be concise but thorough (200-300 words)
2. Use bullet points for clarity
3. Focus on actionable insights
4. Highlight critical considerations
5. Provide specific recommendations

Format your response with clear sections."""

    return ChatAgent(
        chat_client=client,
        instructions=instructions,
        name=role.replace(" ", "_").lower(),
    )


async def analyze_with_agent(
    agent: ChatAgent,
    topic: str,
    agent_name: str
) -> tuple[str, str, float]:
    """
    Runs a single agent's analysis and measures execution time.
    
    Args:
        agent: The ChatAgent to run
        topic: The topic to analyze
        agent_name: Display name for the agent
    
    Returns:
        Tuple of (agent_name, analysis_result, execution_time)
    """
    print(f"🔄 Starting {agent_name}...")
    start_time = time.time()
    
    try:
        prompt = f"Analyze the following topic from your perspective:\n\n{topic}"
        response = await agent.run(prompt)
        result = str(response)  # Convert AgentRunResponse to string
        
        execution_time = time.time() - start_time
        print(f"✅ {agent_name} completed in {execution_time:.1f}s ({len(result)} chars)")
        
        return (agent_name, result, execution_time)
    
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error in {agent_name}: {str(e)}"
        print(f"❌ {agent_name} failed in {execution_time:.1f}s")
        return (agent_name, error_msg, execution_time)


async def run_parallel_analysis(topic: str):
    """
    Executes parallel agent analysis and displays results.
    
    This demonstrates the key benefit of parallel execution: multiple agents
    can work simultaneously, reducing total time compared to sequential execution.
    
    Args:
        topic: The topic to analyze from multiple perspectives
    """
    print("\n" + "="*80)
    print("🚀 PARALLEL MULTI-AGENT ANALYSIS")
    print("="*80)
    print(f"\n📋 Topic: {topic}\n")
    
    # Create shared client
    client = create_github_client()
    
    # Create specialized agents
    print("🔧 Creating specialized agents...\n")
    
    technical_agent = await create_specialized_agent(
        role="Technical Analyst",
        expertise="software architecture, scalability, and technical implementation",
        focus_areas="""- Technical feasibility and architecture
- Technology stack recommendations
- Scalability and performance considerations
- Technical risks and mitigation strategies
- Implementation timeline and complexity""",
        client=client
    )
    
    business_agent = await create_specialized_agent(
        role="Business Analyst",
        expertise="market analysis, business models, and competitive strategy",
        focus_areas="""- Market opportunity and target audience
- Business model and revenue potential
- Competitive landscape and differentiation
- Go-to-market strategy
- Financial projections and ROI""",
        client=client
    )
    
    risk_agent = await create_specialized_agent(
        role="Risk Analyst",
        expertise="risk assessment, compliance, and operational security",
        focus_areas="""- Operational risks and challenges
- Regulatory and compliance requirements
- Security and privacy concerns
- Mitigation strategies and contingency plans
- Long-term sustainability considerations""",
        client=client
    )
    
    creative_agent = await create_specialized_agent(
        role="Creative Consultant",
        expertise="innovation, user experience, and creative problem-solving",
        focus_areas="""- Innovative approaches and unique angles
- User experience and engagement strategies
- Creative differentiation opportunities
- Emerging trends and future possibilities
- Unconventional solutions and blue-sky thinking""",
        client=client
    )
    
    print("✅ All agents created\n")
    
    # Run agents in parallel using asyncio.gather()
    print("🏃 Running parallel analysis...\n")
    overall_start = time.time()
    
    # Execute all agents concurrently
    results = await asyncio.gather(
        analyze_with_agent(technical_agent, topic, "Technical Analyst"),
        analyze_with_agent(business_agent, topic, "Business Analyst"),
        analyze_with_agent(risk_agent, topic, "Risk Analyst"),
        analyze_with_agent(creative_agent, topic, "Creative Consultant"),
        return_exceptions=True  # Don't fail if one agent fails
    )
    
    overall_time = time.time() - overall_start
    
    print(f"\n{'='*80}")
    print(f"⏱️  TOTAL EXECUTION TIME: {overall_time:.1f} seconds")
    print(f"{'='*80}\n")
    
    # Display results
    print("📊 ANALYSIS RESULTS")
    print("="*80 + "\n")
    
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Agent failed with exception: {result}\n")
            continue
            
        agent_name, analysis, exec_time = result
        
        print(f"\n{'─'*80}")
        print(f"👤 {agent_name.upper()} (completed in {exec_time:.1f}s)")
        print(f"{'─'*80}\n")
        print(analysis)
        print()
    
    # Performance summary
    print("\n" + "="*80)
    print("📈 PERFORMANCE SUMMARY")
    print("="*80)
    
    successful_results = [r for r in results if not isinstance(r, Exception)]
    individual_times = [r[2] for r in successful_results]
    
    print(f"\n✅ Successful analyses: {len(successful_results)}/4")
    print(f"⏱️  Total parallel time: {overall_time:.1f}s")
    print(f"⏱️  Longest individual agent: {max(individual_times):.1f}s")
    print(f"⏱️  Sequential time would be: ~{sum(individual_times):.1f}s")
    print(f"🚀 Speedup: ~{sum(individual_times) / overall_time:.1f}x faster")
    
    print("\n💡 Note: Actual speedup depends on:")
    print("   - GitHub Models rate limits (15 requests/min)")
    print("   - Network latency and model response time")
    print("   - System resources and concurrent request handling")
    print()


async def main():
    """
    Main function demonstrating parallel agent execution.
    """
    print("\n" + "="*80)
    print("GitHub Models + Microsoft Agent Framework - Parallel Agents Demo")
    print("="*80)
    
    # Example 1: Analyze a product idea
    topic1 = """
    Product Idea: AI-Powered Personal Learning Assistant
    
    An AI application that creates personalized learning paths, adapts to 
    individual learning styles, tracks progress, and provides interactive 
    practice exercises. It would integrate with existing educational content 
    and use spaced repetition for optimal retention.
    """
    
    await run_parallel_analysis(topic1)
    
    # Optional: Add a second example
    run_second_example = input("\n🤔 Would you like to analyze another topic? (y/n): ").strip().lower()
    
    if run_second_example == 'y':
        print("\n💡 Tip: Try different topics to see how agents adapt their analysis")
        print("Examples:")
        print("  - New business ventures")
        print("  - Technology implementations")
        print("  - Strategic initiatives")
        print("  - Product features\n")
        
        custom_topic = input("Enter your topic: ").strip()
        
        if custom_topic:
            await run_parallel_analysis(custom_topic)
    
    print("\n" + "="*80)
    print("✅ Parallel agent demo completed!")
    print("="*80)
    print("\n💡 Key Takeaways:")
    print("   1. Parallel execution significantly reduces total time")
    print("   2. Use asyncio.gather() for concurrent agent execution")
    print("   3. Handle exceptions gracefully with return_exceptions=True")
    print("   4. Monitor rate limits when running multiple agents")
    print("   5. Each agent maintains its specialized perspective")
    print("\n🔍 Compare with 03_github_multi_agent.py to see the difference!")
    print("   - Sequential: Agents wait for each other (slower, but dependent)")
    print("   - Parallel: Agents run simultaneously (faster, but independent)")
    print()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
