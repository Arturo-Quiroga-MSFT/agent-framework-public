"""Test with api-version 2025-05-15-preview + type field in agent reference."""
import os
from azure.identity import DefaultAzureCredential
import requests

credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default")

endpoint = "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
api_version = "2025-05-15-preview"

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json",
}

# Test different type values for the agent reference
type_values = ["agent", "hosted_agent", "application", "agent_reference", "hosted"]

for type_val in type_values:
    payload = {
        "model": "gpt-4.1",
        "input": "What is the weather in Seattle?",
        "agent": {
            "type": type_val,
            "name": "WeatherAgent",
            "version": "2"
        }
    }
    url = f"{endpoint}/openai/responses?api-version={api_version}"
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    try:
        err = resp.json().get("error", {}).get("message", "")[:120]
    except:
        err = resp.text[:120]
    print(f'type="{type_val}": {resp.status_code} - {err}')
    if resp.status_code == 200:
        print(f"  SUCCESS! Full response: {resp.json()}")
        break
