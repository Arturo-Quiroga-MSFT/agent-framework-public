"""Fix the Application's trafficRoutingPolicy to point to the actual deployment."""
import requests
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default")

sub = "7a28b21e-0d3e-4435-a686-d92889d4ee96"
rg = "aq-foundry-rg"
account = "r2d2-foundry-001"
project = "Main-Project"
app_name = "contoso-support-agent"
deployment_id = "beec5741-387a-4d2b-bbd1-46ee2130ad9a"

base = f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}"
api = "api-version=2025-10-01-preview"

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json",
}

# Step 1: Get current application
print("Step 1: Getting current application config...")
resp = requests.get(f"{base}/applications/{app_name}?{api}", headers=headers)
app = resp.json()
print(f"  Current routing deploymentId: '{app['properties']['trafficRoutingPolicy']['rules'][0]['deploymentId']}'")

# Step 2: Update the trafficRoutingPolicy with the correct deploymentId
print(f"\nStep 2: Updating trafficRoutingPolicy with deploymentId={deployment_id}...")
app["properties"]["trafficRoutingPolicy"]["rules"][0]["deploymentId"] = deployment_id

resp = requests.put(
    f"{base}/applications/{app_name}?{api}",
    headers=headers,
    json=app,
)
print(f"  PUT status: {resp.status_code}")
if resp.status_code in (200, 201):
    updated = resp.json()
    new_id = updated["properties"]["trafficRoutingPolicy"]["rules"][0]["deploymentId"]
    print(f"  Updated routing deploymentId: '{new_id}'")
    print(f"  Blueprint identity state: {updated['properties']['agentIdentityBlueprint']['provisioningState']}")
    print(f"  Instance identity state: {updated['properties']['defaultInstanceIdentity']['provisioningState']}")
else:
    print(f"  Error: {resp.text[:500]}")
