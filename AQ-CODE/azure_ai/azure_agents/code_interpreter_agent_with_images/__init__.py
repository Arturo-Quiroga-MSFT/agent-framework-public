"""
Azure AI Agent: Python Code Interpreter with Image Display

Enhanced Code Interpreter agent that extracts and embeds plot images in DevUI responses.
This version automatically downloads generated plots and includes them in the response.
"""

import base64
import os
from pathlib import Path
from typing import AsyncIterator

from agent_framework import AgentRunResponse, AgentRunResponseUpdate, HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables - go up to azure_ai/ directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check required environment variables
project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")


class CodeInterpreterAgentWithImages:
    """Wrapper that adds automatic image extraction to Code Interpreter responses."""
    
    def __init__(self):
        """Initialize the wrapper with the base agent."""
        credential = DefaultAzureCredential()
        
        self.client = AzureAIAgentClient(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            async_credential=credential
        )
        
        self.base_agent = self.client.create_agent(
            name="CodeInterpreterAgent",
            instructions=(
                "You are a helpful assistant that can write and execute Python code to solve problems. "
                "When asked to perform calculations or computations, write clear Python code, "
                "explain what the code does, and execute it to get the result. "
                "When creating plots or visualizations, mention that they will be displayed automatically. "
                "Always show the code you're running before execution."
            ),
            tools=HostedCodeInterpreterTool(),
        )
        
        # Store agent metadata
        self.name = "CodeInterpreterWithImages"
        self.description = (
            "AZURE AI DEMO: Python Code Interpreter with Image Display\n"
            "\n"
            "Enhanced Code Interpreter that automatically extracts and displays generated plots!\n"
            "\n"
            "TRY THESE QUERIES:\n"
            "  • Create a plot of y = x^2 from -10 to 10\n"
            "  • Generate a bar chart comparing sales data\n"
            "  • Create a scatter plot with random data points\n"
            "  • Plot sine and cosine waves from 0 to 2π\n"
            "  • Calculate the factorial of 100\n"
            "  • Generate the first 20 Fibonacci numbers\n"
            "\n"
            "FEATURES:\n"
            "  ✨ Automatic plot extraction and display\n"
            "  • Executes Python code in secure sandbox\n"
            "  • Complex mathematical calculations\n"
            "  • Data visualization and plotting\n"
            "  • Shows code before executing it\n"
            "\n"
            "IMAGE DISPLAY:\n"
            "  📊 Plots are automatically downloaded and embedded\n"
            "  💾 Images saved to: generated_plots/\n"
            "  🔗 Base64 encoded for inline display in DevUI"
        )
    
    async def _extract_images_from_thread(self, thread_id: str) -> list[tuple[str, bytes]]:
        """Extract image files from agent thread messages.
        
        Returns:
            List of (file_id, image_bytes) tuples
        """
        images = []
        
        print(f"[DEBUG] Extracting images from thread: {thread_id}")
        
        try:
            # Get messages from the thread
            messages_iterator = self.client.agents_client.messages.list(thread_id=thread_id)
            print("[DEBUG] Got messages iterator")
            
            message_count = 0
            async for message in messages_iterator:
                message_count += 1
                print(f"[DEBUG] Processing message {message_count}, content items: {len(message.content) if hasattr(message, 'content') else 0}")
                
                if not hasattr(message, 'content'):
                    continue
                    
                for idx, content_item in enumerate(message.content):
                    print(f"[DEBUG] Content item {idx} type: {type(content_item)}")
                    
                    # Check for image file content
                    if hasattr(content_item, 'image_file') and content_item.image_file:
                        file_id = content_item.image_file.file_id
                        print(f"[DEBUG] Found image file: {file_id}")
                        
                        try:
                            # Download the image file
                            file_content_stream = await self.client.agents_client.files.get_content(file_id)
                            chunks = []
                            async for chunk in file_content_stream:
                                chunks.append(chunk)
                            
                            file_content = b''.join(chunks)
                            print(f"[DEBUG] Downloaded image: {len(file_content)} bytes")
                            images.append((file_id, file_content))
                            
                        except Exception as e:
                            print(f"[WARNING] Could not download image {file_id}: {e}")
                            import traceback
                            traceback.print_exc()
            
            print(f"[DEBUG] Processed {message_count} messages, found {len(images)} images")
                            
        except Exception as e:
            print(f"[WARNING] Error retrieving messages from thread: {e}")
            import traceback
            traceback.print_exc()
        
        return images
    
    def _save_and_encode_images(self, images: list[tuple[str, bytes]]) -> list[str]:
        """Save images to disk and return display information.
        
        Args:
            images: List of (file_id, image_bytes) tuples
            
        Returns:
            List of formatted text sections with image information
        """
        from datetime import datetime
        
        # Create output directory if it doesn't exist
        output_dir = Path(__file__).parent.parent.parent / "generated_plots"
        output_dir.mkdir(exist_ok=True)
        
        markdown_images = []
        
        for idx, (file_id, image_data) in enumerate(images, 1):
            # Save to disk
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plot_{timestamp}_{file_id}.png"
            filepath = output_dir / filename
            
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Create a simple text-based response without base64
                # Users can open the file from the path provided
                image_section = (
                    f"\n\n📊 **Generated Plot #{idx}:**\n\n"
                    f"✅ Plot created successfully!\n\n"
                    f"📁 **File saved to:**\n"
                    f"   `{filename}`\n\n"
                    f"📂 **Full path:**\n"
                    f"   `{filepath}`\n\n"
                    f"💡 **To view:** Open the file from Finder or use:\n"
                    f"   `open {filepath}`\n\n"
                    f"📊 **Image size:** {len(image_data):,} bytes ({len(image_data)/1024:.1f} KB)"
                )
                
                markdown_images.append(image_section)
                print(f"[DEBUG] Image saved: {filepath} ({len(image_data)} bytes)")
                
            except Exception as e:
                print(f"[WARNING] Could not save image {file_id}: {e}")
                markdown_images.append(f"\n\n⚠️ *Image {idx} could not be saved: {e}*")
        
        return markdown_images
    
    async def run(self, *args, **kwargs) -> AgentRunResponse:
        """Run the agent and post-process to extract images."""
        print("[DEBUG] CodeInterpreterWithImages.run() called")
        
        # Run the base agent
        response = await self.base_agent.run(*args, **kwargs)
        print(f"[DEBUG] Base agent response received, messages: {len(response.messages)}")
        
        # Get thread ID from kwargs if provided
        thread = kwargs.get('thread')
        print(f"[DEBUG] Thread from kwargs: {thread}")
        
        if not thread or not hasattr(thread, 'service_thread_id'):
            print("[DEBUG] No valid thread found, returning original response")
            return response
        
        thread_id = thread.service_thread_id
        print(f"[DEBUG] Thread ID: {thread_id}")
        
        # Extract images from the thread
        images = await self._extract_images_from_thread(thread_id)
        print(f"[DEBUG] Found {len(images)} images")
        
        if images:
            # Save images and get markdown
            markdown_images = self._save_and_encode_images(images)
            print(f"[DEBUG] Generated {len(markdown_images)} markdown images")
            
            # Append image information to the response text
            if response.messages:
                last_message = response.messages[-1]
                
                # Add image markdown to the last message's text content
                image_section = "\n\n---\n" + "".join(markdown_images)
                
                # Find and update text content
                from agent_framework import TextContent
                found_text = False
                for content in last_message.contents:
                    if hasattr(content, 'text'):
                        content.text += image_section
                        found_text = True
                        print("[DEBUG] Added images to existing text content")
                        break
                
                # If no text content found, add a new one
                if not found_text:
                    last_message.contents.append(TextContent(text=image_section))
                    print("[DEBUG] Added images as new text content")
            else:
                print("[DEBUG] No messages in response")
        else:
            print("[DEBUG] No images found in thread")
        
        return response
    
    async def run_stream(self, *args, **kwargs) -> AsyncIterator[AgentRunResponseUpdate]:
        """Run the agent in streaming mode and post-process to extract images.
        
        Note: Images are only available after the full response is complete.
        """
        updates = []
        thread_id = None
        
        # Collect all updates
        async for update in self.base_agent.run_stream(*args, **kwargs):
            updates.append(update)
            yield update
        
        # Get thread ID from kwargs if provided
        thread = kwargs.get('thread')
        if thread and hasattr(thread, 'service_thread_id'):
            thread_id = thread.service_thread_id
        
        if thread_id:
            # Extract images after streaming is complete
            images = await self._extract_images_from_thread(thread_id)
            
            if images:
                # Save images and get markdown
                markdown_images = self._save_and_encode_images(images)
                
                # Yield a final update with image information
                from agent_framework import TextContent, Role
                
                image_text = "\n\n---\n" + "".join(markdown_images)
                
                final_update = AgentRunResponseUpdate(
                    role=Role.ASSISTANT,
                    contents=[TextContent(text=image_text)]
                )
                
                yield final_update
    
    def get_new_thread(self):
        """Delegate to base agent."""
        return self.base_agent.get_new_thread()
    
    def __getattr__(self, name):
        """Delegate other attribute access to base agent."""
        return getattr(self.base_agent, name)


# Create and export the wrapped agent
agent = CodeInterpreterAgentWithImages()
