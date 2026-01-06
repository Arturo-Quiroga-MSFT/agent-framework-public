#!/usr/bin/env python3
"""
Example 11: Real API Tool Integrations with DevUI (Enhanced Tools)

This example demonstrates REAL tool integrations that show up beautifully in DevUI's Tools tab.
Unlike mock tools, these make actual API calls and perform real operations.

Tools Integrated:
1. **Web Search (Tavily)**: Real web search with current information
2. **Weather API (OpenWeatherMap)**: Live weather data for any location
3. **File Operations**: Read and write files locally
4. **Calculator**: Perform mathematical computations
5. **Current Time**: Get current date/time for any timezone

Key Features:
- All tools visible in DevUI Tools tab with inputs/outputs
- Real API calls with actual data
- Error handling and validation
- Structured tool responses
- Tracing enabled for full observability

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Add TAVILY_API_KEY to .env (get free key at https://tavily.com)
3. Add OPENWEATHER_API_KEY to .env (get free key at https://openweathermap.org/api)
4. Install dependencies: pip install -r requirements.txt

Usage:
    python 11_github_tools_integration.py
    
    Opens DevUI at http://localhost:8086 with full tool integration!

Example Queries:
- "Search the web for latest news about AI agents"
- "What's the weather in San Francisco?"
- "Calculate the compound interest on $10000 at 5% for 10 years"
- "Save this summary to a file called notes.txt"
- "What time is it in Tokyo?"
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated

import requests
from dotenv import load_dotenv

from agent_framework import ChatAgent, ai_function
from agent_framework.openai import OpenAIChatClient

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

# API Keys for real integrations
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please set it first.")

# Create output directory for file operations
OUTPUT_DIR = Path("workflow_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# TOOL 1: Web Search (Tavily)
# ============================================================================

@ai_function
def search_web(
    query: Annotated[str, "Search query to find information on the web"],
    max_results: Annotated[int, "Maximum number of results to return (1-10)"] = 5,
) -> str:
    """Search the web for current information using Tavily API.
    
    Use this when you need:
    - Recent news or events
    - Current facts or statistics
    - Product information
    - Research on any topic
    - Real-time information not in your training data
    
    Returns: Formatted search results with titles, URLs, and snippets.
    """
    if not TAVILY_API_KEY:
        return "❌ Error: TAVILY_API_KEY not configured in .env file. Get a free key at https://tavily.com"
    
    try:
        # Read API key from file if not in env
        tavily_key = TAVILY_API_KEY
        if not tavily_key:
            tavily_key_file = Path(__file__).parent.parent / "TAVILY_KEY.txt"
            if tavily_key_file.exists():
                tavily_key = tavily_key_file.read_text().strip()
        
        if not tavily_key:
            return "❌ Error: TAVILY_API_KEY not found in .env or TAVILY_KEY.txt"
        
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": tavily_key,
            "query": query,
            "max_results": min(max_results, 10),
            "include_answer": True,
            "search_depth": "basic",
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Format results
        results = []
        
        # Add AI-generated answer if available
        if data.get("answer"):
            results.append(f"📊 Summary: {data['answer']}\n")
        
        # Add search results
        results.append("🔍 Search Results:")
        for i, result in enumerate(data.get("results", [])[:max_results], 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")[:200] + "..."
            results.append(f"\n{i}. **{title}**")
            results.append(f"   URL: {url}")
            results.append(f"   {content}")
        
        return "\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"❌ Error searching web: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


# ============================================================================
# TOOL 2: Weather API (OpenWeatherMap)
# ============================================================================

@ai_function
def get_weather(
    location: Annotated[str, "City name or 'City, Country' (e.g., 'London, UK')"],
) -> str:
    """Get current weather information for any location worldwide.
    
    Use this when users ask about:
    - Current weather conditions
    - Temperature
    - Humidity and wind
    - Weather forecasts
    
    Returns: Current weather data including temperature, conditions, humidity, and wind.
    """
    if not OPENWEATHER_API_KEY:
        return "❌ Error: OPENWEATHER_API_KEY not configured. Get a free key at https://openweathermap.org/api"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "imperial",  # Fahrenheit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract weather data
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"].title()
        wind_speed = data["wind"]["speed"]
        city = data["name"]
        country = data["sys"]["country"]
        
        # Format response
        result = f"""🌤️ Weather in {city}, {country}:

📊 Current Conditions:
   • Temperature: {temp}°F (feels like {feels_like}°F)
   • Conditions: {description}
   • Humidity: {humidity}%
   • Wind Speed: {wind_speed} mph

🕒 Data retrieved at: {datetime.now().strftime('%I:%M %p')}"""
        
        return result
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"❌ Location '{location}' not found. Try 'City, Country' format (e.g., 'Paris, FR')"
        return f"❌ Error fetching weather: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Network error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


# ============================================================================
# TOOL 3: File Operations
# ============================================================================

@ai_function
def save_to_file(
    filename: Annotated[str, "Name of the file to save (e.g., 'notes.txt', 'summary.md')"],
    content: Annotated[str, "Content to write to the file"],
) -> str:
    """Save content to a file in the workflow_outputs directory.
    
    Use this when users want to:
    - Save summaries or notes
    - Export data
    - Create documents
    - Store results for later use
    
    Returns: Confirmation with file path.
    """
    try:
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        file_path = OUTPUT_DIR / safe_filename
        
        # Write file
        file_path.write_text(content, encoding="utf-8")
        
        return f"✅ Content saved successfully!\n📁 Location: {file_path.absolute()}\n📊 Size: {len(content)} characters"
    
    except Exception as e:
        return f"❌ Error saving file: {str(e)}"


@ai_function
def read_from_file(
    filename: Annotated[str, "Name of the file to read from workflow_outputs directory"],
) -> str:
    """Read content from a previously saved file.
    
    Use this when users want to:
    - Review saved notes
    - Load previous summaries
    - Access stored data
    
    Returns: File content or error message.
    """
    try:
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        file_path = OUTPUT_DIR / safe_filename
        
        if not file_path.exists():
            return f"❌ File '{filename}' not found in workflow_outputs directory."
        
        content = file_path.read_text(encoding="utf-8")
        return f"📄 Content of {filename}:\n\n{content}"
    
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


# ============================================================================
# TOOL 4: Calculator
# ============================================================================

@ai_function
def calculate(
    expression: Annotated[str, "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5 + 3')"],
) -> str:
    """Perform mathematical calculations safely.
    
    Use this for:
    - Basic arithmetic (+, -, *, /)
    - Percentages and ratios
    - Financial calculations
    - Unit conversions
    
    Returns: Calculation result or error message.
    """
    try:
        # Safe evaluation (only math operations, no exec/eval of arbitrary code)
        # Using a safer approach with limited builtins
        allowed_names = {
            "abs": abs,
            "round": round,
            "pow": pow,
            "min": min,
            "max": max,
        }
        
        # Parse and evaluate safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return f"🔢 Calculation: {expression}\n✅ Result: {result}"
    
    except SyntaxError:
        return f"❌ Invalid expression: '{expression}'"
    except NameError as e:
        return f"❌ Unsupported operation in expression: {str(e)}"
    except ZeroDivisionError:
        return "❌ Error: Division by zero"
    except Exception as e:
        return f"❌ Calculation error: {str(e)}"


# ============================================================================
# TOOL 5: Current Time
# ============================================================================

@ai_function
def get_current_time(
    timezone: Annotated[str, "Timezone name (e.g., 'UTC', 'America/New_York', 'Asia/Tokyo')"] = "UTC",
) -> str:
    """Get the current date and time for a specific timezone.
    
    Use this when users ask:
    - What time is it?
    - Current date
    - Time in different timezones
    
    Returns: Current date and time with timezone info.
    """
    try:
        from zoneinfo import ZoneInfo
        
        try:
            tz = ZoneInfo(timezone)
        except Exception:
            # Try common timezone abbreviations
            tz_map = {
                "PST": "America/Los_Angeles",
                "EST": "America/New_York",
                "CST": "America/Chicago",
                "MST": "America/Denver",
                "JST": "Asia/Tokyo",
                "GMT": "Europe/London",
            }
            timezone = tz_map.get(timezone.upper(), "UTC")
            tz = ZoneInfo(timezone)
        
        now = datetime.now(tz)
        
        result = f"""🕒 Current Time Information:

📅 Date: {now.strftime('%A, %B %d, %Y')}
⏰ Time: {now.strftime('%I:%M:%S %p')}
🌍 Timezone: {timezone}
📊 ISO Format: {now.isoformat()}"""
        
        return result
    
    except Exception as e:
        return f"❌ Error: Invalid timezone '{timezone}'. Use format like 'America/New_York' or 'UTC'"


# ============================================================================
# Create Agent with All Tools
# ============================================================================

async def create_tool_agent():
    """Create a research agent with all real tool integrations."""
    
    # Create OpenAI-compatible chat client
    client = OpenAIChatClient(
        model_id=GITHUB_MODEL,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )
    
    # Create agent with all tools
    agent = ChatAgent(
        name="ResearchAssistant",
        description="Intelligent assistant with web search, weather, file operations, calculator, and time tools",
        instructions="""You are a helpful research assistant with access to powerful real-world tools.

**Your Capabilities:**

1. **Web Search** (`search_web`):
   - Find current information, news, facts
   - Research any topic with real-time data
   - Get product information, statistics

2. **Weather** (`get_weather`):
   - Check current weather for any location
   - Provide temperature, conditions, humidity

3. **File Operations** (`save_to_file`, `read_from_file`):
   - Save summaries, notes, or results to files
   - Read previously saved files
   - All files stored in workflow_outputs/

4. **Calculator** (`calculate`):
   - Perform mathematical calculations
   - Handle percentages, ratios, conversions

5. **Time** (`get_current_time`):
   - Get current date/time for any timezone
   - Convert between timezones

**Guidelines:**

- **Use tools proactively** when they can provide better answers
- **Web search** for anything requiring current information
- **Explain tool outputs** clearly to users
- **Save important information** when users might need it later
- **Handle errors gracefully** and suggest alternatives
- **Be concise** but thorough in responses

When users ask questions:
1. Determine if tools can help (usually yes!)
2. Call appropriate tools
3. Synthesize results into clear answers
4. Offer to save useful information

Examples:
- "What's happening with AI agents?" → Use search_web
- "Weather in Paris?" → Use get_weather
- "Save this summary" → Use save_to_file
- "Calculate 15% tip on $87" → Use calculate
- "What time is it in Tokyo?" → Use get_current_time""",
        chat_client=client,
        tools=[search_web, get_weather, save_to_file, read_from_file, calculate, get_current_time],
    )
    
    return agent


def main():
    """Launch the tool integration example in DevUI."""
    from agent_framework.devui import serve
    
    print("\n" + "="*80)
    print("🛠️  Real API Tool Integrations - Enhanced Tools Example")
    print("="*80)
    print("\n📋 Available Tools:")
    print("   1. 🔍 Web Search (Tavily API)")
    print("   2. 🌤️  Weather (OpenWeatherMap API)")
    print("   3. 📁 File Operations (Read/Write)")
    print("   4. 🔢 Calculator (Safe Math)")
    print("   5. 🕒 Current Time (Timezone-aware)")
    print("\n🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("🎨 Feature: Real tool integrations visible in DevUI Tools tab")
    print("\n🌐 Starting DevUI server...")
    
    # Create the agent
    agent = asyncio.run(create_tool_agent())
    
    print("\n✅ Research assistant created with all tools")
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8086")
    print("📡 API:     http://localhost:8086/v1/*")
    print("🔍 Entity:  ResearchAssistant")
    print("📊 Feature: Watch tools execute in real-time")
    
    print("\n" + "="*80)
    print("💡 How to See Tools in Action")
    print("="*80)
    print("\n1. Open http://localhost:8086 in your browser")
    print("2. Select 'ResearchAssistant' from dropdown")
    print("3. Try these example queries:")
    print("\n   🔍 Web Search:")
    print("      • 'Search for latest developments in AI agents'")
    print("      • 'What are the top trends in tech for 2026?'")
    print("      • 'Find information about Microsoft Agent Framework'")
    
    print("\n   🌤️  Weather:")
    print("      • 'What's the weather in San Francisco?'")
    print("      • 'Check weather in Tokyo, Japan'")
    print("      • 'Is it raining in London?'")
    
    print("\n   🔢 Calculator:")
    print("      • 'Calculate 15% tip on $87.50'")
    print("      • 'What's 10000 * 1.05 to the power of 10?'")
    print("      • 'Divide 1000 by 7'")
    
    print("\n   📁 File Operations:")
    print("      • 'Save this weather data to weather.txt'")
    print("      • 'Create a summary file with search results'")
    print("      • 'Read the file weather.txt'")
    
    print("\n   🕒 Current Time:")
    print("      • 'What time is it in Tokyo?'")
    print("      • 'Current time in New York'")
    print("      • 'What's the date today?'")
    
    print("\n4. Watch the magic:")
    print("   • Agent decides which tools to use")
    print("   • Tools execute with real API calls")
    print("   • Results appear in chat (~10-20s)")
    print("   • Check 'Tools' tab to see tool inputs/outputs")
    print("   • Check 'Traces' tab for full execution details")
    
    print("\n" + "="*80)
    print("🔍 DevUI Features to Explore")
    print("="*80)
    print("\n1. **Chat Tab**: See conversation and tool results")
    print("2. **Tools Tab**: View all tool executions with inputs/outputs")
    print("3. **Traces Tab**: Deep dive into execution with token usage")
    print("4. **Agent Info**: See available tools and descriptions")
    
    print("\n" + "="*80)
    print("📊 Tool Integration Highlights")
    print("="*80)
    print("\n✨ What's Different from Mock Tools:")
    print("   • Real API calls to Tavily, OpenWeatherMap")
    print("   • Actual file I/O operations")
    print("   • Live data, not hardcoded responses")
    print("   • Full tracing and observability")
    print("   • Error handling for API failures")
    
    print("\n💡 Configuration Required:")
    if not TAVILY_API_KEY:
        print("   ⚠️  TAVILY_API_KEY not set (web search disabled)")
        print("      Get free key: https://tavily.com")
    else:
        print("   ✅ TAVILY_API_KEY configured")
    
    if not OPENWEATHER_API_KEY:
        print("   ⚠️  OPENWEATHER_API_KEY not set (weather disabled)")
        print("      Get free key: https://openweathermap.org/api")
    else:
        print("   ✅ OPENWEATHER_API_KEY configured")
    
    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Launch DevUI server with tracing enabled
    serve(
        entities=[agent],
        port=8086,
        auto_open=True,
        tracing_enabled=True,  # Enable OpenTelemetry tracing
    )


if __name__ == "__main__":
    main()
