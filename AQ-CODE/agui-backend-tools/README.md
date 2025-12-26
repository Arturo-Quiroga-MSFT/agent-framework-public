# Backend Tool Rendering

**AGUI Enhancement #2**: Secure server-side function execution with credential protection.

## Overview

Backend Tool Rendering enables agents to execute tools on the server while keeping credentials, business logic, and sensitive operations secure. Unlike frontend tools that execute in the browser, backend tools run server-side with full access to protected resources.

## Key Benefits

### 🔐 Security
- **Credentials Protected**: API keys, database passwords, and tokens never leave the server
- **Business Logic Hidden**: Implementation details not visible to clients
- **Audit Trail**: Complete server-side logging of all tool executions
- **Access Control**: Server-enforced rate limiting and permissions

### 🎯 Type Safety
- **Pydantic Models**: Type-safe request/response structures
- **Validation**: Automatic input validation at the schema level
- **Documentation**: Self-documenting tool signatures

### 🔄 Orchestration
- **Multi-Tool Chains**: Agent can call multiple tools in sequence
- **Conditional Logic**: Tools can trigger other tools based on results
- **Error Handling**: Centralized error management

## Architecture

```
┌─────────────┐
│   Client    │  → Natural language query
└──────┬──────┘
       │ HTTPS
       ↓
┌─────────────┐
│   Agent     │  → Determines which tools to call
└──────┬──────┘
       │ Local
       ↓
┌─────────────┐
│Backend Tools│  → Execute with secure credentials
└──────┬──────┘
       │
       ├─→ Weather API (with API key)
       ├─→ Database (with connection string)
       └─→ Messaging System (with auth tokens)
```

## Implementation

### Tool Definition

```python
from agent_framework import ai_function
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str

@ai_function
async def get_weather(
    self,
    city: str,
    country_code: Optional[str] = None
) -> WeatherResponse:
    """Get current weather for a city.
    
    This tool has access to a weather API with credentials
    stored securely on the server.
    """
    # API key stored on server
    api_key = self._weather_api_key
    
    # Call external API
    data = await weather_api.get(city, api_key)
    
    # Return structured response
    return WeatherResponse(
        city=city,
        temperature=data["temp"],
        condition=data["condition"]
    )
```

### Agent Setup

```python
from agent_framework import ChatAgent

agent = ChatAgent(
    name="BackendToolsAgent",
    instructions="You have secure access to backend systems.",
    chat_client=chat_client,
    tools=[
        self.get_weather,
        self.query_database,
        self.send_notification
    ]
)
```

## Available Tools

### 1. `get_weather`
- **Purpose**: Fetch current weather data
- **Security**: Weather API key stored on server
- **Returns**: `WeatherResponse` with temperature, condition, humidity

### 2. `query_database`
- **Purpose**: Query production database
- **Security**: Database connection string never exposed
- **Returns**: `DatabaseQueryResponse` with query results

### 3. `send_notification`
- **Purpose**: Send internal notifications
- **Security**: Messaging system credentials secure
- **Returns**: Confirmation message

## Usage

### Running Tests (No Azure credentials required)

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/agui-backend-tools
source /Users/arturoquiroga/GITHUB/agent-framework-public/.venv/bin/activate
python test_backend_tools.py
```

### Running with Live Agent

```bash
# Set Azure OpenAI credentials
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"  # optional

# Run the agent
python backend_tools_agent.py
```

### Example Queries

1. **Simple Query**: "What's the weather like in Seattle?"
   - Agent calls `get_weather("Seattle")`
   - Returns current weather data

2. **Database Query**: "Show me all users in the database"
   - Agent calls `query_database("users")`
   - Returns user records

3. **Multi-Tool**: "Get weather for New York and notify admin if it's hot"
   - Agent calls `get_weather("New York")`
   - Evaluates temperature
   - Calls `send_notification()` if needed

## Comparison: Backend vs Frontend Tools

| Aspect | Frontend Tools | Backend Tools |
|--------|---------------|---------------|
| **Credentials** | ❌ Exposed to client | ✅ Secure on server |
| **Business Logic** | ❌ Visible in browser | ✅ Hidden implementation |
| **Rate Limiting** | ❌ Client-side only | ✅ Server-enforced |
| **Audit Trail** | ❌ Limited tracking | ✅ Full server logs |
| **Performance** | ✅ Instant execution | ⚠️ Network latency |

## Security Best Practices

1. **Never Return Credentials**: Tool responses should contain data, not secrets
2. **Input Validation**: Use Pydantic models to validate all inputs
3. **Rate Limiting**: Implement server-side rate limits per user/tool
4. **Audit Logging**: Log all tool executions with user context
5. **Error Messages**: Don't leak sensitive details in error messages

## Integration with Other Enhancements

- **Agentic UI**: Backend tools can update plan status during execution
- **Predictive State**: Tool results can be streamed progressively to clients

## Testing

The test suite validates:
- ✅ Security architecture
- ✅ Type safety with Pydantic models
- ✅ Execution flow simulation
- ✅ Multi-tool orchestration
- ✅ Tool inventory and discovery

## Files

- `backend_tools_agent.py`: Main implementation with 3 example tools
- `test_backend_tools.py`: Comprehensive test suite
- `README.md`: This file

## Next Steps

- Run tests to validate architecture
- Add more backend tools for your use case
- Implement with real agent for live testing
- Combine with Enhancement #3 (Predictive State Updates)
