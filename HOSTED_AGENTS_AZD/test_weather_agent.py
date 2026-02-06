"""Test if WeatherAgent (existing app) works with same invocation pattern."""
import os
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default")

endpoint = "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=token.token,
    api_version="2025-05-01-preview",
)

# Test 1: Invoke WeatherAgent with AgentReference
print("=" * 60)
print("TEST 1: WeatherAgent via extra_body agent reference")
print("=" * 60)
try:
    response = client.responses.create(
        model="gpt-4.1",
        input="What is the weather in Seattle?",
        extra_body={
            "agent": {
                "name": "WeatherAgent",
                "version": "2"
            }
        }
    )
    print(f"SUCCESS! Response ID: {response.id}")
    for item in response.output:
        if hasattr(item, 'content'):
            for c in item.content:
                if hasattr(c, 'text'):
                    print(f"Text: {c.text[:200]}")
except Exception as e:
    print(f"FAILED: {e}")

# Test 2: Invoke contoso-support-agent with same pattern
print("\n" + "=" * 60)
print("TEST 2: contoso-support-agent via extra_body agent reference")
print("=" * 60)
try:
    response = client.responses.create(
        model="gpt-4.1",
        input="What is the status of order 12345?",
        extra_body={
            "agent": {
                "name": "contoso-support-agent",
                "version": "3"
            }
        }
    )
    print(f"SUCCESS! Response ID: {response.id}")
    for item in response.output:
        if hasattr(item, 'content'):
            for c in item.content:
                if hasattr(c, 'text'):
                    print(f"Text: {c.text[:200]}")
except Exception as e:
    print(f"FAILED: {e}")

# Test 3: contoso-support-agent WITHOUT version
print("\n" + "=" * 60)
print("TEST 3: contoso-support-agent without version")
print("=" * 60)
try:
    response = client.responses.create(
        model="gpt-4.1",
        input="What is the status of order 12345?",
        extra_body={
            "agent": {
                "name": "contoso-support-agent"
            }
        }
    )
    print(f"SUCCESS! Response ID: {response.id}")
    for item in response.output:
        if hasattr(item, 'content'):
            for c in item.content:
                if hasattr(c, 'text'):
                    print(f"Text: {c.text[:200]}")
except Exception as e:
    print(f"FAILED: {e}")
