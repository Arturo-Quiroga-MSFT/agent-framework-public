"""
MCP Agents - Firecrawl and Hosted MCP
"""

import os

from agent_framework import ChatAgent, HostedMCPTool
from agent_framework._clients import ChatClientProtocol
from agent_framework_ag_ui import AgentFrameworkAgent


def create_firecrawl_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create Firecrawl MCP agent for web scraping and content extraction."""
    
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
    
    # Firecrawl hosted MCP server format
    firecrawl_url = f"https://mcp.firecrawl.dev/{api_key}/v2/mcp"
    firecrawl_tool = HostedMCPTool(
        name="Firecrawl Web Scraper",
        url=firecrawl_url,
    )
    
    base_agent = ChatAgent(
        name="firecrawl-agent",
        instructions="""You are a helpful web research assistant with advanced web scraping capabilities.

Your capabilities:
- Scrape and extract clean content from any website
- Handle JavaScript-heavy sites and dynamic content
- Extract structured data from web pages
- Bypass bot detection and access protected content
- Convert web pages to clean, readable markdown

Best practices:
1. When given a URL, use Firecrawl to extract the content
2. Summarize the key information from the scraped content
3. Highlight important sections, data points, or quotes
4. For news articles, extract headline, date, author, and main points
5. For documentation, extract code examples and key concepts

Tool: Firecrawl MCP (hosted)

Remember previous scraping requests for context.
""",
        chat_client=chat_client,
        tools=firecrawl_tool,
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="FirecrawlAgent",
        description="Web scraping agent with Firecrawl MCP integration",
        state_schema={
            "scraped_urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "History of scraped URLs",
            }
        },
        require_confirmation=False,
    )


def create_hosted_mcp_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create hosted MCP agent for Microsoft Learn documentation access."""
    
    # Microsoft Learn MCP server
    mcp_tool = HostedMCPTool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
    )
    
    base_agent = ChatAgent(
        name="hosted-mcp-agent",
        instructions="""You are a helpful assistant with access to Microsoft Learn documentation.

Your capabilities:
- Search Microsoft's official documentation
- Find information about Azure services, Microsoft products, and developer tools
- Access up-to-date technical documentation
- Retrieve code examples and best practices
- Explain Microsoft technologies and concepts

Best practices:
1. Use the MCP tool to search Microsoft Learn documentation
2. Provide accurate information from official sources
3. Include code examples when relevant
4. Link to specific documentation pages when available
5. Explain technical concepts in clear, accessible language

Data source: Microsoft Learn (via MCP)

Remember previous documentation searches for context.
""",
        chat_client=chat_client,
        tools=mcp_tool,
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="HostedMCPAgent",
        description="Microsoft Learn documentation agent via MCP protocol",
        state_schema={
            "search_history": {
                "type": "array",
                "items": {"type": "string"},
                "description": "History of documentation searches",
            }
        },
        require_confirmation=False,
    )
