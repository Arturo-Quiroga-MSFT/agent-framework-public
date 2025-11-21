"""
Azure AI Search Agent for Indexed Content
"""

from agent_framework import ChatAgent, HostedFileSearchTool
from agent_framework._clients import ChatClientProtocol
from agent_framework_ag_ui import AgentFrameworkAgent


def create_azure_ai_search_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create Azure AI Search agent for searching indexed hotel data."""
    
    # Create Azure AI Search tool
    azure_ai_search_tool = HostedFileSearchTool(
        additional_properties={
            "index_name": "hotels-sample-index",
            "query_type": "simple",
            "top_k": 10,
        },
    )
    
    base_agent = ChatAgent(
        name="azure_ai_search_agent",
        instructions="""You are a helpful travel assistant with access to a hotel database.

Your capabilities:
- Search through indexed hotel information
- Find hotels by location, amenities, price range, and ratings
- Provide detailed hotel information including address, features, and contact details
- Compare hotels and make recommendations

Best practices:
1. Use the search tool to find relevant hotels for the user's query
2. Present hotel information in a clear, organized manner
3. Include key details: name, location, rating, price, amenities
4. For multiple hotels, summarize and compare key features
5. Make recommendations based on user preferences

Search index: hotels-sample-index

Remember previous searches and questions for context in follow-up queries.
""",
        chat_client=chat_client,
        tools=azure_ai_search_tool,
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="AzureAISearchAgent",
        description="Hotel search agent with Azure AI Search integration",
        state_schema={
            "search_history": {
                "type": "array",
                "items": {"type": "string"},
                "description": "History of hotel searches",
            }
        },
        require_confirmation=False,
    )
