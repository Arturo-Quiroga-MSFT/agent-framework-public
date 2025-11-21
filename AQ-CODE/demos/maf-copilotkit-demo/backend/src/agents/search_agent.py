"""
Bing Search Agent with Web Grounding
"""

from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework._clients import ChatClientProtocol
from agent_framework_ag_ui import AgentFrameworkAgent


def create_bing_search_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create Bing search agent with web grounding capability."""
    
    bing_search_tool = HostedWebSearchTool(
        name="Bing Grounding Search",
        description="Search the web for current information using Bing",
    )
    
    base_agent = ChatAgent(
        name="bing_search_agent",
        instructions="""You are a helpful web search assistant with access to Bing search.

Your capabilities:
- Search the web for current, real-time information
- Find breaking news, recent events, and up-to-date facts
- Answer questions that require current information
- Provide well-sourced, accurate answers with citations

Best practices:
1. Use Bing search when questions require current information
2. Always cite your sources with URLs when available
3. Distinguish between factual information and opinions
4. For controversial topics, present multiple perspectives
5. Indicate the recency of information (e.g., "As of [date]...")

Remember previous searches in the conversation for context and follow-up questions.
""",
        chat_client=chat_client,
        tools=bing_search_tool,
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="BingSearchAgent",
        description="Web search agent with Bing grounding for current information",
        state_schema={
            "search_history": {
                "type": "array",
                "items": {"type": "string"},
                "description": "History of search queries",
            }
        },
        require_confirmation=False,
    )
