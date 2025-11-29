#!/usr/bin/env python3
"""
Quick test script to verify NL2SQL workflow functionality
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_workflow():
    """Test the workflow with a sample question."""
    from nl2sql_workflow import create_nl2sql_workflow, NL2SQLInput
    
    print("=" * 80)
    print("🧪 Testing NL2SQL Workflow")
    print("=" * 80)
    print()
    
    # Create workflow
    print("📦 Creating workflow...")
    workflow = await create_nl2sql_workflow()
    print("✅ Workflow created")
    print()
    
    # Test question
    test_question = "What are the top 5 customers by annual revenue?"
    print(f"❓ Test Question: {test_question}")
    print()
    
    # Create input
    input_data = NL2SQLInput(question=test_question)
    
    # Run workflow
    print("🚀 Running workflow...")
    print("─" * 80)
    
    try:
        result = await workflow.run(input_data)
        
        print()
        print("─" * 80)
        print("✅ Workflow completed successfully!")
        print()
        print("📊 Result:")
        print(result)
        print()
        print("=" * 80)
        print("✅ TEST PASSED - Workflow is ready for demos!")
        print("=" * 80)
        
    except Exception as e:
        print()
        print("─" * 80)
        print(f"❌ Workflow failed: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        raise

if __name__ == "__main__":
    asyncio.run(test_workflow())
