#!/usr/bin/env python
"""Verify agent_framework installation and imports.

This script checks that all essential agent_framework components
can be imported and provides diagnostic information if they can't.

Usage:
    python verify_agent_framework.py
"""
import sys
from typing import List, Tuple


def test_import(module_path: str, names: List[str]) -> Tuple[bool, str]:
    """Test importing specific names from a module.
    
    Args:
        module_path: Module to import from (e.g., 'agent_framework')
        names: List of names to import (e.g., ['ChatMessage', 'Role'])
        
    Returns:
        Tuple of (success, message)
    """
    try:
        module = __import__(module_path, fromlist=names)
        for name in names:
            if not hasattr(module, name):
                return False, f"Module '{module_path}' doesn't have '{name}'"
        return True, f"✅ {module_path}: {', '.join(names)}"
    except ImportError as e:
        return False, f"❌ {module_path}: {e}"
    except Exception as e:
        return False, f"❌ {module_path}: Unexpected error: {e}"


def main() -> int:
    """Run all import tests and return exit code."""
    print("=" * 70)
    print("🔍 Agent Framework Installation Verification")
    print("=" * 70)
    print()
    
    tests = [
        # Core types
        ("agent_framework", ["ChatMessage", "Role"]),
        ("agent_framework", ["AgentThread", "AgentRunResponse"]),
        ("agent_framework", ["BaseAgent", "ChatAgent"]),
        
        # Workflow components
        ("agent_framework", ["Executor", "WorkflowBuilder", "WorkflowContext", "handler"]),
        ("agent_framework", ["Workflow", "WorkflowAgent", "WorkflowExecutor"]),
        
        # Tools
        ("agent_framework", ["ai_function", "AIFunction"]),
        
        # Observability
        ("agent_framework.observability", ["setup_observability", "get_tracer"]),
        
        # Azure OpenAI integration (optional)
        ("agent_framework.azure", ["AzureOpenAIChatClient"]),
        ("agent_framework.azure", ["AzureOpenAIAssistantsClient", "AzureOpenAIResponsesClient"]),
        
        # Azure AI integration (optional)
        ("agent_framework.azure", ["AzureAIAgentClient", "AzureAISettings"]),
        
        # DevUI (optional)
        ("agent_framework.devui", ["serve"]),
    ]
    
    results = []
    for module_path, names in tests:
        success, message = test_import(module_path, names)
        results.append((success, message))
        print(message)
    
    print()
    print("=" * 70)
    
    # Summary
    passed = sum(1 for success, _ in results if success)
    total = len(results)
    
    if passed == total:
        print(f"🎉 SUCCESS: All {total} import tests passed!")
        print()
        print("Your agent_framework installation is working correctly.")
        print("You can now run your workflow scripts.")
        print()
        print("Try:")
        print("  python AQ-CODE/orchestration/healthcare_product_launch_devui.py")
        return 0
    else:
        print(f"⚠️  PARTIAL: {passed}/{total} import tests passed")
        print()
        if passed >= 5:  # Core components work
            print("Core components work, but some optional integrations failed.")
            print("This is OK if you're not using those integrations.")
        else:
            print("Core components failed to import. Please check the installation:")
            print()
            print("  pip install -e python/packages/core")
            print()
            print("Or for full installation:")
            print("  pip install -e python")
        return 1


if __name__ == "__main__":
    sys.exit(main())
