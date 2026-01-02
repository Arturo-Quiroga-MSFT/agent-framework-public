#!/usr/bin/env python3
"""
Helper script to save group chat conversations from DevUI.

After running a group chat in DevUI, you can copy the conversation
and save it using this script, or it will automatically detect and
format conversation outputs.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def format_conversation(messages, feature_idea="Group Chat Discussion"):
    """Format conversation into markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output = f"""# Product Feature Review - Group Chat Summary

**Generated:** {timestamp}
**Feature Idea:** {feature_idea}

---

## Complete Conversation

"""
    
    for i, msg in enumerate(messages, 1):
        speaker_emoji = {
            "ProductManager": "💡",
            "TechnicalArchitect": "🔧",
            "UXDesigner": "🎨",
            "BusinessAnalyst": "📊"
        }.get(msg.get("role", ""), "💬")
        
        speaker = msg.get("role", "Unknown")
        content = msg.get("content", "")
        
        output += f"\n### {i}. {speaker_emoji} {speaker}\n\n{content}\n"
    
    return output


def save_conversation(messages, feature_idea="Group Chat Discussion"):
    """Save conversation to file."""
    # Create output directory
    output_dir = Path("workflow_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groupchat_feature_review_{timestamp}.md"
    filepath = output_dir / filename
    
    # Format and save
    content = format_conversation(messages, feature_idea)
    filepath.write_text(content)
    
    print(f"✅ Conversation saved to: {filepath}")
    return filepath


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python save_groupchat_conversation.py <conversation_json_file>")
        print("   or: python save_groupchat_conversation.py --interactive")
        return
    
    if sys.argv[1] == "--interactive":
        print("📋 Paste your conversation (Ctrl+D when done):")
        content = sys.stdin.read()
        try:
            data = json.loads(content)
            save_conversation(data.get("messages", []), data.get("feature_idea", ""))
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
    else:
        # Load from file
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return
        
        data = json.loads(filepath.read_text())
        save_conversation(data.get("messages", []), data.get("feature_idea", ""))


if __name__ == "__main__":
    main()
