"""
Autonomous Agent Example - Client Credentials Flow
Date: January 19, 2026

Demonstrates:
- Client credentials authentication (autonomous agent)
- Token acquisition and caching
- Azure Storage access without user interaction
- Error handling and token refresh
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
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


class AutonomousAgent:
    """
    An autonomous agent that operates without user interaction.
    Uses client credentials (service principal) for authentication.
    """
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize autonomous agent.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Agent's client ID (app registration)
            client_secret: Agent's client secret
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        
        # Create credential
        with AuthErrorContext("Agent Initialization"):
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        
        print(f"\n{'='*60}")
        print(f"Autonomous Agent (Client Credentials)")
        print(f"{'='*60}")
        print(f"Agent ID: {client_id}")
        print(f"{'='*60}\n")
    
    def get_access_token(self, scope: str) -> str:
        """
        Acquire access token for a specific scope.
        
        Args:
            scope: OAuth scope (e.g., "https://storage.azure.com/.default")
            
        Returns:
            Access token string
        """
        with AuthErrorContext(f"Token Acquisition for {scope}"):
            try:
                token_result = self.credential.get_token(scope)
                token = token_result.token
                
                # Validate the token
                validator = TokenValidator(self.tenant_id)
                claims = validator.get_token_claims(token)
                
                print(f"✓ Token acquired for: {claims.get('appid')}")
                print(f"  Expires: {datetime.fromtimestamp(token_result.expires_on)}")
                
                # Verify it's an agent token
                if not validator.validate_agent_identity(token):
                    print(f"⚠ Warning: Token does not represent an agent identity!")
                
                return token
                
            except ClientAuthenticationError as e:
                auth_error = handle_auth_error(e, "Token acquisition")
                raise auth_error
    
    def access_storage(self, storage_account_name: str, container_name: str) -> list:
        """
        Access Azure Storage using agent identity.
        
        Args:
            storage_account_name: Storage account name
            container_name: Container name
            
        Returns:
            List of blob names
        """
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        with AuthErrorContext("Storage Access"):
            try:
                # BlobServiceClient uses the credential automatically
                blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=self.credential
                )
                
                # Get or create container
                container_client = blob_service_client.get_container_client(container_name)
                
                # Try to create container if it doesn't exist
                try:
                    container_client.create_container()
                    print(f"✓ Created new container: {container_name}")
                except Exception as e:
                    if "ContainerAlreadyExists" in str(e):
                        print(f"✓ Container exists: {container_name}")
                    else:
                        pass  # Ignore other container creation messages
                
                # List blobs in container
                blobs = []
                
                for blob in container_client.list_blobs():
                    blobs.append(blob.name)
                    print(f"  - {blob.name} ({blob.size} bytes)")
                
                print(f"✓ Found {len(blobs)} blobs")
                return blobs
                
            except HttpResponseError as e:
                if e.status_code == 403:
                    logger.error(
                        f"Agent does not have permission to access storage.\n"
                        f"Required role: 'Storage Blob Data Reader' or similar\n"
                        f"Assign with: az role assignment create "
                        f"--assignee {self.client_id} "
                        f"--role 'Storage Blob Data Reader' "
                        f"--scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
                    )
                auth_error = handle_auth_error(e, "Storage access")
                raise auth_error
    
    def demonstrate_token_refresh(self):
        """
        Demonstrate automatic token refresh.
        The Azure Identity SDK handles token caching and refresh automatically.
        """
        scope = "https://management.azure.com/.default"
        
        # First token acquisition
        print("Acquiring first token...")
        token1 = self.get_access_token(scope)
        
        # Check if token is cached
        print("Acquiring second token (should use cache)...")
        token2 = self.get_access_token(scope)
        
        if token1 == token2:
            print("✓ Token was reused from cache")
        else:
            print("✗ New token was acquired")
        
        # Validate token
        validator = TokenValidator(self.tenant_id)
        if not validator.is_token_expired(token1):
            print("✓ Token is still valid")
        else:
            print("✗ Token is expired (will be refreshed automatically)")


def main():
    """Main execution function."""
    
    # Load environment variables
    load_dotenv()
    
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("AGENT_CLIENT_ID")
    client_secret = os.getenv("AGENT_CLIENT_SECRET")
    storage_account = os.getenv("STORAGE_ACCOUNT_NAME")
    container_name = os.getenv("STORAGE_CONTAINER_NAME", "test-container")
    
    # Validate configuration
    if not all([tenant_id, client_id, client_secret]):
        print("ERROR: Missing required environment variables!")
        print("Please create .env file with:")
        print("  TENANT_ID")
        print("  AGENT_CLIENT_ID")
        print("  AGENT_CLIENT_SECRET")
        print("See .env.example for template.")
        return 1
    
    try:
        # Create autonomous agent
        agent = AutonomousAgent(tenant_id, client_id, client_secret)
        
        # Demo 1: Acquire token for Azure Management API
        print(f"\n{'='*60}")
        print(f"DEMO 1: Azure Management Token")
        print(f"{'='*60}")
        mgmt_token = agent.get_access_token("https://management.azure.com/.default")
        
        # Demo 2: Access Azure Storage (if configured)
        if storage_account:
            print(f"\n{'='*60}")
            print(f"DEMO 2: Azure Storage Access")
            print(f"{'='*60}")
            print(f"Storage account: {storage_account}")
            print(f"Container: {container_name}")
            try:
                blobs = agent.access_storage(storage_account, container_name)
            except Exception as e:
                print(f"⚠ Storage access failed: {e}")
                print("To enable storage demo, configure STORAGE_ACCOUNT_NAME and permissions")
        else:
            print(f"\n{'='*60}")
            print(f"DEMO 2: Skipped (no storage account configured)")
            print(f"{'='*60}")
        
        # Demo 3: Token refresh behavior
        print(f"\n{'='*60}")
        print(f"DEMO 3: Token Refresh and Caching")
        print(f"{'='*60}")
        agent.demonstrate_token_refresh()
        
        print(f"\n{'='*60}")
        print(f"ALL DEMOS COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        return 0
        
    except Exception as e:
        print(f"ERROR: Demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
