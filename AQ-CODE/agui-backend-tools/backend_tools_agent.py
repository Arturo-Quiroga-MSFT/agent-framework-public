"""
Backend Tool Rendering - Secure server-side function execution.

This demonstrates how tools can be defined and executed on the server
while keeping credentials and business logic secure.
"""
import asyncio
import os
from typing import Optional
from pydantic import BaseModel, Field

from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


# ============================================================================
# DATA MODELS - Type-safe request/response structures
# ============================================================================

class WeatherRequest(BaseModel):
    """Request model for weather lookup."""
    city: str = Field(..., description="City name")
    country_code: Optional[str] = Field(None, description="Two-letter country code (e.g., 'US', 'UK')")


class WeatherResponse(BaseModel):
    """Response model for weather data."""
    city: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    description: str


class DatabaseQueryRequest(BaseModel):
    """Request model for database operations."""
    query_type: str = Field(..., description="Type: 'users', 'products', 'orders'")
    filter: Optional[str] = Field(None, description="Optional filter criteria")


class DatabaseQueryResponse(BaseModel):
    """Response model for database queries."""
    query_type: str
    record_count: int
    results: list[dict]
    execution_time_ms: float


# ============================================================================
# BACKEND TOOLS - Server-side implementations
# ============================================================================

class BackendToolsAgent:
    """Agent with backend tools that execute securely on the server."""
    
    def __init__(self, chat_client):
        """Initialize the agent with backend tools."""
        self.chat_client = chat_client
        self.console = Console()
        
        # Simulated API keys (in production, these would be in environment/vault)
        self._weather_api_key = "sk_weather_secret_key_12345"
        self._db_connection_string = "Server=db.example.com;Database=prod;User=admin;Password=secret"
        
        # Create agent with backend tools
        self.agent = ChatAgent(
            name="BackendToolsAgent",
            instructions="""You are a helpful assistant with access to backend systems.

You have secure access to:
1. Weather API - Get current weather for any city
2. Database - Query user, product, and order data

When users ask questions:
- Use get_weather for weather-related queries
- Use query_database for data lookups
- Be specific about what information you're retrieving
- Explain the results in a user-friendly way

Remember: All tools execute securely on the server with proper authentication.""",
            chat_client=self.chat_client,
            tools=[self.get_weather, self.query_database, self.send_notification]
        )
    
    @ai_function
    async def get_weather(
        self,
        city: str,
        country_code: Optional[str] = None
    ) -> WeatherResponse:
        """Get current weather for a city.
        
        This tool has access to a weather API with credentials stored securely
        on the server. Clients never see the API key.
        
        Args:
            city: Name of the city
            country_code: Optional two-letter country code
            
        Returns:
            Current weather data
        """
        # Log the secure operation
        self.console.print(f"\n[dim]🔐 Backend: Calling Weather API with key: {self._weather_api_key[:15]}...[/dim]")
        
        # Simulate API call with delay
        await asyncio.sleep(0.5)
        
        # Simulated weather data (in production, would call actual API)
        weather_data = {
            "Seattle": {"temp": 52, "condition": "Rainy", "humidity": 85, "wind": 12.5},
            "New York": {"temp": 68, "condition": "Partly Cloudy", "humidity": 60, "wind": 8.0},
            "London": {"temp": 55, "condition": "Foggy", "humidity": 78, "wind": 10.0},
            "Tokyo": {"temp": 72, "condition": "Sunny", "humidity": 55, "wind": 5.5},
            "Paris": {"temp": 59, "condition": "Clear", "humidity": 65, "wind": 7.0},
        }
        
        city_data = weather_data.get(city, {
            "temp": 70, "condition": "Clear", "humidity": 50, "wind": 8.0
        })
        
        response = WeatherResponse(
            city=city,
            temperature=city_data["temp"],
            condition=city_data["condition"],
            humidity=city_data["humidity"],
            wind_speed=city_data["wind"],
            description=f"Current weather in {city}: {city_data['condition']}, {city_data['temp']}°F"
        )
        
        self.console.print(f"[green]✓[/green] Weather data retrieved for {city}")
        return response
    
    @ai_function
    async def query_database(
        self,
        query_type: str,
        filter: Optional[str] = None
    ) -> DatabaseQueryResponse:
        """Query the production database securely.
        
        This tool has direct database access with credentials stored on the server.
        Clients never see connection strings or have direct DB access.
        
        Args:
            query_type: Type of query ('users', 'products', 'orders')
            filter: Optional filter criteria
            
        Returns:
            Query results
        """
        # Log the secure operation
        self.console.print(f"\n[dim]🔐 Backend: Connecting to database: {self._db_connection_string[:30]}...[/dim]")
        
        # Simulate database query with delay
        await asyncio.sleep(0.8)
        
        # Simulated database results
        mock_data = {
            "users": [
                {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin"},
                {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "User"},
                {"id": 3, "name": "Carol White", "email": "carol@example.com", "role": "Manager"},
            ],
            "products": [
                {"id": 101, "name": "Laptop Pro", "price": 1299.99, "stock": 45},
                {"id": 102, "name": "Wireless Mouse", "price": 29.99, "stock": 150},
                {"id": 103, "name": "USB-C Cable", "price": 12.99, "stock": 200},
            ],
            "orders": [
                {"id": 5001, "customer": "Alice Johnson", "total": 1329.98, "status": "Shipped"},
                {"id": 5002, "customer": "Bob Smith", "total": 42.98, "status": "Processing"},
                {"id": 5003, "customer": "Carol White", "total": 1299.99, "status": "Delivered"},
            ]
        }
        
        results = mock_data.get(query_type, [])
        
        response = DatabaseQueryResponse(
            query_type=query_type,
            record_count=len(results),
            results=results,
            execution_time_ms=156.3
        )
        
        self.console.print(f"[green]✓[/green] Database query completed: {len(results)} records")
        return response
    
    @ai_function
    async def send_notification(
        self,
        recipient: str,
        message: str,
        priority: str = "normal"
    ) -> str:
        """Send a notification via internal messaging system.
        
        This demonstrates a tool that performs actions (not just queries).
        The messaging system credentials are kept on the server.
        
        Args:
            recipient: Email or username
            message: Notification message
            priority: Priority level (low, normal, high, urgent)
            
        Returns:
            Confirmation message
        """
        self.console.print(f"\n[dim]🔐 Backend: Sending notification via internal system[/dim]")
        await asyncio.sleep(0.3)
        
        self.console.print(f"[green]✓[/green] Notification sent to {recipient}")
        return f"Notification sent successfully to {recipient} with {priority} priority"
    
    async def run_query(self, user_query: str):
        """Execute a user query with streaming response."""
        self.console.print(f"\n[bold blue]User Query:[/bold blue] {user_query}\n")
        
        # Show "thinking" indicator
        with self.console.status("[bold green]Agent is processing...", spinner="dots"):
            response = await self.agent.run(user_query)
        
        # Display the response
        self.console.print(Panel(
            response.text,
            title="[bold cyan]Agent Response",
            border_style="cyan"
        ))
        
        return response


async def demo_backend_tools():
    """Demonstrate backend tool rendering."""
    console = Console()
    
    console.print("\n[bold cyan]🔧 Backend Tool Rendering Demo[/bold cyan]")
    console.print("[dim]Demonstrates secure server-side tool execution[/dim]\n")
    
    # Initialize client
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    if not endpoint:
        console.print("\n[yellow]⚠️  No Azure OpenAI credentials - running in demo mode[/yellow]")
        console.print("[dim]Set AZURE_OPENAI_ENDPOINT to test with real agent[/dim]\n")
        demo_mode_display(console)
        return
    
    client = AzureOpenAIResponsesClient(
        endpoint=endpoint,
        deployment_name=deployment,
        credential=DefaultAzureCredential()
    )
    
    chat_client = client.create_chat_client()
    agent = BackendToolsAgent(chat_client)
    
    # Example queries
    queries = [
        "What's the weather like in Seattle?",
        "Show me all users in the database",
        "Get the product inventory",
        "Compare weather between New York and London"
    ]
    
    console.print("[bold]Example queries you can try:[/bold]")
    for i, q in enumerate(queries, start=1):
        console.print(f"  {i}. {q}")
    console.print("  [dim]Or type your own query[/dim]\n")
    
    choice = console.input("[bold]Enter query number or custom query:[/bold] ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(queries):
        query = queries[int(choice) - 1]
    else:
        query = choice
    
    # Execute the query
    await agent.run_query(query)
    
    # Show security benefits
    console.print("\n[bold green]🔐 Security Benefits of Backend Tool Rendering[/bold green]\n")
    
    benefits = Table(show_header=False, box=None)
    benefits.add_row("✓", "[green]API keys never exposed to client")
    benefits.add_row("✓", "[green]Database credentials remain on server")
    benefits.add_row("✓", "[green]Business logic hidden from inspection")
    benefits.add_row("✓", "[green]Centralized audit logging")
    benefits.add_row("✓", "[green]Rate limiting and access control")
    
    console.print(benefits)


def demo_mode_display(console: Console):
    """Display demo mode information."""
    
    console.print(Panel.fit(
        """[bold cyan]Backend Tool Architecture[/bold cyan]

[yellow]Client Side:[/yellow]
• Sends natural language query
• Receives structured responses
• Never sees credentials or connection details

[yellow]Server Side:[/yellow]
• Agent determines which tools to call
• Tools execute with secure credentials
• Results streamed back to client

[bold]Tool Examples:[/bold]
1. get_weather(city, country) → WeatherResponse
2. query_database(type, filter) → DatabaseQueryResponse
3. send_notification(recipient, message) → Confirmation""",
        border_style="blue"
    ))
    
    console.print("\n[bold]Example Tool Execution Flow:[/bold]\n")
    
    # Show the flow
    steps = [
        ("1️⃣", "Client", "User asks: 'What's the weather in Seattle?'"),
        ("2️⃣", "Agent", "Determines get_weather tool is needed"),
        ("3️⃣", "Server", "Calls Weather API with secure API key"),
        ("4️⃣", "Server", "Returns: WeatherResponse(temp=52, condition='Rainy')"),
        ("5️⃣", "Client", "Displays formatted weather information")
    ]
    
    for emoji, location, description in steps:
        console.print(f"{emoji} [cyan]{location:8}[/cyan] → {description}")
    
    console.print("\n[bold green]✓ Credentials protected[/bold green]")
    console.print("[bold green]✓ Business logic secure[/bold green]")
    console.print("[bold green]✓ Type-safe execution[/bold green]\n")


if __name__ == "__main__":
    asyncio.run(demo_backend_tools())
