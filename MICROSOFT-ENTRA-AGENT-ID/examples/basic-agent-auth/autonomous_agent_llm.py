"""
Autonomous Agent with LLM - Client Credentials Flow
Date: January 19, 2026

Demonstrates:
- Client credentials authentication (autonomous agent)
- Azure OpenAI integration with agent identity
- LLM-powered autonomous operations
- Secure API access without user interaction
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
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
logging.getLogger('utils.error_handler').setLevel(logging.WARNING)
logging.getLogger('utils.token_validator').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class AutonomousAgentWithLLM:
    """
    An autonomous AI agent that uses LLM capabilities.
    Authenticates via client credentials (service principal).
    """
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        azure_openai_endpoint: str,
        deployment_name: str
    ):
        """
        Initialize autonomous AI agent.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Agent's client ID (app registration)
            client_secret: Agent's client secret
            azure_openai_endpoint: Azure OpenAI endpoint URL
            deployment_name: Model deployment name
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.azure_openai_endpoint = azure_openai_endpoint
        self.deployment_name = deployment_name
        
        # Create credential
        with AuthErrorContext("Agent Initialization"):
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        
        # Create Azure OpenAI client with agent credential
        self.openai_client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint,
            azure_ad_token_provider=self._get_openai_token,
            api_version="2024-08-01-preview"
        )
        
        print(f"\n{'='*60}")
        print(f"Autonomous AI Agent with LLM")
        print(f"{'='*60}")
        print(f"Agent ID: {client_id}")
        print(f"Azure OpenAI: {azure_openai_endpoint}")
        print(f"Model: {deployment_name}")
        print(f"{'='*60}\n")
    
    def _get_openai_token(self) -> str:
        """
        Token provider for Azure OpenAI.
        Returns a valid token for Cognitive Services.
        """
        try:
            token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        except Exception as e:
            logger.error(f"Failed to acquire token for Azure OpenAI: {e}")
            raise
    
    def verify_identity(self):
        """Verify the agent's identity and token."""
        print(f"\n{'='*60}")
        print(f"DEMO 1: Agent Identity Verification")
        print(f"{'='*60}")
        
        with AuthErrorContext("Identity Verification"):
            # Get token for inspection
            token_result = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            token = token_result.token
            
            # Validate the token
            validator = TokenValidator(self.tenant_id)
            claims = validator.get_token_claims(token)
            
            print(f"✓ Agent ID: {claims.get('appid')}")
            print(f"✓ Token expires: {datetime.fromtimestamp(token_result.expires_on)}")
            
            # Verify it's an agent token
            is_agent = validator.validate_agent_identity(token)
            if is_agent:
                print(f"✓ Confirmed as agent identity (not user)")
            else:
                print(f"⚠ Warning: Token may not be agent identity")
    
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
                
                response = self.openai_client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                assistant_message = response.choices[0].message.content
                
                print(f"  Model: {response.model}")
                print(f"  Tokens: {response.usage.total_tokens}")
                
                return assistant_message
                
            except Exception as e:
                logger.error(f"Chat request failed: {e}")
                auth_error = handle_auth_error(e, "LLM chat")
                raise auth_error
    
    def demonstrate_autonomous_reasoning(self):
        """Demonstrate autonomous agent reasoning with LLM."""
        print(f"\n{'='*60}")
        print(f"DEMO 3: Autonomous Agent Reasoning")
        print(f"{'='*60}")
        
        system_prompt = """You are an autonomous AI agent operating with a service principal identity.
You have no direct user interaction - you make decisions independently based on your programming.
Respond concisely and professionally."""
        
        tasks = [
            "Explain the difference between autonomous agents and user-delegated agents in 2 sentences.",
            "What are the top 3 security considerations for autonomous AI agents?",
            "Generate a brief summary of what Microsoft Entra Agent ID enables."
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\n--- Task {i}: {task[:60]}...")
            
            try:
                response = self.chat(task, system_prompt)
                print(f"\nResponse:\n{response}\n")
            except Exception as e:
                print(f"ERROR: Task {i} failed: {e}")


def main():
    """Main execution function."""
    
    # Load environment variables
    load_dotenv()
    
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("AGENT_CLIENT_ID")
    client_secret = os.getenv("AGENT_CLIENT_SECRET")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    # Validate configuration
    if not all([tenant_id, client_id, client_secret, azure_openai_endpoint, deployment_name]):
        print("ERROR: Missing required environment variables!")
        print("Please ensure .env file contains:")
        print("  TENANT_ID")
        print("  AGENT_CLIENT_ID")
        print("  AGENT_CLIENT_SECRET")
        print("  AZURE_OPENAI_ENDPOINT")
        print("  AZURE_OPENAI_DEPLOYMENT")
        return 1
    
    try:
        # Create autonomous AI agent
        agent = AutonomousAgentWithLLM(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            azure_openai_endpoint=azure_openai_endpoint,
            deployment_name=deployment_name
        )
        
        # Demo 1: Verify agent identity
        agent.verify_identity()
        
        # Demo 2: Simple chat interaction
        print(f"\n{'='*60}")
        print(f"DEMO 2: Simple LLM Interaction")
        print(f"{'='*60}")
        print(f"Query: What is Microsoft Entra Agent ID?")
        response = agent.chat(
            "What is Microsoft Entra Agent ID?",
            system_prompt="You are a helpful AI assistant with expertise in Azure identity services."
        )
        print(f"\nResponse:\n{response}\n")
        
        # Demo 3: Autonomous reasoning
        agent.demonstrate_autonomous_reasoning()
        
        print(f"\n{'='*60}")
        print(f"ALL DEMOS COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        return 0
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
