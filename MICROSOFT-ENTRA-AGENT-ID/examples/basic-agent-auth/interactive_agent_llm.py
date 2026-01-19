"""
Interactive Agent with LLM - User Context
Date: January 19, 2026

Demonstrates:
- Interactive authentication with user consent
- LLM access with delegated permissions (user context)
- AI agent acting on behalf of authenticated user
- User-scoped Azure OpenAI access
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential, DeviceCodeCredential
from openai import AzureOpenAI
from azure.core.exceptions import ClientAuthenticationError

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
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('utils.error_handler').setLevel(logging.WARNING)
logging.getLogger('utils.token_validator').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/user_impersonation"
COGNITIVE_SERVICES_DEFAULT_SCOPE = "https://cognitiveservices.azure.com/.default"


class InteractiveAgentWithLLM:
    """
    An AI agent that operates with user context (delegated permissions).
    Requires user authentication and acts on behalf of the user.
    """
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        azure_openai_endpoint: str,
        deployment_name: str,
        use_device_code: bool = False
    ):
        """
        Initialize interactive AI agent.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Agent's client ID (app registration)
            azure_openai_endpoint: Azure OpenAI endpoint URL
            deployment_name: Model deployment name
            use_device_code: Use device code flow instead of browser
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.azure_openai_endpoint = azure_openai_endpoint
        self.deployment_name = deployment_name
        
        # Create credential
        with AuthErrorContext("Agent Initialization"):
            if use_device_code:
                logger.info("Using device code flow...")
                self.credential = DeviceCodeCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    prompt_callback=self._device_code_callback
                )
            else:
                logger.info("Using interactive browser flow...")
                self.credential = InteractiveBrowserCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    redirect_uri="http://localhost:8400"
                )
        
        # Create Azure OpenAI client with user credential
        self.openai_client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint,
            azure_ad_token_provider=self._get_openai_token,
            api_version="2024-08-01-preview"
        )
        
        logger.info(f"Interactive AI agent initialized: {client_id}")
        logger.info(f"Azure OpenAI endpoint: {azure_openai_endpoint}")
        logger.info(f"Model deployment: {deployment_name}")
    
    def _device_code_callback(self, verification_uri: str, user_code: str, expires_in: int):
        """Callback to display device code to user."""
        logger.info("\n" + "=" * 60)
        logger.info("USER AUTHENTICATION REQUIRED")
        logger.info("=" * 60)
        logger.info(f"1. Open: {verification_uri}")
        logger.info(f"2. Enter code: {user_code}")
        logger.info(f"3. Sign in and consent")
        logger.info(f"Code expires in {expires_in} seconds")
        logger.info("=" * 60 + "\n")
    
    def _get_openai_token(self) -> str:
        """Token provider for Azure OpenAI."""
        try:
            # Delegated tokens should request a delegated scope (user_impersonation).
            # Some tenants/configurations may still accept /.default; keep a fallback.
            try:
                token = self.credential.get_token(COGNITIVE_SERVICES_SCOPE)
            except Exception:
                token = self.credential.get_token(COGNITIVE_SERVICES_DEFAULT_SCOPE)
            return token.token
        except Exception as e:
            logger.error(f"Failed to acquire token with user credentials: {e}")
            logger.error("User may need to consent to Cognitive Services access")
            raise
    
    def verify_user_context(self):
        """Verify that the agent is operating in user context."""
        logger.info("\n=== User Context Verification ===")
        
        with AuthErrorContext("User Context Verification"):
            # Get token for inspection
            try:
                token_result = self.credential.get_token(COGNITIVE_SERVICES_SCOPE)
            except Exception:
                token_result = self.credential.get_token(COGNITIVE_SERVICES_DEFAULT_SCOPE)
            token = token_result.token
            
            # Validate the token
            validator = TokenValidator(self.tenant_id)
            claims = validator.get_token_claims(token)
            
            user_name = claims.get('unique_name') or claims.get('upn') or claims.get('email')
            user_oid = claims.get('oid')
            
            logger.info(f"✓ Agent acting on behalf of user: {user_name}")
            logger.info(f"  User OID: {user_oid}")
            logger.info(f"  Token expires at: {datetime.fromtimestamp(token_result.expires_on)}")
            logger.info(f"  Scopes: {claims.get('scp', 'N/A')}")
            
            # Verify it's a user token (not agent token)
            is_agent = validator.validate_agent_identity(token)
            if not is_agent:
                logger.info(f"✓ Token confirmed as user identity (delegated permissions)")
            else:
                logger.warning(f"⚠ Token appears to be an agent identity")
    
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """
        Send a message to the LLM on behalf of the user.
        
        Args:
            user_message: The user's message
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        with AuthErrorContext("LLM Chat Request"):
            try:
                messages = []
                
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                
                messages.append({"role": "user", "content": user_message})
                
                logger.info(f"\n=== Sending request on behalf of user ===")
                logger.info(f"User message: {user_message[:100]}...")
                
                response = self.openai_client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                assistant_message = response.choices[0].message.content
                
                logger.info(f"\n=== LLM Response ===")
                logger.info(f"Model: {response.model}")
                logger.info(f"Usage: {response.usage.total_tokens} tokens")
                logger.info(f"Response: {assistant_message[:200]}...")
                
                return assistant_message
                
            except Exception as e:
                logger.error(f"Chat request failed: {e}")
                auth_error = handle_auth_error(e, "LLM chat")
                raise auth_error
    
    def demonstrate_user_context_llm(self):
        """Demonstrate LLM interaction in user context."""
        logger.info("\n=== User Context LLM Demo ===")
        
        system_prompt = """You are an AI assistant operating with user context.
You have delegated permissions - meaning you act on behalf of the authenticated user.
All actions are audited under the user's identity."""
        
        questions = [
            "What does it mean for an AI agent to operate with 'user context'?",
            "How do delegated permissions differ from application permissions?",
        ]
        
        for i, question in enumerate(questions, 1):
            logger.info(f"\n--- Question {i} ---")
            logger.info(f"Query: {question}")
            
            try:
                response = self.chat(question, system_prompt)
                logger.info(f"✓ Response received (acting as user)")
                print(f"\n{response}\n")
            except Exception as e:
                logger.error(f"Question {i} failed: {e}")
        
        logger.info("\n=== Key Characteristics of User Context ===")
        logger.info("1. ✓ Requires user authentication and consent")
        logger.info("2. ✓ Agent inherits user's permissions")
        logger.info("3. ✓ All actions audited under user identity")
        logger.info("4. ✓ Can access user-specific resources")
        logger.info("5. ✓ Token expires when user session ends")


def main():
    """Main execution function."""
    
    # Load environment variables
    load_dotenv()
    
    tenant_id = os.getenv("TENANT_ID")
    # Use dedicated interactive agent client ID, fallback to service principal ID
    client_id = os.getenv("INTERACTIVE_AGENT_CLIENT_ID") or os.getenv("AGENT_CLIENT_ID")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    # Validate configuration
    if not all([tenant_id, client_id, azure_openai_endpoint, deployment_name]):
        logger.error(
            "Missing required environment variables!\n"
            "Please ensure .env file contains:\n"
            "  TENANT_ID\n"
            "  AGENT_CLIENT_ID\n"
            "  AZURE_OPENAI_ENDPOINT\n"
            "  AZURE_OPENAI_DEPLOYMENT\n"
        )
        return 1
    
    try:
        logger.info("=== Interactive AI Agent with LLM Demo ===\n")
        
        # Check if running in headless environment
        import sys
        use_device_code = "--device-code" in sys.argv or not os.environ.get("DISPLAY")
        
        if use_device_code:
            logger.info("Detected headless environment, using device code flow\n")
        
        # Create interactive AI agent
        agent = InteractiveAgentWithLLM(
            tenant_id=tenant_id,
            client_id=client_id,
            azure_openai_endpoint=azure_openai_endpoint,
            deployment_name=deployment_name,
            use_device_code=use_device_code
        )
        
        # Demo 1: Verify user context
        logger.info("\n--- Demo 1: User Context Verification ---")
        agent.verify_user_context()
        
        # Demo 2: Simple chat interaction
        logger.info("\n--- Demo 2: LLM Chat in User Context ---")
        response = agent.chat(
            "What are the benefits of user-delegated permissions for AI agents?",
            system_prompt="You are a helpful AI assistant explaining Azure identity concepts."
        )
        print(f"\nAgent Response (as user):\n{response}\n")
        
        # Demo 3: User context characteristics
        logger.info("\n--- Demo 3: User Context Characteristics ---")
        agent.demonstrate_user_context_llm()
        
        logger.info("\n=== All demos completed successfully ===")
        logger.info("\nNote: App registration must have 'User.Read' and delegated")
        logger.info("Cognitive Services permissions for this demo to work.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
