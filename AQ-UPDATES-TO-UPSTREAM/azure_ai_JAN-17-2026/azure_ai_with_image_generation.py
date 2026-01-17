# Copyright (c) Microsoft. All rights reserved.
import asyncio
import base64
import os
import re
from datetime import datetime
from pathlib import Path

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

"""
Azure AI Agent with Image Generation Example

This sample uses the Azure AI Projects SDK directly (bypassing MAF) to create an agent
that can generate images using the gpt-image-1 model.

Pre-requisites:
- Set AZURE_AI_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME, and 
  AZURE_AI_IMAGE_GENERATION_DEPLOYMENT_NAME environment variables
- Deploy gpt-image-1 model in your Azure AI Foundry project
- Run `az login` for authentication
"""


async def main() -> None:
    # Get configuration from environment
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
    image_model = os.environ.get("AZURE_AI_IMAGE_GENERATION_DEPLOYMENT_NAME", "gpt-image-1")
    
    if not project_endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
    
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client:
            
            # Create agent with image generation tool
            print("Creating agent with image generation tool...")
            agent = await project_client.agents.create_version(
                agent_name="ImageGenAgent",
                definition={
                    "kind": "prompt",
                    "model": model_deployment,
                    "instructions": "Generate images based on user prompts using the image_generation tool.",
                    "tools": [
                        {
                            "type": "image_generation",
                            "quality": "low",
                            "size": "1024x1024"
                        }
                    ]
                }
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            
            # Get OpenAI client for responses
            openai_client = project_client.get_openai_client()
            
            # Generate image using responses API
            query = "Generate an image of a beautiful sunset over mountains."
            print(f"\nUser: {query}")
            print("Generating image...")
            
            response = await openai_client.responses.create(
                input=query,
                extra_headers={
                    "x-ms-oai-image-generation-deployment": image_model
                },
                extra_body={
                    "agent": {
                        "name": agent.name,
                        "type": "agent_reference"
                    }
                }
            )
            print(f"Response created: {response.id}")
            
            # Extract and save the generated image
            print("\nDownloading generated image...")
            image_data = [
                output.result 
                for output in (response.output or []) 
                if hasattr(output, 'type') and output.type == "image_generation_call"
            ]
            
            if image_data and image_data[0]:
                # Create filename from prompt and timestamp
                # Extract first few meaningful words from prompt
                prompt_words = re.sub(r'[^\w\s-]', '', query.lower())  # Remove special chars
                prompt_words = re.sub(r'\s+', '_', prompt_words)  # Replace spaces with underscores
                prompt_part = '_'.join(prompt_words.split('_')[:5])  # Take first 5 words
                
                # Get current timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Create filename
                filename = f"{prompt_part}_{timestamp}.png"
                current_dir = Path(__file__).parent.resolve()
                file_path = current_dir / filename
                
                # Decode base64 and save
                image_bytes = base64.b64decode(image_data[0])
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                
                print(f"Image downloaded and saved to: {file_path}")
            else:
                print("No image data found in the response.")
            
            # Clean up
            print("\nCleaning up...")
            await project_client.agents.delete_version(agent.name, agent.version)
            print("Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
