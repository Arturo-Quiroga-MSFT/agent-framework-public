#!/usr/bin/env python3
"""Test invoking the azd-deployed hosted agent."""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

ENDPOINT = "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
AGENT_NAME = "contoso-support-agent"


def main():
    client = AIProjectClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())
    openai_client = client.get_openai_client()

    print(f"1) OpenAI base_url: {openai_client.base_url}")

    # Check if conversations API exists
    has_conversations = hasattr(openai_client, "conversations")
    print(f"2) Has conversations API: {has_conversations}")

    # Sanity check: direct model call works?
    print("\n=== TEST 1: Direct model call (no agent) ===")
    try:
        resp = openai_client.responses.create(
            input="Say hi in one word",
            model="gpt-4.1",
            stream=False,
        )
        print(f"OK: {resp.output_text[:100]}")
    except Exception as e:
        print(f"FAIL: {e}")

    # Test 2: With conversation + agent reference
    if has_conversations:
        print("\n=== TEST 2: With conversation + agent reference ===")
        try:
            conv = openai_client.conversations.create()
            print(f"Conversation created: {conv.id}")
            resp = openai_client.responses.create(
                input="Hello! What products do you carry?",
                conversation=conv.id,
                stream=False,
                extra_body={"agent": {"name": AGENT_NAME, "type": "agent_reference"}},
            )
            print(f"OK: {resp.output_text[:200]}")
        except Exception as e:
            print(f"FAIL: {e}")

    # Test 3: Without conversation
    print("\n=== TEST 3: Without conversation, agent reference ===")
    try:
        resp = openai_client.responses.create(
            input="Hello! What products do you carry?",
            stream=False,
            extra_body={"agent": {"name": AGENT_NAME, "type": "agent_reference"}},
        )
        print(f"OK: {resp.output_text[:200]}")
    except Exception as e:
        print(f"FAIL: {e}")

    # Test 4: agent name with version
    print("\n=== TEST 4: Agent name with version ===")
    try:
        resp = openai_client.responses.create(
            input="Hello!",
            stream=False,
            extra_body={"agent": {"name": f"{AGENT_NAME}:3", "type": "agent_reference"}},
        )
        print(f"OK: {resp.output_text[:200]}")
    except Exception as e:
        print(f"FAIL: {e}")


if __name__ == "__main__":
    main()
