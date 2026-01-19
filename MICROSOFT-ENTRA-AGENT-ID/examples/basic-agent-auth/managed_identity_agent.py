"""
Managed Identity Agent Example
Date: January 19, 2026

Demonstrates:
- Managed identity authentication (Azure-hosted agents)
- Zero configuration credential management
- System-assigned vs user-assigned identities
- Automatic credential rotation
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError

from utils.token_validator import TokenValidator
from utils.error_handler import handle_auth_error, AuthErrorContext

# Configure logging - reduce verbosity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Silence verbose loggers
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
logging.getLogger('azure.identity').setLevel(logging.WARNING)
logging.getLogger('utils.error_handler').setLevel(logging.WARNING)
logging.getLogger('utils.token_validator').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ManagedIdentityAgent:
    """
    An agent running in Azure that uses managed identity.
    No credentials needed - Azure manages authentication automatically.
    """
    
    def __init__(self, client_id: str = None):
        """
        Initialize managed identity agent.
        
        Args:
            client_id: Optional client ID for user-assigned managed identity.
                      If None, uses system-assigned managed identity.
        """
        self.client_id = client_id
        
        with AuthErrorContext("Managed Identity Initialization"):
            if client_id:
                logger.info(f"Using user-assigned managed identity: {client_id}")
                self.credential = ManagedIdentityCredential(client_id=client_id)
            else:
                logger.info("Using system-assigned managed identity")
                self.credential = ManagedIdentityCredential()
        
        logger.info("Managed identity agent initialized")
    
    def get_access_token(self, scope: str) -> str:
        """
        Acquire access token using managed identity.
        
        Args:
            scope: OAuth scope (e.g., "https://storage.azure.com/.default")
            
        Returns:
            Access token string
        """
        with AuthErrorContext(f"Token Acquisition for {scope}"):
            try:
                token_result = self.credential.get_token(scope)
                token = token_result.token
                
                logger.info(f"Token acquired via managed identity")
                logger.info(f"Token expires at: {datetime.fromtimestamp(token_result.expires_on)}")
                
                return token
                
            except ClientAuthenticationError as e:
                logger.error(
                    "Managed identity authentication failed.\n"
                    "Common causes:\n"
                    "  1. Not running in Azure environment\n"
                    "  2. Managed identity not enabled on resource\n"
                    "  3. Wrong client_id for user-assigned identity\n"
                    "  4. IMDS endpoint not accessible"
                )
                auth_error = handle_auth_error(e, "Managed identity token acquisition")
                raise auth_error
    
    def access_azure_resources(self, subscription_id: str = None):
        """
        Access Azure resources using managed identity.
        
        Args:
            subscription_id: Optional subscription ID
        """
        with AuthErrorContext("Azure Resource Access"):
            try:
                # Get subscription ID if not provided
                if not subscription_id:
                    import subprocess
                    result = subprocess.run(
                        ["az", "account", "show", "--query", "id", "-o", "tsv"],
                        capture_output=True,
                        text=True
                    )
                    subscription_id = result.stdout.strip()
                
                # Create resource management client
                resource_client = ResourceManagementClient(
                    credential=self.credential,
                    subscription_id=subscription_id
                )
                
                # List resource groups
                logger.info(f"\n=== Resource Groups in Subscription {subscription_id[:8]}... ===")
                rg_count = 0
                for rg in resource_client.resource_groups.list():
                    logger.info(f"  - {rg.name} ({rg.location})")
                    rg_count += 1
                
                logger.info(f"\n✓ Successfully accessed {rg_count} resource groups")
                
            except HttpResponseError as e:
                if e.status_code == 403:
                    logger.error(
                        "Managed identity does not have permission to list resource groups.\n"
                        "Required: 'Reader' role or higher at subscription/resource group level"
                    )
                auth_error = handle_auth_error(e, "Resource access")
                raise auth_error
    
    def demonstrate_zero_config(self):
        """
        Demonstrate the advantage of managed identity - zero configuration.
        """
        logger.info("\n=== Zero Configuration Demo ===")
        logger.info("\n✓ Managed Identity Advantages:")
        logger.info("  1. No credentials to manage")
        logger.info("  2. No secrets in code or configuration")
        logger.info("  3. Automatic credential rotation by Azure")
        logger.info("  4. Works across all Azure services")
        logger.info("  5. Audit trail automatically maintained")
        
        logger.info("\n=== Comparing Authentication Methods ===")
        logger.info("\nClient Secret (Autonomous Agent):")
        logger.info("  ❌ Must store client secret securely")
        logger.info("  ❌ Must rotate secrets manually")
        logger.info("  ❌ Risk of secret exposure")
        logger.info("  ✓ Works anywhere (not just Azure)")
        
        logger.info("\nManaged Identity:")
        logger.info("  ✓ No secrets to manage")
        logger.info("  ✓ Automatic rotation")
        logger.info("  ✓ Zero configuration")
        logger.info("  ❌ Only works in Azure")


class DefaultCredentialAgent:
    """
    Agent using DefaultAzureCredential - works in any environment.
    Tries multiple authentication methods in order:
    1. Environment variables
    2. Managed identity
    3. Visual Studio Code
    4. Azure CLI
    5. Azure PowerShell
    """
    
    def __init__(self):
        """Initialize agent with DefaultAzureCredential."""
        with AuthErrorContext("Default Credential Initialization"):
            self.credential = DefaultAzureCredential()
        
        logger.info("DefaultAzureCredential agent initialized")
        logger.info("Will try: Environment → Managed Identity → CLI → ...")
    
    def get_access_token(self, scope: str) -> str:
        """
        Acquire access token using first available credential.
        
        Args:
            scope: OAuth scope
            
        Returns:
            Access token string
        """
        with AuthErrorContext(f"Default Credential Token Acquisition"):
            try:
                token_result = self.credential.get_token(scope)
                token = token_result.token
                
                logger.info(f"✓ Token acquired via DefaultAzureCredential")
                
                # Try to determine which method was used
                # (This is approximate - DefaultAzureCredential doesn't expose this)
                if os.getenv("AZURE_CLIENT_ID"):
                    logger.info("  Likely method: Environment variables")
                elif self._is_running_in_azure():
                    logger.info("  Likely method: Managed identity")
                else:
                    logger.info("  Likely method: Azure CLI or VS Code")
                
                return token
                
            except ClientAuthenticationError as e:
                logger.error(
                    "All credential methods failed.\n"
                    "Try one of:\n"
                    "  1. Set environment variables (AZURE_CLIENT_ID, etc.)\n"
                    "  2. Run in Azure with managed identity\n"
                    "  3. Login with: az login"
                )
                auth_error = handle_auth_error(e, "Default credential")
                raise auth_error
    
    def _is_running_in_azure(self) -> bool:
        """Check if running in Azure environment."""
        # Check for IMDS endpoint (managed identity)
        try:
            import requests
            response = requests.get(
                "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
                headers={"Metadata": "true"},
                timeout=2
            )
            return response.status_code == 200
        except:
            return False


def main():
    """Main execution function."""
    
    load_dotenv()
    
    # Check environment
    is_azure = os.path.exists("/var/lib/waagent") or os.environ.get("MSI_ENDPOINT")
    
    try:
        logger.info("=== Managed Identity Agent Demo ===\n")
        
        if is_azure:
            logger.info("✓ Detected Azure environment")
            
            # Demo 1: System-assigned managed identity
            logger.info("\n--- Demo 1: System-Assigned Managed Identity ---")
            agent = ManagedIdentityAgent()
            token = agent.get_access_token("https://management.azure.com/.default")
            logger.info(f"✓ Token acquired (length: {len(token)})")
            
            # Demo 2: Access Azure resources
            logger.info("\n--- Demo 2: Access Azure Resources ---")
            agent.access_azure_resources()
            
            # Demo 3: Zero config advantage
            logger.info("\n--- Demo 3: Zero Configuration ---")
            agent.demonstrate_zero_config()
            
        else:
            logger.info("⚠ Not running in Azure environment")
            logger.info("Falling back to DefaultAzureCredential")
            
            # Demo: DefaultAzureCredential
            logger.info("\n--- DefaultAzureCredential Demo ---")
            agent = DefaultCredentialAgent()
            token = agent.get_access_token("https://management.azure.com/.default")
            logger.info(f"✓ Token acquired (length: {len(token)})")
            
            logger.info("\n=== How to Enable Managed Identity ===")
            logger.info("\nFor Azure VM:")
            logger.info("  az vm identity assign --name <vm-name> --resource-group <rg>")
            
            logger.info("\nFor Azure App Service:")
            logger.info("  az webapp identity assign --name <app-name> --resource-group <rg>")
            
            logger.info("\nFor Azure Container Instance:")
            logger.info("  az container create ... --assign-identity")
            
            logger.info("\nFor Azure Function:")
            logger.info("  az functionapp identity assign --name <func-name> --resource-group <rg>")
        
        logger.info("\n=== All demos completed successfully ===")
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
