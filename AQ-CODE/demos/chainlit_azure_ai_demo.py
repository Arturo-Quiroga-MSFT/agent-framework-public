"""
Chainlit Demo - Azure AI Agent Framework V2
============================================

A polished chat UI for demonstrating Azure AI Agent Framework capabilities.
Chainlit handles streaming, tool calls, and conversation state natively.

Demos available (select via sidebar settings):
1. Basic Chat - Simple conversational agent
2. Weather Function Tool - Agent with custom Python function
3. Code Interpreter - Agent that can execute Python code
4. Bing Grounding - Agent with web search capabilities
5. File Search - Agent that searches uploaded documents
6. Azure AI Search - Agent with enterprise search integration

Run with: chainlit run chainlit_azure_ai_demo.py -w
"""

import os
from pathlib import Path
from typing import Annotated
from datetime import datetime
import httpx
import chainlit as cl
from dotenv import load_dotenv
from pydantic import Field
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from agent_framework_azure_ai import AzureAIProjectAgentProvider
from agent_framework import HostedCodeInterpreterTool, TextContent, CitationAnnotation, HostedFileContent

# Load environment variables from script's directory
script_dir = Path(__file__).parent
load_dotenv(script_dir / ".env")

# Output directory for generated plots
OUTPUT_DIR = script_dir / "generated_plots"
OUTPUT_DIR.mkdir(exist_ok=True)

# Azure AI configuration
AZURE_AI_PROJECT_ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
assert AZURE_AI_PROJECT_ENDPOINT, "AZURE_AI_PROJECT_ENDPOINT environment variable required"


# ================== Tool Definitions ==================

def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    print(f"[DEBUG] get_weather function called with location: {location}")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    print(f"[DEBUG] API key present: {bool(api_key)}")
    
    if not api_key:
        # Fallback to simulated data if no API key
        weather_data = {
            "seattle": {"temp_c": 12, "condition": "Cloudy with light rain"},
            "london": {"temp_c": 8, "condition": "Overcast"},
            "tokyo": {"temp_c": 18, "condition": "Partly cloudy"},
            "new york": {"temp_c": 15, "condition": "Clear skies"},
            "paris": {"temp_c": 10, "condition": "Light drizzle"},
            "sydney": {"temp_c": 25, "condition": "Sunny"},
            "mumbai": {"temp_c": 32, "condition": "Hot and humid"},
            "berlin": {"temp_c": 6, "condition": "Cold and foggy"},
            "mexico city": {"temp_c": 22, "condition": "Partly cloudy"},
        }
        city_lower = location.lower()
        if city_lower in weather_data:
            data = weather_data[city_lower]
            return f"The weather in {location} is {data['condition']} with a temperature of {data['temp_c']}°C."
        return f"Weather data not available for {location} (no API key configured)."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        result = f"The weather in {location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
        print(f"[DEBUG] Weather result: {result}")
        return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        print(f"[DEBUG] Exception in get_weather: {e}")
        return f"Error: {str(e)}"


# ================== Agent Creation ==================

async def create_basic_agent():
    """Create a basic conversational agent."""
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            agent = await provider.create_agent(
                name="BasicChatAgent",
                instructions="""You are a friendly and knowledgeable assistant. 
                Provide helpful, accurate, and engaging responses. 
                Be concise but thorough.""",
            )
            return agent, provider


async def create_weather_agent():
    """Create an agent with weather function tool."""
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            agent = await provider.create_agent(
                name="WeatherAgent",
                instructions="""You are a helpful weather assistant.
                When asked about weather, ALWAYS use the get_weather function to fetch weather data.
                Never apologize or say you can't access weather data - you have the get_weather function available.
                Provide friendly, informative weather reports based on the data returned.""",
                tools=[get_weather],
            )
            return agent, provider


async def create_code_interpreter_agent():
    """Create an agent with code interpreter capability."""
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            agent = await provider.create_agent(
                name="CodeInterpreterAgent",
                instructions="""You are a data analysis and coding assistant.
                Use the code interpreter tool to execute Python code for:
                - Mathematical calculations
                - Data analysis
                - Creating visualizations
                - Processing data
                Always show intermediate steps and explain your approach.""",
                tools=HostedCodeInterpreterTool(),
            )
            return agent, provider


async def create_bing_grounded_agent():
    """Create an agent with Bing search grounding."""
    bing_connection = os.getenv("BING_PROJECT_CONNECTION_ID")
    if not bing_connection:
        raise ValueError("BING_PROJECT_CONNECTION_ID environment variable required for Bing grounding")
    
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            agent = await provider.create_agent(
                name="BingGroundedAgent",
                instructions="""You are a research assistant with access to web search.
                Use Bing search to find current, accurate information.
                Always cite your sources when providing information from the web.
                Synthesize information from multiple sources when relevant.""",
                tools={
                    "type": "bing_grounding",
                    "bing_grounding": {
                        "search_configurations": [
                            {"project_connection_id": bing_connection}
                        ]
                    },
                },
            )
            return agent, provider


# ================== Session State ==================

@cl.set_chat_profiles
async def chat_profiles():
    """Define available chat profiles (demo modes)."""
    return [
        cl.ChatProfile(
            name="Basic Chat",
            markdown_description="💬 Simple conversational agent for general questions",
            icon="https://img.icons8.com/fluency/96/chat.png",
        ),
        cl.ChatProfile(
            name="Weather Tool",
            markdown_description="🌤️ Real-time weather lookup with OpenWeatherMap API",
            icon="https://img.icons8.com/fluency/96/partly-cloudy-day.png",
        ),
        cl.ChatProfile(
            name="Code Interpreter",
            markdown_description="💻 Execute Python code, create visualizations & analyze data",
            icon="https://img.icons8.com/fluency/96/code.png",
        ),
        cl.ChatProfile(
            name="Bing Grounding",
            markdown_description="🔍 Web search powered research with citations",
            icon="https://img.icons8.com/fluency/96/search.png",
        ),
    ]


@cl.set_starters
async def set_starters():
    """Set starter prompts - shown on new chat."""
    return [
        cl.Starter(
            label="🌤️ Weather in Tokyo",
            message="What's the weather like in Tokyo right now?",
            icon="https://img.icons8.com/fluency/96/partly-cloudy-day.png",
        ),
        cl.Starter(
            label="📊 Population chart",
            message="Create a bar chart showing the top 10 most populated countries in the world",
            icon="https://img.icons8.com/fluency/96/bar-chart.png",
        ),
        cl.Starter(
            label="📈 Compound interest",
            message="Plot a line chart showing how $10,000 grows over 30 years with 7% compound interest",
            icon="https://img.icons8.com/fluency/96/money-bag.png",
        ),
        cl.Starter(
            label="💡 Explain quantum computing",
            message="Can you explain quantum computing in simple terms?",
            icon="https://img.icons8.com/fluency/96/atom.png",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with mode-specific welcome."""
    chat_profile = cl.user_session.get("chat_profile")
    
    # Enhanced welcome messages with mode explanations
    welcome_messages = {
        "Basic Chat": """👋 **Welcome to Basic Chat!**

I'm a conversational AI assistant that can help with:
- Answering questions on any topic
- Writing and editing text
- Explaining concepts
- Brainstorming ideas

Try one of the suggested prompts below, or ask me anything!""",

        "Weather Tool": """🌤️ **Welcome to Weather Tool!**

I can fetch **real-time weather data** for any city using the OpenWeatherMap API.

I'll provide:
- Current temperature & conditions
- "Feels like" temperature
- Humidity levels
- Clothing recommendations

Try one of the suggested prompts, or ask about any city!""",

        "Code Interpreter": """💻 **Welcome to Code Interpreter!**

I can **execute Python code** to help you with:
- 📊 Creating charts and visualizations
- 🔢 Mathematical calculations
- 📈 Data analysis
- 🎨 Generating plots with matplotlib

Charts will be displayed inline. Try one of the suggested prompts!""",

        "Bing Grounding": """🔍 **Welcome to Bing Grounding!**

I'm a research assistant with **web search capabilities**.

I can:
- Find current news and information
- Answer questions with real-time data
- Provide sources and citations
- Synthesize information from multiple sources

Try one of the suggested prompts, or ask about any topic!""",
    }
    
    profile = chat_profile or "Basic Chat"
    
    await cl.Message(
        content=welcome_messages.get(profile, welcome_messages["Basic Chat"]),
    ).send()
    
    # Store chat history for context
    cl.user_session.set("chat_history", [])


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    chat_profile = cl.user_session.get("chat_profile") or "Basic Chat"
    chat_history = cl.user_session.get("chat_history") or []
    
    # Create thinking indicator
    thinking_msg = cl.Message(content="Thinking...")
    await thinking_msg.send()
    
    try:
        # Build context from history (last 6 messages = 3 exchanges)
        context = ""
        if chat_history:
            context = "\n\nPrevious conversation:\n"
            for msg in chat_history[-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        # Route to appropriate agent
        if chat_profile == "Basic Chat":
            response = await run_basic_chat(message.content, context)
            images = []
        elif chat_profile == "Weather Tool":
            response = await run_weather_chat(message.content, context)
            images = []
        elif chat_profile == "Code Interpreter":
            response, images = await run_code_interpreter_chat(message.content, context)
        elif chat_profile == "Bing Grounding":
            response = await run_bing_chat(message.content, context)
            images = []
        else:
            response = await run_basic_chat(message.content, context)
            images = []
        
        # Update history
        chat_history.append({"role": "user", "content": message.content})
        chat_history.append({"role": "assistant", "content": response})
        cl.user_session.set("chat_history", chat_history)
        
        # Update the thinking message with response
        thinking_msg.content = response
        
        # Add images if any were generated
        if images:
            elements = []
            for i, img_data in enumerate(images):
                elements.append(
                    cl.Image(
                        content=img_data,
                        name=f"chart_{i+1}",
                        display="inline",
                    )
                )
            thinking_msg.elements = elements
        
        await thinking_msg.update()
        
    except Exception as e:
        thinking_msg.content = f"Error: {str(e)}"
        await thinking_msg.update()


# ================== Agent Runners ==================

async def run_basic_chat(user_query: str, context: str) -> str:
    """Run basic chat agent."""
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            
            instructions = f"""You are a friendly and knowledgeable assistant. 
            Provide helpful, accurate, and engaging responses.
            Be concise but thorough.{context}"""
            
            agent = await provider.create_agent(
                name="BasicChatAgent",
                instructions=instructions,
            )
            
            thread = agent.get_new_thread()
            result = await agent.run(user_query, thread=thread, store=False)
            return str(result.text) if hasattr(result, 'text') else str(result)


async def run_weather_chat(user_query: str, context: str) -> str:
    """Run weather agent with function tool."""
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            
            instructions = f"""You are a helpful weather assistant. 
            When asked about weather, ALWAYS use the get_weather function to fetch weather data.
            Never apologize or say you can't access weather data - you have the get_weather function available.
            Provide friendly, informative weather reports based on the data returned.{context}"""
            
            agent = await provider.create_agent(
                name="WeatherAgent",
                instructions=instructions,
                tools=[get_weather],
            )
            
            thread = agent.get_new_thread()
            result = await agent.run(user_query, thread=thread, store=False)
            return str(result.text) if hasattr(result, 'text') else str(result)


async def run_code_interpreter_chat(user_query: str, context: str) -> tuple[str, list[bytes]]:
    """Run code interpreter agent. Returns (text_response, list_of_image_bytes).
    
    Uses V2 pattern: extract files from result.messages annotations and download
    via OpenAI containers API.
    """
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            
            instructions = f"""You are a data analysis and coding assistant.
            Use the code interpreter tool to execute Python code for:
            - Mathematical calculations
            - Data analysis
            - Creating visualizations
            - Processing data
            Always show intermediate steps and explain your approach.
            When creating visualizations, always use matplotlib to generate and display the chart.{context}"""
            
            agent = await provider.create_agent(
                name="CodeInterpreterAgent",
                instructions=instructions,
                tools=HostedCodeInterpreterTool(),
            )
            
            result = await agent.run(user_query)
            
            result_text = str(result.text) if hasattr(result, 'text') else str(result)
            image_data_list = []
            
            # V2 pattern: extract file annotations from result.messages
            try:
                file_refs = []  # List of (file_id, container_id, filename) tuples
                
                for message in result.messages:
                    for content in message.contents:
                        # Check TextContent for CitationAnnotations
                        if isinstance(content, TextContent) and content.annotations:
                            for annotation in content.annotations:
                                if isinstance(annotation, CitationAnnotation) and annotation.file_id:
                                    container_id = annotation.additional_properties.get("container_id") if annotation.additional_properties else None
                                    filename = annotation.url or f"{annotation.file_id}.png"
                                    if filename.startswith("sandbox:"):
                                        filename = filename.split("/")[-1]
                                    file_refs.append((annotation.file_id, container_id, filename))
                                    print(f"[DEBUG] Found CitationAnnotation: file_id={annotation.file_id}, container_id={container_id}")
                        
                        # Check for HostedFileContent directly
                        elif isinstance(content, HostedFileContent) and content.file_id:
                            container_id = content.additional_properties.get("container_id") if content.additional_properties else None
                            filename = content.additional_properties.get("filename", f"{content.file_id}.png") if content.additional_properties else f"{content.file_id}.png"
                            file_refs.append((content.file_id, container_id, filename))
                            print(f"[DEBUG] Found HostedFileContent: file_id={content.file_id}, container_id={container_id}")
                
                # Download files using OpenAI containers API
                if file_refs:
                    openai_client = agent.chat_client.client
                    
                    for file_id, container_id, filename in file_refs:
                        if not container_id:
                            print(f"[DEBUG] Skipping {file_id}: no container_id")
                            continue
                        
                        try:
                            print(f"[DEBUG] Downloading {filename} (file_id={file_id}, container_id={container_id})")
                            file_content = await openai_client.containers.files.content.retrieve(
                                file_id=file_id,
                                container_id=container_id,
                            )
                            
                            content_bytes = file_content.read()
                            image_data_list.append(content_bytes)
                            
                            # Save locally
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filepath = OUTPUT_DIR / f"plot_{timestamp}_{filename}"
                            with open(filepath, 'wb') as f:
                                f.write(content_bytes)
                            print(f"[DEBUG] Saved to {filepath}")
                            
                        except Exception as e:
                            print(f"[DEBUG] Failed to download {file_id}: {e}")
                            result_text += f"\n\n⚠️ Found file but couldn't download: {str(e)}"
                else:
                    print("[DEBUG] No file annotations found in response")
            
            except Exception as e:
                print(f"[DEBUG] Error extracting files: {e}")
            
            return result_text, image_data_list


async def run_bing_chat(user_query: str, context: str) -> str:
    """Run Bing grounded agent."""
    bing_connection = os.getenv("BING_PROJECT_CONNECTION_ID")
    if not bing_connection:
        return "Bing grounding not configured. Set BING_PROJECT_CONNECTION_ID environment variable."
    
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=credential,
        ) as client:
            provider = AzureAIProjectAgentProvider(project_client=client)
            
            instructions = f"""You are a research assistant with access to web search.
            Use Bing search to find current, accurate information.
            Always cite your sources when providing information from the web.
            Synthesize information from multiple sources when relevant.{context}"""
            
            agent = await provider.create_agent(
                name="BingGroundedAgent",
                instructions=instructions,
                tools={
                    "type": "bing_grounding",
                    "bing_grounding": {
                        "search_configurations": [
                            {"project_connection_id": bing_connection}
                        ]
                    },
                },
            )
            
            thread = agent.get_new_thread()
            result = await agent.run(user_query, thread=thread, store=False)
            return str(result.text) if hasattr(result, 'text') else str(result)


# ================== Main Entry Point ==================

if __name__ == "__main__":
    # For testing without chainlit
    import asyncio
    
    async def test():
        result = await run_weather_chat("What's the weather in Tokyo?", "")
        print(result)
    
    asyncio.run(test())
