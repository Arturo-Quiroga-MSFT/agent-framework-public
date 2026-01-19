"""
Interactive Agent Example - Authorization Code Flow
Date: January 19, 2026

Demonstrates:
- Interactive authentication with user consent
- Delegated permissions (user context)
- Device code flow (for headless environments)
- Browser-based authentication
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential, DeviceCodeCredential
from azure.core.exceptions import ClientAuthenticationError
from microsoft.graph import GraphServiceClient

from utils.token_validator import TokenValidator
from utils.error_handler import handle_auth_error, AuthErrorContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InteractiveAgent:
    """
    An agent that operates with user context (delegated permissions).
    Requires user authentication and consent.
    """
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        use_device_code: bool = False
    ):
        """
        Initialize interactive agent.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Agent's client ID (app registration)
            use_device_code: Use device code flow instead of browser
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        
        with AuthErrorContext("Agent Initialization"):
            if use_device_code:
                # Device code flow - for SSH sessions, containers, etc.
                logger.info("Using device code flow...")
                self.credential = DeviceCodeCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    # Callback to display code to user
                    prompt_callback=self._device_code_callback
                )
            else:
                # Interactive browser flow - opens browser for user login
                logger.info("Using interactive browser flow...")
                self.credential = InteractiveBrowserCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    redirect_uri="http://localhost:8400"  # Must be registered in Azure AD
                )
        
        logger.info(f"Interactive agent initialized: {client_id}")
    
    def _device_code_callback(self, verification_uri: str, user_code: str, expires_in: int):
        """Callback to display device code to user."""
        logger.info("\n" + "=" * 60)
        logger.info("AUTHENTICATION REQUIRED")
        logger.info("=" * 60)
        logger.info(f"1. Open: {verification_uri}")
        logger.info(f"2. Enter code: {user_code}")
        logger.info(f"3. Sign in and consent")
        logger.info(f"Code expires in {expires_in} seconds")
        logger.info("=" * 60 + "\n")
    
    def get_user_token(self, scopes: list[str]) -> str:
        """
        Acquire user token with delegated permissions.
        
        Args:
            scopes: List of permission scopes (e.g., ["User.Read", "Mail.Read"])
            
        Returns:
            Access token string
        """
        with AuthErrorContext(f"User Token Acquisition"):
            try:
                # Format scopes for Azure AD
                formatted_scopes = [
                    scope if scope.startswith("https://") else f"https://graph.microsoft.com/{scope}"
                    for scope in scopes
                ]
                
                logger.info(f"Requesting scopes: {formatted_scopes}")
                
                token_result = self.credential.get_token(*formatted_scopes)
                token = token_result.token
                
                logger.info(f"Token acquired successfully")
                logger.info(f"Token expires at: {datetime.fromtimestamp(token_result.expires_on)}")
                
                # Validate and inspect token
                validator = TokenValidator(self.tenant_id)
                claims = validator.get_token_claims(token)
                
                # This should be a user token (not agent token)
                logger.info(f"Token for user: {claims.get('unique_name') or claims.get('upn')}")
                logger.info(f"User OID: {claims.get('oid')}")
                logger.info(f"Scopes: {claims.get('scp', '').split()}")
                
                return token
                
            except ClientAuthenticationError as e:
                auth_error = handle_auth_error(e, "User token acquisition")
                raise auth_error
    
    def access_user_profile(self) -> dict:
        """
        Access user's Microsoft Graph profile.
        
        Returns:
            User profile information
        """
        with AuthErrorContext("Graph API Access"):
            try:
                # Create Graph client with credential
                # Note: GraphServiceClient is from microsoft-graph SDK
                # For this example, we'll use requests directly
                
                import requests
                
                # Get token for Microsoft Graph
                token = self.get_user_token(["User.Read"])
                
                # Call Graph API
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                profile = response.json()
                
                logger.info("\n=== User Profile ===")
                logger.info(f"Name: {profile.get('displayName')}")
                logger.info(f"Email: {profile.get('mail') or profile.get('userPrincipalName')}")
                logger.info(f"Job Title: {profile.get('jobTitle')}")
                logger.info(f"Office Location: {profile.get('officeLocation')}")
                
                return profile
                
            except Exception as e:
                auth_error = handle_auth_error(e, "Graph API access")
                raise auth_error
    
    def demonstrate_user_context(self):
        """
        Demonstrate agent operating in user context.
        Shows how agent can access resources on behalf of the user.
        """
        logger.info("\n=== User Context Demo ===")
        
        try:
            # Get user profile
            profile = self.access_user_profile()
            
            logger.info("\n✓ Agent successfully operating in user context")
            logger.info(f"  User: {profile.get('displayName')}")
            logger.info(f"  Agent acts on behalf of: {profile.get('userPrincipalName')}")
            
            # Show difference from autonomous agent
            logger.info("\n=== Key Differences from Autonomous Agent ===")
            logger.info("1. Requires user authentication")
            logger.info("2. Has delegated permissions (user's permissions)")
            logger.info("3. Actions are audited under user identity")
            logger.info("4. Can access user-specific resources")
            
        except Exception as e:
            logger.error(f"User context demo failed: {e}")


def main():
    """Main execution function."""
    
    # Load environment variables
    load_dotenv()
    
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("AGENT_CLIENT_ID")
    
    # Validate configuration
    if not all([tenant_id, client_id]):
        logger.error(
            "Missing required environment variables!\n"
            "Please create .env file with:\n"
            "  TENANT_ID\n"
            "  AGENT_CLIENT_ID\n"
            "See .env.example for template."
        )
        return 1
    
    try:
        logger.info("=== Interactive Agent Demo ===\n")
        
        # Check if running in headless environment
        import sys
        use_device_code = "--device-code" in sys.argv or not os.environ.get("DISPLAY")
        
        if use_device_code:
            logger.info("Detected headless environment, using device code flow")
        
        # Create interactive agent
        agent = InteractiveAgent(
            tenant_id=tenant_id,
            client_id=client_id,
            use_device_code=use_device_code
        )
        
        # Demo 1: Acquire user token
        logger.info("\n--- Demo 1: User Token Acquisition ---")
        token = agent.get_user_token(["User.Read"])
        logger.info(f"✓ User token acquired (length: {len(token)})")
        
        # Demo 2: Access user resources
        logger.info("\n--- Demo 2: Access User Resources ---")
        agent.demonstrate_user_context()
        
        logger.info("\n=== All demos completed successfully ===")
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
