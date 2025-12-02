#!/usr/bin/env python3
"""
AG-UI Client - Console client for interacting with AG-UI protocol servers.

This client connects to an AG-UI server and provides an interactive
console interface with streaming response support.
"""

import asyncio
import os
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime

import httpx
from httpx_sse import aconnect_sse

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'


# ============================================================================
# Configuration
# ============================================================================

# Server configuration
DEFAULT_SERVER_URL = "http://localhost:5100"
AGUI_SERVER_URL = os.getenv("AGUI_SERVER_URL", DEFAULT_SERVER_URL)


# ============================================================================
# AG-UI Client
# ============================================================================

class AGUIClient:
    """Client for interacting with AG-UI protocol servers."""
    
    def __init__(self, server_url: str = AGUI_SERVER_URL):
        """
        Initialize AG-UI client.
        
        Args:
            server_url: URL of the AG-UI server
        """
        self.server_url = server_url.rstrip('/')
        self.thread_id: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
        
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def send_message(
        self,
        message: str,
        thread_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Send a message to the AG-UI server and stream responses.
        
        Args:
            message: User message to send
            thread_id: Optional thread ID for conversation continuity
            context: Optional additional context
        """
        # Use existing thread or let server create one
        request_thread_id = thread_id or self.thread_id
        
        # Build request payload
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "context": context or {}
        }
        
        if request_thread_id:
            payload["threadId"] = request_thread_id
        
        # Track state
        run_started = False
        current_thread_id = None
        current_run_id = None
        response_text = ""
        
        try:
            # Connect to SSE endpoint
            async with aconnect_sse(
                self.client,
                "POST",
                f"{self.server_url}/",
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as event_source:
                
                async for event in event_source.aiter_sse():
                    # Parse event
                    event_type = event.event
                    
                    try:
                        data = json.loads(event.data)
                    except json.JSONDecodeError:
                        print(f"{Colors.RED}⚠️  Failed to parse event data{Colors.RESET}")
                        continue
                    
                    # Handle different event types
                    if event_type == "thread.run.created":
                        # Run started
                        current_thread_id = data.get("thread_id")
                        current_run_id = data.get("run_id")
                        
                        if not run_started:
                            print(f"\n{Colors.YELLOW}[Run Started - Thread: {current_thread_id}, Run: {current_run_id}]{Colors.RESET}")
                            run_started = True
                        
                        # Update persistent thread ID
                        if current_thread_id and not self.thread_id:
                            self.thread_id = current_thread_id
                    
                    elif event_type == "thread.message.delta":
                        # Streaming text content
                        delta = data.get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            print(f"{Colors.CYAN}{content}{Colors.RESET}", end="", flush=True)
                            response_text += content
                    
                    elif event_type == "thread.message.completed":
                        # Message completed (optional handling)
                        pass
                    
                    elif event_type == "thread.run.completed":
                        # Run completed
                        if current_thread_id and current_run_id:
                            print(f"\n{Colors.GREEN}[Run Finished - Thread: {current_thread_id}, Run: {current_run_id}]{Colors.RESET}")
                        break
                    
                    elif event_type == "error":
                        # Error occurred
                        error_msg = data.get("error", "Unknown error")
                        print(f"\n{Colors.RED}❌ Error: {error_msg}{Colors.RESET}")
                        break
        
        except httpx.ConnectError:
            print(f"{Colors.RED}❌ Failed to connect to server at {self.server_url}{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Make sure the server is running: python agui_server.py{Colors.RESET}")
        except httpx.ReadTimeout:
            print(f"{Colors.RED}❌ Request timed out{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
    
    async def check_health(self) -> bool:
        """
        Check if the server is healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.server_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False


# ============================================================================
# Interactive Console
# ============================================================================

async def run_interactive_console():
    """Run the interactive console for AG-UI client."""
    # Print header
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 80)
    print("🚀 AG-UI Client")
    print("=" * 80)
    print(f"{Colors.RESET}")
    print(f"Connecting to server at: {Colors.CYAN}{AGUI_SERVER_URL}{Colors.RESET}\n")
    
    # Initialize client
    client = AGUIClient(AGUI_SERVER_URL)
    
    # Check server health
    if not await client.check_health():
        print(f"{Colors.RED}❌ Server is not responding at {AGUI_SERVER_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Make sure the server is running:{Colors.RESET}")
        print(f"   cd AQ-CODE/agui-clientserver")
        print(f"   python agui_server.py")
        return
    
    print(f"{Colors.GREEN}✅ Connected to server{Colors.RESET}\n")
    
    # Main interaction loop
    try:
        while True:
            # Get user input
            try:
                user_input = input(f"\n{Colors.BOLD}User{Colors.RESET} (:q or quit to exit): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()  # New line
                break
            
            # Check for exit commands
            if user_input.lower() in [':q', 'quit', 'exit']:
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Send message and stream response
            await client.send_message(user_input)
    
    finally:
        # Cleanup
        await client.close()
        print(f"\n{Colors.CYAN}Goodbye! 👋{Colors.RESET}\n")


# ============================================================================
# Non-Interactive Mode (for testing)
# ============================================================================

async def run_single_query(query: str):
    """
    Run a single query in non-interactive mode.
    
    Args:
        query: Query to send to the server
    """
    client = AGUIClient(AGUI_SERVER_URL)
    
    try:
        # Check server health
        if not await client.check_health():
            print(f"❌ Server is not responding at {AGUI_SERVER_URL}")
            return
        
        print(f"Query: {query}\n")
        await client.send_message(query)
        print()  # New line after response
    
    finally:
        await client.close()


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point."""
    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Non-interactive mode - run single query
        query = " ".join(sys.argv[1:])
        await run_single_query(query)
    else:
        # Interactive mode
        await run_interactive_console()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}Interrupted. Goodbye! 👋{Colors.RESET}\n")
        sys.exit(0)
