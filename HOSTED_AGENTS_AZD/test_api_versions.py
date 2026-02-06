"""Test different API versions for agent invocation."""
import os
from azure.identity import DefaultAzureCredential
import requests

credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default")

endpoint = "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"

api_versions = [
    "2025-03-01-preview",
    "2025-04-01-preview",
    "2025-04-14",
    "2025-05-01-preview",
    "2025-05-15-preview",
    "2025-06-01-preview",
    "2025-01-01-preview",
    "2024-12-01-preview",
]

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json",
}

payload = {
    "model": "gpt-4.1",
    "input": "Hello",
    "agent": {
        "name": "WeatherAgent",
        "version": "2"
    }
}

for api_version in api_versions:
    url = f"{endpoint}/openai/responses?api-version={api_version}"
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    status = resp.status_code
    # Get short error message
    try:
        err = resp.json().get("error", {}).get("message", "")[:80]
    except:
        err = resp.text[:80]
    print(f"API {api_version}: {status} - {err}")
