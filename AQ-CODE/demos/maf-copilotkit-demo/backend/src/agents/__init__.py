"""
MAF + CopilotKit Demo Agents

This module contains all the agent definitions ported from the Streamlit demo,
enhanced with AG-UI protocol capabilities for rich web UI interactions.
"""

from .weather_agent import create_weather_agent
from .code_agent import create_code_interpreter_agent
from .search_agent import create_bing_search_agent
from .file_agent import create_file_search_agent
from .azure_search_agent import create_azure_ai_search_agent
from .mcp_agent import create_firecrawl_agent, create_hosted_mcp_agent

__all__ = [
    "create_weather_agent",
    "create_code_interpreter_agent",
    "create_bing_search_agent",
    "create_file_search_agent",
    "create_azure_ai_search_agent",
    "create_firecrawl_agent",
    "create_hosted_mcp_agent",
]
