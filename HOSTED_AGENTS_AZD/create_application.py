#!/usr/bin/env python3
"""
Create the missing Application + agentDeployment resources for contoso-support-agent.

The 'azd deploy' created the agent version and started the container, but did NOT
create the ARM-level Application resource which provides the routing entry.
This script creates that.
"""
import subprocess
import json
import sys

SUBSCRIPTION = "7a28b21e-0d3e-4435-a686-d92889d4ee96"
RG = "aq-foundry-rg"
ACCOUNT = "r2d2-foundry-001"
PROJECT = "Main-Project"
AGENT_NAME = "contoso-support-agent"
AGENT_VERSION = "3"
API_VERSION = "2025-10-01-preview"

BASE_URL = f"https://management.azure.com/subscriptions/{SUBSCRIPTION}/resourceGroups/{RG}/providers/Microsoft.CognitiveServices/accounts/{ACCOUNT}/projects/{PROJECT}"


def get_token():
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://management.azure.com", "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def arm_request(method, path, body=None):
    url = f"{BASE_URL}/{path}?api-version={API_VERSION}"
    token = get_token()
    cmd = ["curl", "-sS", "-X", method, url,
           "-H", f"Authorization: Bearer {token}",
           "-H", "Content-Type: application/json"]
    if body:
        cmd += ["-d", json.dumps(body)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\n{method} {path}")
    try:
        parsed = json.loads(result.stdout)
        print(json.dumps(parsed, indent=2))
        return parsed
    except json.JSONDecodeError:
        print(f"Raw: {result.stdout}")
        return None


def main():
    # Step 1: Create Application
    print("=" * 60)
    print("STEP 1: Create Application resource")
    print("=" * 60)
    app_body = {
        "properties": {
            "displayName": AGENT_NAME,
            "agents": [
                {
                    "agentName": AGENT_NAME
                }
            ],
            "authorizationPolicy": {
                "authorizationScheme": "Default"
            }
        }
    }
    result = arm_request("PUT", f"applications/{AGENT_NAME}", app_body)
    if result and "error" in result:
        print(f"\nFailed to create application: {result['error']['message']}")
        sys.exit(1)

    # Step 2: Create agentDeployment
    print("\n" + "=" * 60)
    print("STEP 2: Create agentDeployment")
    print("=" * 60)
    deploy_body = {
        "properties": {
            "displayName": f"{AGENT_NAME}-deployment",
            "protocols": [
                {
                    "protocol": "Responses",
                    "version": "v1"
                }
            ],
            "agents": [
                {
                    "agentName": AGENT_NAME,
                    "agentVersion": AGENT_VERSION
                }
            ],
            "deploymentType": "Hosted",
            "minReplicas": 1,
            "maxReplicas": 3
        }
    }
    result = arm_request("PUT", f"applications/{AGENT_NAME}/agentDeployments/{AGENT_NAME}-deployment", deploy_body)
    if result and "error" in result:
        print(f"\nFailed to create deployment: {result['error']['message']}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("DONE! Application and deployment created.")
    print("Wait ~30 seconds, then test invocation.")
    print("=" * 60)


if __name__ == "__main__":
    main()
