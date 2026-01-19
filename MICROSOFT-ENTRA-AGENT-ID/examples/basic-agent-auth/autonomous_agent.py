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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        
        logger.info(f"Autonomous agent initialized: {client_id}")
    
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
                
                # Log token metadata (never log the actual token!)
                logger.info(f"Token acquired successfully")
                logger.info(f"Token expires at: {datetime.fromtimestamp(token_result.expires_on)}")
                
                # Validate the token
                validator = TokenValidator(self.tenant_id)
                claims = validator.get_token_claims(token)
                
                logger.info(f"Token issued for: {claims.get('appid')}")
                logger.info(f"Token roles: {claims.get('roles', [])}")
                
                # Verify it's an agent token
                if not validator.validate_agent_identity(token):
                    logger.warning("Token does not represent an agent identity!")
                
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
                
                # List blobs in container
                container_client = blob_service_client.get_container_client(container_name)
                blobs = []
                
                logger.info(f"Listing blobs in container: {container_name}")
                for blob in container_client.list_blobs():
                    blobs.append(blob.name)
                    logger.info(f"  - {blob.name} ({blob.size} bytes)")
                
                logger.info(f"Found {len(blobs)} blobs")
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
        logger.info("\n=== Token Refresh Demo ===")
        
        scope = "https://management.azure.com/.default"
        
        # First token acquisition
        logger.info("Acquiring first token...")
        token1 = self.get_access_token(scope)
        
        # Check if token is cached
        logger.info("Acquiring second token (should use cache)...")
        token2 = self.get_access_token(scope)
        
        if token1 == token2:
            logger.info("✓ Token was reused from cache")
        else:
            logger.info("✗ New token was acquired")
        
        # Validate token
        validator = TokenValidator(self.tenant_id)
        if not validator.is_token_expired(token1):
            logger.info("✓ Token is still valid")
        else:
            logger.info("✗ Token is expired (will be refreshed automatically)")


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
        logger.error(
            "Missing required environment variables!\n"
            "Please create .env file with:\n"
            "  TENANT_ID\n"
            "  AGENT_CLIENT_ID\n"
            "  AGENT_CLIENT_SECRET\n"
            "See .env.example for template."
        )
        return 1
    
    try:
        logger.info("=== Autonomous Agent Demo ===\n")
        
        # Create autonomous agent
        agent = AutonomousAgent(tenant_id, client_id, client_secret)
        
        # Demo 1: Acquire token for Azure Management API
        logger.info("\n--- Demo 1: Azure Management Token ---")
        mgmt_token = agent.get_access_token("https://management.azure.com/.default")
        logger.info(f"✓ Management token acquired (length: {len(mgmt_token)})")
        
        # Demo 2: Access Azure Storage (if configured)
        if storage_account:
            logger.info("\n--- Demo 2: Azure Storage Access ---")
            try:
                blobs = agent.access_storage(storage_account, container_name)
                logger.info(f"✓ Successfully accessed storage: {len(blobs)} blobs found")
            except Exception as e:
                logger.warning(f"Storage access demo skipped: {e}")
                logger.info("To enable storage demo, configure STORAGE_ACCOUNT_NAME")
        else:
            logger.info("\n--- Demo 2: Skipped (no storage account configured) ---")
        
        # Demo 3: Token refresh behavior
        logger.info("\n--- Demo 3: Token Refresh ---")
        agent.demonstrate_token_refresh()
        
        logger.info("\n=== All demos completed successfully ===")
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
