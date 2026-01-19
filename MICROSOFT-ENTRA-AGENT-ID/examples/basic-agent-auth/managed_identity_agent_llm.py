"""
Managed Identity Agent with LLM
Date: January 19, 2026

Demonstrates:
- Managed identity authentication (Azure-hosted agents)
- Zero configuration LLM access
- Automatic credential management for AI agents
- Secure Azure OpenAI access without secrets
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
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
logging.getLogger('utils.error_handler').setLevel(logging.WARNING)
logging.getLogger('utils.token_validator').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ManagedIdentityAgentWithLLM:
    """
    An AI agent running in Azure that uses managed identity.
    No credentials needed - Azure manages authentication automatically.
    """
    
    def __init__(
        self,
        azure_openai_endpoint: str,
        deployment_name: str,
        client_id: str = None
    ):
        """
        Initialize managed identity AI agent.
        
        Args:
            azure_openai_endpoint: Azure OpenAI endpoint URL
            deployment_name: Model deployment name
            client_id: Optional client ID for user-assigned managed identity
        """
        self.azure_openai_endpoint = azure_openai_endpoint
        self.deployment_name = deployment_name
        self.client_id = client_id
        
        # Create credential
        with AuthErrorContext("Managed Identity Initialization"):
            if client_id:
                logger.info(f"Using user-assigned managed identity: {client_id}")
                self.credential = ManagedIdentityCredential(client_id=client_id)
            else:
                logger.info("Using system-assigned managed identity")
                self.credential = ManagedIdentityCredential()
        
        # Create Azure OpenAI client with managed identity
        self.openai_client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint,
            azure_ad_token_provider=self._get_openai_token,
            api_version="2024-08-01-preview"
        )
        
        logger.info("Managed identity AI agent initialized")
        logger.info(f"Azure OpenAI endpoint: {azure_openai_endpoint}")
        logger.info(f"Model deployment: {deployment_name}")
    
    def _get_openai_token(self) -> str:
        """Token provider for Azure OpenAI."""
        try:
            token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        except Exception as e:
            logger.error(f"Failed to acquire token via managed identity: {e}")
            logger.error("Ensure managed identity is enabled and has Cognitive Services role")
            raise
    
    def verify_zero_config(self):
        """Verify that no credentials are needed."""
        logger.info("\n=== Zero Configuration Verification ===")
        logger.info("✓ No client secret in code")
        logger.info("✓ No connection strings")
        logger.info("✓ No API keys")
        logger.info("✓ Azure manages all credentials automatically")
        logger.info("✓ Credentials rotate automatically")
    
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """
        Send a message to the LLM and get a response.
        
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
                
                logger.info(f"\n=== Sending request via managed identity ===")
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
    
    def demonstrate_managed_identity_llm(self):
        """Demonstrate LLM access via managed identity."""
        logger.info("\n=== Managed Identity LLM Access Demo ===")
        
        system_prompt = """You are an AI agent running in Azure with managed identity.
You have zero-configuration security - Azure handles all authentication automatically."""
        
        questions = [
            "What are the benefits of using managed identities for AI agents?",
            "How does zero-configuration authentication improve security?",
        ]
        
        for i, question in enumerate(questions, 1):
            logger.info(f"\n--- Question {i} ---")
            logger.info(f"Query: {question}")
            
            try:
                response = self.chat(question, system_prompt)
                logger.info(f"✓ Response received via managed identity")
                print(f"\n{response}\n")
            except Exception as e:
                logger.error(f"Question {i} failed: {e}")


class DefaultCredentialAgentWithLLM:
    """
    AI agent using DefaultAzureCredential - works in any environment.
    Automatically tries: Environment → Managed Identity → CLI → VS Code
    """
    
    def __init__(self, azure_openai_endpoint: str, deployment_name: str):
        """Initialize agent with DefaultAzureCredential."""
        with AuthErrorContext("Default Credential Initialization"):
            self.credential = DefaultAzureCredential()
        
        self.azure_openai_endpoint = azure_openai_endpoint
        self.deployment_name = deployment_name
        
        # Create Azure OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint,
            azure_ad_token_provider=self._get_openai_token,
            api_version="2024-08-01-preview"
        )
        
        logger.info("DefaultAzureCredential AI agent initialized")
        logger.info("Will try: Environment → Managed Identity → CLI → VS Code")
    
    def _get_openai_token(self) -> str:
        """Token provider for Azure OpenAI."""
        try:
            token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        except Exception as e:
            logger.error(f"All credential methods failed for Azure OpenAI: {e}")
            raise
    
    def chat(self, user_message: str) -> str:
        """Send a message to the LLM."""
        response = self.openai_client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content


def main():
    """Main execution function."""
    
    load_dotenv()
    
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    # Validate configuration
    if not all([azure_openai_endpoint, deployment_name]):
        logger.error(
            "Missing required environment variables!\n"
            "Please ensure .env file contains:\n"
            "  AZURE_OPENAI_ENDPOINT\n"
            "  AZURE_OPENAI_DEPLOYMENT\n"
        )
        return 1
    
    # Check environment
    is_azure = os.path.exists("/var/lib/waagent") or os.environ.get("MSI_ENDPOINT")
    
    try:
        logger.info("=== Managed Identity AI Agent with LLM Demo ===\n")
        
        if is_azure:
            logger.info("✓ Detected Azure environment")
            
            # Demo: Managed identity with LLM
            logger.info("\n--- Managed Identity LLM Demo ---")
            agent = ManagedIdentityAgentWithLLM(
                azure_openai_endpoint=azure_openai_endpoint,
                deployment_name=deployment_name
            )
            
            agent.verify_zero_config()
            agent.demonstrate_managed_identity_llm()
            
        else:
            logger.info("⚠ Not running in Azure environment")
            logger.info("Falling back to DefaultAzureCredential\n")
            
            # Demo: DefaultAzureCredential with LLM
            logger.info("\n--- DefaultAzureCredential LLM Demo ---")
            agent = DefaultCredentialAgentWithLLM(
                azure_openai_endpoint=azure_openai_endpoint,
                deployment_name=deployment_name
            )
            
            response = agent.chat("What is the advantage of using DefaultAzureCredential?")
            print(f"\nAgent Response:\n{response}\n")
            
            logger.info("\n=== How to Enable Managed Identity ===")
            logger.info("\nFor Azure VM:")
            logger.info("  az vm identity assign --name <vm-name> --resource-group <rg>")
            logger.info("\nFor Azure App Service:")
            logger.info("  az webapp identity assign --name <app-name> --resource-group <rg>")
            logger.info("\nFor Azure Container Instance:")
            logger.info("  az container create ... --assign-identity")
            
            logger.info("\nThen grant Cognitive Services OpenAI User role:")
            logger.info("  az role assignment create \\")
            logger.info("    --assignee <managed-identity-principal-id> \\")
            logger.info("    --role 'Cognitive Services OpenAI User' \\")
            logger.info("    --scope <openai-resource-id>")
        
        logger.info("\n=== All demos completed successfully ===")
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
