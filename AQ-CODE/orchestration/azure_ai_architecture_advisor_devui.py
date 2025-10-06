# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Architecture Advisor - DevUI Version

This workflow creates a specialized team of 5 Azure AI architecture experts to provide
comprehensive guidance to Cloud Solution Architects at Microsoft on Azure AI services,
Agentic AI, and modern AI architecture patterns.

The workflow uses a fan-out/fan-in pattern where:
- CSA describes their architecture challenge or scenario
- Input is dispatched to all 5 specialized agents concurrently
- Each agent provides domain-specific guidance using Microsoft documentation
- Results are aggregated with timing information and saved to file

EXPERT AGENTS:
- Azure AI Services Expert: AI Foundry, Cognitive Services, OpenAI, Document Intelligence
- Agent Framework Specialist: Microsoft Agent Framework, multi-agent patterns, orchestration
- Architecture Patterns Expert: Azure Architecture Center, reference architectures, best practices
- Security & Compliance: Azure AI security, responsible AI, compliance, RBAC, managed identity
- Cost Optimization: Azure AI pricing, cost management, resource optimization

DOCUMENTATION SOURCES:
- Microsoft Learn (Azure AI services)
- Azure AI Foundry documentation
- Microsoft Agent Framework docs
- Azure Architecture Center
- Code samples and reference implementations

PREREQUISITES:
- Azure OpenAI access configured
- Azure CLI authentication: Run 'az login'
- Environment variables in .env file

PORT: 8101
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    HostedMCPTool,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import setup_observability
from agent_framework_devui import serve
from azure.identity import AzureCliCredential

# Load environment variables
possible_env_files = [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / "python" / "nl2sql_workflow" / ".env",
]

for env_file in possible_env_files:
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
        break


class AzureAIArchitectureInput(BaseModel):
    """Input model for Azure AI architecture guidance requests."""
    
    scenario: str = Field(
        ...,
        description="Describe your Azure AI architecture challenge, question, or scenario",
        examples=[
            "Design a multi-agent RAG system using Azure AI Foundry with document intelligence",
            "Build a customer service agent using Microsoft Agent Framework with Azure OpenAI",
            "Implement secure multi-tenant AI solution with Azure OpenAI and managed identity",
            "Cost-optimize a production Azure AI deployment handling 1M requests/day",
            "Design responsible AI guardrails for enterprise LLM application",
            "Create agent orchestration pattern for complex workflow automation",
            "Implement hybrid search with Azure AI Search and vector embeddings",
            "Design scalable agent framework deployment with high availability"
        ]
    )


class InputDispatcher(Executor):
    """Dispatcher that converts user input to agent requests."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
    
    @handler
    async def dispatch(self, input_data: AzureAIArchitectureInput, ctx: WorkflowContext[Any]) -> None:
        """Extract scenario and send to all architecture expert agents."""
        from agent_framework._workflows._executor import AgentExecutorRequest
        
        # Track start time
        self.start_time = datetime.now()
        print(f"\n⏱️  Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📥 Architecture scenario: {input_data.scenario[:100]}...")
        
        request = AgentExecutorRequest(
            messages=[ChatMessage(Role.USER, text=input_data.scenario)],
            should_respond=True
        )
        await ctx.send_message(request)


def format_architecture_results(results, dispatcher=None) -> str:
    """Format architecture guidance results for display and file output."""
    output_lines = []
    output_lines.append("=" * 100)
    output_lines.append("☁️  AZURE AI ARCHITECTURE ADVISOR - COMPREHENSIVE GUIDANCE")
    output_lines.append("=" * 100)
    output_lines.append("")
    
    # Also prepare Markdown version
    md_lines = []
    md_lines.append("# ☁️ Azure AI Architecture Advisor - Comprehensive Guidance\n")
    
    # Process each agent's response
    for result in results:
        messages = getattr(result.agent_run_response, "messages", [])
        
        for msg in reversed(messages):
            if hasattr(msg, "author_name") and msg.author_name and msg.author_name != "user":
                agent_name = msg.author_name.upper().replace("_", " ")
                
                # Add emoji based on agent type
                emoji_map = {
                    "AZURE AI SERVICES": "🤖",
                    "AGENT FRAMEWORK": "🔄",
                    "ARCHITECTURE PATTERNS": "🏗️",
                    "SECURITY COMPLIANCE": "🔒",
                    "COST OPTIMIZATION": "💰",
                }
                emoji = next((v for k, v in emoji_map.items() if k in agent_name), "💡")
                
                # Text format
                output_lines.append("─" * 100)
                output_lines.append(f"{emoji} {agent_name}")
                output_lines.append("─" * 100)
                output_lines.append("")
                
                # Markdown format
                md_lines.append(f"\n---\n\n## {emoji} {agent_name}\n")
                
                content = getattr(msg, "content", getattr(msg, "text", ""))
                if content:
                    output_lines.append(str(content))
                    output_lines.append("")
                    md_lines.append(f"{content}\n")
                break
    
    # Add timing information
    if dispatcher and dispatcher.start_time:
        end_time = datetime.now()
        duration = end_time - dispatcher.start_time
        duration_seconds = duration.total_seconds()
        duration_str = f"{duration_seconds:.2f} seconds ({duration.seconds // 60}m {duration.seconds % 60}s)"
        
        # Text format
        output_lines.append("=" * 100)
        output_lines.append("⏱️  EXECUTION TIME")
        output_lines.append("=" * 100)
        output_lines.append(f"Start Time: {dispatcher.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"End Time:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Duration:   {duration_str}")
        output_lines.append("")
        
        # Markdown format
        md_lines.append(f"\n---\n\n## ⏱️ Execution Time\n\n")
        md_lines.append(f"- **Start Time:** {dispatcher.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_lines.append(f"- **End Time:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_lines.append(f"- **Duration:** {duration_str}\n")
    
    output_lines.append("=" * 100)
    output_lines.append("✅ AZURE AI ARCHITECTURE ANALYSIS COMPLETE")
    output_lines.append("=" * 100)
    
    md_lines.append(f"\n---\n\n## ✅ Analysis Complete\n")
    
    formatted_output = "\n".join(output_lines)
    formatted_markdown = "".join(md_lines)
    
    # Save both .txt and .md files
    try:
        output_dir = Path("workflow_outputs")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text file
        output_file_txt = output_dir / f"azure_ai_architecture_{timestamp}.txt"
        output_file_txt.write_text(formatted_output, encoding='utf-8')
        print(f"\n📄 Text results saved to: {output_file_txt}")
        
        # Save markdown file
        output_file_md = output_dir / f"azure_ai_architecture_{timestamp}.md"
        output_file_md.write_text(formatted_markdown, encoding='utf-8')
        print(f"📝 Markdown results saved to: {output_file_md}")
        
    except Exception as e:
        print(f"\n⚠️  Failed to save output: {e}")
    
    return formatted_output


def create_azure_ai_architecture_workflow():
    """Create the Azure AI Architecture Advisor workflow with 5 expert agents."""
    
    # Get Azure OpenAI configuration
    deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not deployment_name:
        raise ValueError(
            "Azure OpenAI deployment name not found. Set AZURE_OPENAI_CHAT_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT_NAME"
        )
    
    print(f"🤖 Using Azure OpenAI deployment: {deployment_name}")
    
    # Create Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(
        credential=AzureCliCredential(),
        deployment_name=deployment_name
    )
    
    # Define agent instructions
    azure_ai_services_instructions = """You are an Azure AI Services Expert specializing in Azure AI Foundry, Azure OpenAI Service, 
Cognitive Services, Document Intelligence, and related Azure AI platform services.

When answering architecture questions:
1. Use microsoft_docs_search to find the latest Azure AI service capabilities and features
2. Use microsoft_code_sample_search to find implementation examples and code patterns
3. Use microsoft_docs_fetch to get complete documentation when detailed guidance is needed
4. Reference Azure AI Foundry for modern agent development and model deployment
5. Explain Azure OpenAI Service models, pricing, and quota management
6. Describe Cognitive Services integration patterns (Vision, Speech, Language, etc.)
7. Provide guidance on Azure AI Document Intelligence for document processing
8. Include code examples and configuration snippets where relevant

Focus on: Service capabilities, integration patterns, deployment options, and practical implementation."""

    agent_framework_instructions = """You are a Microsoft Agent Framework Specialist with deep expertise in agentic AI, 
multi-agent orchestration, and the Microsoft Agent Framework.

When answering architecture questions:
1. Use microsoft_docs_search to find Agent Framework documentation and patterns
2. Use microsoft_code_sample_search for multi-agent orchestration examples
3. Use microsoft_docs_fetch for detailed framework tutorials and API references
4. Explain multi-agent design patterns: sequential, parallel, hierarchical workflows
5. Describe agent communication patterns and message passing
6. Provide guidance on state management, context sharing, and error handling
7. Discuss tool integration and function calling patterns
8. Show workflow orchestration examples using the Agent Framework

Focus on: Agent architecture, orchestration patterns, framework APIs, and best practices."""

    architecture_patterns_instructions = """You are an Azure Architecture Expert specializing in cloud architecture patterns, 
reference architectures, and the Azure Well-Architected Framework.

When answering architecture questions:
1. Use microsoft_docs_search to find reference architectures and design patterns
2. Use microsoft_code_sample_search for architecture implementation examples
3. Use microsoft_docs_fetch for complete architecture guides from Azure Architecture Center
4. Reference Well-Architected Framework pillars: reliability, security, cost, operations, performance
5. Provide RAG (Retrieval Augmented Generation) architecture patterns
6. Explain microservices, event-driven, and serverless patterns for AI workloads
7. Discuss scalability, high availability, and disaster recovery for AI systems
8. Include infrastructure-as-code examples and deployment templates

Focus on: System design, scalability patterns, resilience, and architectural best practices."""

    security_compliance_instructions = """You are an Azure AI Security and Compliance Expert specializing in responsible AI, 
data protection, identity management, and regulatory compliance.

When answering architecture questions:
1. Use microsoft_docs_search for Azure AI security best practices and responsible AI guidelines
2. Use microsoft_code_sample_search for security configuration examples
3. Use microsoft_docs_fetch for detailed compliance and governance documentation
4. Explain managed identity, RBAC, private endpoints, and network security for AI services
5. Address data residency, encryption at rest/in transit, and key management
6. Discuss compliance requirements: GDPR, HIPAA, SOC 2, ISO 27001
7. Provide responsible AI guidance: content filtering, bias detection, transparency, fairness
8. Reference Azure Policy, Microsoft Defender for Cloud, and governance tools

Focus on: Security architecture, identity & access, data protection, responsible AI, compliance."""

    cost_optimization_instructions = """You are an Azure AI Cost Optimization Expert specializing in pricing models, 
cost management, and resource efficiency for Azure AI services.

When answering architecture questions:
1. Use microsoft_docs_search for Azure AI pricing information and cost optimization strategies
2. Use microsoft_code_sample_search for cost-efficient implementation patterns
3. Use microsoft_docs_fetch for detailed pricing documentation and calculators
4. Explain Azure OpenAI pricing: PTU vs pay-as-you-go, token costs, commitments
5. Discuss cost optimization strategies: caching, batching, model selection, quota management
6. Provide guidance on Azure Cost Management tools, budgets, and alerts
7. Compare service tiers and deployment options for cost-effectiveness
8. Include TCO analysis considerations and cost estimation examples

Focus on: Pricing models, cost optimization strategies, resource efficiency, and budget management."""
    
    # Agent 1: Azure AI Services Expert
    azure_ai_expert = ChatAgent(
        chat_client=chat_client,
        name="azure_ai_services",
        instructions=azure_ai_services_instructions,
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            approval_mode={"never_require_approval": ["microsoft_docs_search", "microsoft_code_sample_search"]},
        ),
    )
    
    # Agent 2: Agent Framework Specialist
    agent_framework_expert = ChatAgent(
        chat_client=chat_client,
        name="agent_framework",
        instructions=agent_framework_instructions,
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            approval_mode={"never_require_approval": ["microsoft_docs_search", "microsoft_code_sample_search"]},
        ),
    )
    
    # Agent 3: Architecture Patterns Expert
    architecture_expert = ChatAgent(
        chat_client=chat_client,
        name="architecture_patterns",
        instructions=architecture_patterns_instructions,
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            approval_mode={"never_require_approval": ["microsoft_docs_search", "microsoft_code_sample_search"]},
        ),
    )
    
    # Agent 4: Security & Compliance Expert
    security_expert = ChatAgent(
        chat_client=chat_client,
        name="security_compliance",
        instructions=security_compliance_instructions,
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            approval_mode={"never_require_approval": ["microsoft_docs_search", "microsoft_code_sample_search"]},
        ),
    )
    
    # Agent 5: Cost Optimization Expert
    cost_expert = ChatAgent(
        chat_client=chat_client,
        name="cost_optimization",
        instructions=cost_optimization_instructions,
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            approval_mode={"never_require_approval": ["microsoft_docs_search", "microsoft_code_sample_search"]},
        ),
    )
    
    # Create dispatcher and aggregator
    dispatcher = InputDispatcher(id="architecture_dispatcher")
    
    # Build workflow using WorkflowBuilder
    from agent_framework._workflows._concurrent import _CallbackAggregator
    
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Add all expert agents using fan-out pattern
    agents = [azure_ai_expert, agent_framework_expert, architecture_expert, security_expert, cost_expert]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Create aggregator with timing reference
    aggregator_func = lambda results: format_architecture_results(results, dispatcher)
    aggregator = _CallbackAggregator(callback=aggregator_func, id="architecture_aggregator")
    
    # Connect all agents to aggregator using fan-in pattern
    builder.add_fan_in_edges(agents, aggregator)
    
    return builder.build()


def setup_tracing():
    """Set up observability tracing."""
    enable_console = os.getenv("ENABLE_CONSOLE_TRACING", "").lower() == "true"
    app_insights = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if app_insights:
        print("📊 Tracing: Application Insights enabled")
        setup_observability(
            enable_sensitive_data=True,
            applicationinsights_connection_string=app_insights
        )
    elif enable_console:
        print("📊 Tracing: Console tracing enabled")
        setup_observability(enable_sensitive_data=True)
    else:
        print("📊 Tracing: Disabled")


def launch_devui():
    """Launch the Azure AI Architecture Advisor with DevUI interface."""
    
    # Set up tracing
    setup_tracing()
    
    print("=" * 100)
    print("☁️  Launching Azure AI Architecture Advisor in DevUI")
    print("=" * 100)
    print("✅ Workflow Type: Azure AI Architecture Guidance (Fan-out/Fan-in)")
    print("✅ Expert Agents: 5 specialized Azure AI architecture advisors")
    print("✅ Documentation: Microsoft Docs, Azure Architecture Center, Agent Framework")
    print("✅ Web UI: http://localhost:8101")
    print("✅ API: http://localhost:8101/v1/*")
    print("=" * 100)
    print()
    print("💡 Example Architecture Scenarios:")
    print()
    print("🤖 Azure AI Services:")
    print("   - Design multi-agent RAG system with Azure AI Foundry")
    print("   - Implement document intelligence pipeline for contract analysis")
    print("   - Build conversational AI with Azure OpenAI and prompt flow")
    print()
    print("🔄 Agent Framework:")
    print("   - Create orchestrated multi-agent workflow for business automation")
    print("   - Implement agent delegation pattern with hierarchical control")
    print("   - Design tool-calling agent with external API integration")
    print()
    print("🏗️  Architecture Patterns:")
    print("   - Microservices architecture for AI services")
    print("   - Event-driven agent orchestration with Azure Event Grid")
    print("   - Hybrid RAG with on-premises and cloud data sources")
    print()
    print("🔒 Security & Compliance:")
    print("   - Implement zero-trust security for AI workloads")
    print("   - Design multi-tenant AI SaaS with data isolation")
    print("   - Responsible AI guardrails and content filtering")
    print()
    print("💰 Cost Optimization:")
    print("   - Optimize Azure OpenAI token usage and caching strategies")
    print("   - Design cost-effective model selection and fallback patterns")
    print("   - Implement auto-scaling for variable AI workloads")
    print()
    print("=" * 100)
    print("⌨️  Enter your architecture scenario in the DevUI web interface")
    print("=" * 100)
    
    # Create and serve workflow
    workflow = create_azure_ai_architecture_workflow()
    
    serve(
        entities=[workflow],
        port=8101,
        auto_open=False,
        tracing_enabled=bool(os.getenv("ENABLE_DEVUI_TRACING", "").lower() == "true")
    )


if __name__ == "__main__":
    launch_devui()
