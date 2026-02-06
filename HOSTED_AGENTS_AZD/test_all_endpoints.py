#!/usr/bin/env python3
"""
Test all possible invocation patterns for the hosted agent.
The Application resource is now created. This tests various endpoint/format combinations.
"""
import subprocess
import json
import requests

AGENT_NAME = "contoso-support-agent"
PROJECT_ENDPOINT = "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"


def get_ai_token():
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://ai.azure.com", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_cogservices_token():
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://cognitiveservices.azure.com", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def test_endpoint(name, url, token, body):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"URL: {url}")
    print(f"Body: {json.dumps(body, indent=2)}")
    print(f"{'='*60}")
    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=60,
        )
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            if resp.status_code == 200:
                # Try to find output text
                output_text = data.get("output_text", "")
                if not output_text and "output" in data:
                    for item in data["output"]:
                        if item.get("type") == "message":
                            for c in item.get("content", []):
                                if c.get("type") == "output_text":
                                    output_text = c.get("text", "")
                                    break
                        if not output_text:
                            output_text = item.get("content", str(item))[:200]
                print(f"SUCCESS! Output: {output_text[:300]}")
            else:
                print(f"Error: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Raw: {resp.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")


def main():
    ai_token = get_ai_token()
    cog_token = get_cogservices_token()
    print(f"Got tokens (ai: {len(ai_token)} chars, cog: {len(cog_token)} chars)")

    api_version = "2025-05-15-preview"

    # Test 1: OpenAI-style /openai/responses with agent reference (ai.azure.com token)
    test_endpoint(
        "OpenAI /responses + agent ref (ai.azure.com token)",
        f"{PROJECT_ENDPOINT}/openai/responses?api-version={api_version}",
        ai_token,
        {
            "input": "Hello, what products do you carry?",
            "stream": False,
            "agent": {"name": AGENT_NAME, "type": "agent_reference"},
        },
    )

    # Test 2: Same but with cognitiveservices token
    test_endpoint(
        "OpenAI /responses + agent ref (cognitiveservices token)",
        f"{PROJECT_ENDPOINT}/openai/responses?api-version={api_version}",
        cog_token,
        {
            "input": "Hello, what products do you carry?",
            "stream": False,
            "agent": {"name": AGENT_NAME, "type": "agent_reference"},
        },
    )

    # Test 3: Application-specific endpoint
    test_endpoint(
        "Application-specific /responses endpoint",
        f"{PROJECT_ENDPOINT}/applications/{AGENT_NAME}/responses?api-version={api_version}",
        ai_token,
        {
            "input": "Hello, what products do you carry?",
            "stream": False,
        },
    )

    # Test 4: Project /responses endpoint (not /openai/responses)
    test_endpoint(
        "Project /responses (not /openai/)",
        f"{PROJECT_ENDPOINT}/responses?api-version={api_version}",
        ai_token,
        {
            "input": "Hello, what products do you carry?",
            "stream": False,
            "agent": {"name": AGENT_NAME, "type": "agent_reference"},
        },
    )

    # Test 5: Agent-specific /responses
    test_endpoint(
        "Agent-specific /agents/{name}/responses",
        f"{PROJECT_ENDPOINT}/agents/{AGENT_NAME}/responses?api-version={api_version}",
        ai_token,
        {
            "input": "Hello, what products do you carry?",
            "stream": False,
        },
    )

    # Test 6: /openai/responses with model field set to agent name
    test_endpoint(
        "/openai/responses with model=agent_name",
        f"{PROJECT_ENDPOINT}/openai/responses?api-version={api_version}",
        ai_token,
        {
            "input": "Hello, what products do you carry?",
            "stream": False,
            "model": AGENT_NAME,
        },
    )


if __name__ == "__main__":
    main()
