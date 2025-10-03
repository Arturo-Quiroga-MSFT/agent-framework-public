# Real Weather Data Integration Guide

This guide shows you how to use **real weather data** from OpenWeatherMap API in your Azure AI agent samples.

## 🌤️ Overview

The samples in this directory now support:
- ✅ **Real weather data** from OpenWeatherMap API
- ✅ **Automatic fallback** to mock data if no API key is configured
- ✅ **Shared utilities** across all samples
- ✅ **Zero code changes** required - just add your API key!

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Get Your Free API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Click "Sign Up" (it's free!)
3. Verify your email
4. Go to "API keys" in your account
5. Copy your API key

**Free tier includes:**
- 1,000 API calls per day
- 60 calls per minute
- Current weather data
- No credit card required!

### Step 2: Add API Key to .env

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/python/samples/getting_started/agents/azure_ai

# Add your API key to .env
echo "OPENWEATHER_API_KEY=your_api_key_here" >> .env
```

Or edit `.env` manually:
```bash
# ==== WEATHER API (Optional - for real weather data) ====
OPENWEATHER_API_KEY=your_api_key_here
```

### Step 3: Run Your Agent

```bash
python azure_ai_basic_devui.py
```

**That's it!** The agent will now use real weather data automatically! 🎉

---

## 📊 What Changes?

### Without API Key (Mock Data):
```
User: What's the weather in Seattle?
Agent: The weather in Seattle is sunny with a high of 23°C.
📝 Note: This is mock data for testing
```

### With API Key (Real Data):
```
User: What's the weather in Seattle?
Agent: 
🌤️ Weather in Seattle, US:
🌡️ Temperature: 15.3°C (59.5°F)
🤔 Feels like: 14.2°C
☁️ Conditions: Partly cloudy
💧 Humidity: 67%
💨 Wind: 3.5 m/s
```

---

## 🛠️ Shared Utilities Module

### Location: `shared_utils.py`

This module provides reusable weather functions for all samples:

```python
from shared_utils import get_real_weather, get_mock_weather

# Get real weather (requires API key)
result = get_real_weather("Seattle")

# Get mock weather (no API key needed)
result = get_mock_weather("Seattle")
```

### Available Functions:

#### 1. `get_real_weather(location: str) -> str`
Fetches **real weather data** from OpenWeatherMap API.

**Features:**
- ✅ Current temperature (Celsius & Fahrenheit)
- ✅ Feels-like temperature
- ✅ Weather conditions (clear, cloudy, rainy, etc.)
- ✅ Humidity percentage
- ✅ Wind speed
- ✅ City and country identification
- ✅ Helpful error messages

**Example:**
```python
weather = get_real_weather("Tokyo")
print(weather)
# Output:
# 🌤️ Weather in Tokyo, JP:
# 🌡️ Temperature: 22.5°C (72.5°F)
# 🤔 Feels like: 21.8°C
# ☁️ Conditions: Clear sky
# 💧 Humidity: 55%
# 💨 Wind: 2.1 m/s
```

#### 2. `get_mock_weather(location: str) -> str`
Returns **randomized mock data** for testing without API key.

**Example:**
```python
weather = get_mock_weather("London")
print(weather)
# Output:
# 🌤️ Weather in London:
# 🌡️ Temperature: 18°C (64.4°F)
# ☁️ Conditions: Partly cloudy
# 💧 Humidity: 72%
# 📝 Note: This is mock data for testing
```

#### 3. `get_weather(location: str) -> str`
**Legacy function** for backwards compatibility (simple mock data).

---

## 🔧 How It Works

### Automatic Selection

The samples automatically choose which function to use:

```python
# In azure_ai_basic_devui.py
has_api_key = bool(os.environ.get("OPENWEATHER_API_KEY"))
weather_function = get_real_weather if has_api_key else get_mock_weather

# Agent uses the appropriate function
agent = client.create_agent(
    name="WeatherAgent",
    tools=weather_function,  # Automatically real or mock
)
```

**At startup, you'll see:**
```
🌤️  Weather data: Using real-time weather data
   OR
🌤️  Weather data: Using mock weather data
💡 Tip: Set OPENWEATHER_API_KEY in .env for real weather data
   Get free API key at: https://openweathermap.org/api
```

---

## 📝 Samples Using Real Weather

### Currently Integrated:
- ✅ `azure_ai_basic_devui.py` - DevUI version with real weather
- ✅ `devui_agents/weather_agent/agent.py` - Directory-based agent

### Easy to Add to Other Samples:

```python
# In any sample file:
from shared_utils import get_real_weather, get_mock_weather
import os

# Choose based on API key availability
has_api_key = bool(os.environ.get("OPENWEATHER_API_KEY"))
weather_func = get_real_weather if has_api_key else get_mock_weather

# Use in your agent
agent = ChatAgent(
    chat_client=client,
    tools=weather_func,
    name="WeatherBot"
)
```

---

## 🎯 Use Cases

### 1. Development & Testing
```bash
# No API key needed
python azure_ai_basic_devui.py --test
# Uses mock data automatically
```

### 2. Demo & Production
```bash
# Add API key for real data
OPENWEATHER_API_KEY=your_key python azure_ai_basic_devui.py
# Shows actual current weather
```

### 3. Testing Different Cities
```python
# Works with any city worldwide
test_cities = ["Seattle", "Tokyo", "London", "Mumbai", "São Paulo"]
for city in test_cities:
    weather = get_real_weather(city)
    print(weather)
```

---

## 🌍 Supported Locations

OpenWeatherMap supports:
- ✅ **200,000+ cities** worldwide
- ✅ City names (e.g., "Seattle")
- ✅ City + country (e.g., "Seattle,US")
- ✅ City + state (e.g., "Seattle,WA,US")
- ✅ Coordinates (lat,lon)
- ✅ ZIP codes (US only)

**Examples:**
```python
get_real_weather("New York")
get_real_weather("New York,US")
get_real_weather("Paris,FR")
get_real_weather("東京")  # Tokyo in Japanese
```

---

## 🛡️ Error Handling

The `get_real_weather` function handles all common errors gracefully:

### No API Key
```
❌ OpenWeatherMap API key not found.
Please set OPENWEATHER_API_KEY in your .env file.
Get a free API key at: https://openweathermap.org/api
```

### Invalid City
```
❌ Location 'Nonexistentville' not found.
Please check the spelling or try a different city name.
```

### Invalid API Key
```
❌ Invalid API key.
Please check your OPENWEATHER_API_KEY in .env file.
```

### Network Error
```
❌ Network error while fetching weather data: Connection timeout
```

**Agent handles these gracefully** and can inform users appropriately.

---

## 📊 API Rate Limits

### Free Tier:
- **1,000 calls/day** (plenty for development)
- **60 calls/minute**
- Current weather only
- No credit card required

### If You Hit Limits:
The function will return an error message, and the agent can inform the user.

### Best Practices:
- ✅ Cache results for repeated queries
- ✅ Use mock data for automated tests
- ✅ Consider upgrading for production apps

---

## 🔍 Advanced Configuration

### Custom Error Messages

Edit `shared_utils.py` to customize error responses:

```python
def get_real_weather(location: str) -> str:
    if not api_key:
        return "Weather service is temporarily unavailable."
    # ... rest of function
```

### Add More Weather Details

The API returns much more data. Edit the function to include:

```python
# In shared_utils.py, add to the response:
pressure = data["main"]["pressure"]
visibility = data.get("visibility", 0) / 1000  # Convert to km
clouds = data["clouds"]["all"]

weather_info = (
    f"🌤️ Weather in {city_name}, {country}:\n"
    f"🌡️ Temperature: {temp_celsius:.1f}°C ({temp_fahrenheit:.1f}°F)\n"
    f"🤔 Feels like: {feels_like:.1f}°C\n"
    f"☁️ Conditions: {description.capitalize()}\n"
    f"☁️ Cloud cover: {clouds}%\n"
    f"💧 Humidity: {humidity}%\n"
    f"💨 Wind: {wind_speed:.1f} m/s\n"
    f"🔭 Visibility: {visibility:.1f} km\n"
    f"🎈 Pressure: {pressure} hPa"
)
```

---

## 🎓 Technical Details

### Dependencies

The `shared_utils.py` module requires:
```bash
pip install httpx  # For HTTP requests
pip install pydantic  # For type annotations
```

These are already included in the agent framework dependencies.

### API Endpoint

```python
base_url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    "q": location,
    "appid": api_key,
    "units": "metric"  # Celsius
}
```

### Response Format

```json
{
  "name": "Seattle",
  "sys": {"country": "US"},
  "main": {
    "temp": 15.3,
    "feels_like": 14.2,
    "humidity": 67
  },
  "weather": [
    {"description": "partly cloudy"}
  ],
  "wind": {"speed": 3.5}
}
```

---

## 🐛 Troubleshooting

### "API key not found" but I set it

**Solution:** Make sure to restart your Python session:
```bash
# Stop the agent (Ctrl+C)
# Verify .env has the key
cat .env | grep OPENWEATHER_API_KEY
# Restart
python azure_ai_basic_devui.py
```

### "Invalid API key" error

**Solution:** 
1. Check for extra spaces in .env: `OPENWEATHER_API_KEY=abc123` (no quotes needed)
2. Verify key is active in your OpenWeatherMap account
3. New keys may take 10-15 minutes to activate

### Still using mock data

**Solution:**
```bash
# Check if key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENWEATHER_API_KEY'))"
```

---

## 📚 Learn More

### OpenWeatherMap Documentation:
- [API Documentation](https://openweathermap.org/api)
- [Current Weather API](https://openweathermap.org/current)
- [API Response Format](https://openweathermap.org/current#current_JSON)

### Related Files:
- `shared_utils.py` - Weather functions implementation
- `azure_ai_basic_devui.py` - Example usage
- `.env` - Configuration file

---

## 🎉 Summary

**To use real weather data:**
```bash
# 1. Get free API key from openweathermap.org
# 2. Add to .env
echo "OPENWEATHER_API_KEY=your_key_here" >> .env
# 3. Run any sample
python azure_ai_basic_devui.py
```

**Benefits:**
- ✅ Real, accurate weather data
- ✅ 200,000+ cities worldwide
- ✅ Automatic fallback to mock data
- ✅ Works with all samples
- ✅ Free tier (1,000 calls/day)

**No API key?** No problem! Mock data works perfectly for testing and learning.

---

**Questions?** The agent can handle both real and mock data gracefully, so you can start using it immediately! 🚀
