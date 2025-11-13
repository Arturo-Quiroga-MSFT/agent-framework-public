"""
Helper script to set up File Search for DevUI demo.
Creates a vector store with the sample employees.pdf document.
"""

import asyncio
import os
from pathlib import Path

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def setup_file_search():
    """Create vector store with sample employee PDF."""
    
    # Check if already configured
    existing_id = os.getenv("FILE_SEARCH_VECTOR_STORE_ID")
    if existing_id:
        print(f"✓ Vector store already configured: {existing_id}")
        print("\nTo verify it exists, go to https://ai.azure.com")
        return
    
    # Find the sample PDF
    sample_pdf = Path(__file__).parent.parent.parent / "python" / "samples" / "getting_started" / "agents" / "resources" / "employees.pdf"
    
    if not sample_pdf.exists():
        print(f"❌ Sample PDF not found at: {sample_pdf}")
        print("\nPlease ensure the repository has the sample files.")
        return
    
    print(f"📄 Found sample PDF: {sample_pdf}")
    print("🔄 Creating vector store...")
    
    # Create client
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    if not project_endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not found in .env file")
        return
    
    client = AzureAIAgentClient(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment_name,
        async_credential=DefaultAzureCredential()
    )
    
    try:
        # Upload the PDF
        print("⬆️  Uploading employees.pdf...")
        file = await client.project_client.agents.files.upload_and_poll(
            file_path=str(sample_pdf),
            purpose="assistants"
        )
        print(f"✓ File uploaded: {file.id}")
        
        # Create vector store
        print("🔧 Creating vector store...")
        vector_store = await client.project_client.agents.vector_stores.create_and_poll(
            file_ids=[file.id],
            name="Employee Documents (DevUI Demo)"
        )
        print(f"✓ Vector store created: {vector_store.id}")
        
        # Show instructions
        print("\n" + "="*60)
        print("SUCCESS! Add this to your .env file:")
        print("="*60)
        print(f'FILE_SEARCH_VECTOR_STORE_ID="{vector_store.id}"')
        print("="*60)
        print("\nThen restart DevUI:")
        print("  cd AQ-CODE/azure_ai")
        print("  devui azure_agents --port 8100")
        print("\n✓ File Search agent will now work!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(setup_file_search())
