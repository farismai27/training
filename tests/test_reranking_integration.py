#!/usr/bin/env python3
"""Test that re-ranking demo integrates correctly with demo.py"""

import os
import sys
import traceback

# Add src folder to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_imports():
    """Test that all necessary modules can be imported."""
    print("Testing imports...")
    
    try:
        from hybrid_retriever import RetrieverWithReranking, Retriever, chunk_text_by_section, generate_embeddings_batch
        print("✅ Successfully imported from hybrid_retriever:")
        print("   - RetrieverWithReranking")
        print("   - Retriever")
        print("   - chunk_text_by_section")
        print("   - generate_embeddings_batch")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        from anthropic import Anthropic
        print("✅ Successfully imported Anthropic")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True


def test_retriever_instantiation():
    """Test that RetrieverWithReranking can be instantiated."""
    print("\nTesting RetrieverWithReranking instantiation...")
    
    try:
        from hybrid_retriever import RetrieverWithReranking
        from anthropic import Anthropic
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - skipping client test")
            # Test without client
            retriever = RetrieverWithReranking(client=None)
            print("✅ RetrieverWithReranking instantiated without client")
        else:
            client = Anthropic(api_key=api_key)
            retriever = RetrieverWithReranking(client=client)
            print("✅ RetrieverWithReranking instantiated with Anthropic client")
            print(f"   Client type: {type(client)}")
        
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        traceback.print_exc()
        return False


def test_demo_function_exists():
    """Test that run_reranking_demo function exists and is callable."""
    print("\nTesting run_reranking_demo function...")
    
    try:
        # Read demo.py source
        with open('demo.py', 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        
        # Check for function definition
        if 'def run_reranking_demo():' in source:
            print("✅ run_reranking_demo() function found in demo.py")
        else:
            print("❌ run_reranking_demo() function NOT found in demo.py")
            return False
        
        # Check for /rerank-demo command routing
        if '"/rerank-demo"' in source and 'run_reranking_demo()' in source:
            print("✅ /rerank-demo command routing found in demo.py")
        else:
            print("❌ /rerank-demo command routing NOT found in demo.py")
            return False
        
        # Check for help menu
        if "'/rerank-demo' - Re-ranking with Claude" in source:
            print("✅ /rerank-demo in help menu")
        else:
            print("❌ /rerank-demo NOT in help menu")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_report_file():
    """Test that report.md exists."""
    print("\nTesting report.md...")
    
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            content = f.read()
        print(f"✅ report.md found in data/ folder ({len(content)} characters)")
        return True
    else:
        print("⚠️  report.md not found in data/ folder (needed for demo)")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("RE-RANKING INTEGRATION TEST")
    print("="*70)
    
    results = [
        ("Imports", test_imports()),
        ("Retriever Instantiation", test_retriever_instantiation()),
        ("Demo Function", test_demo_function_exists()),
        ("Report File", test_report_file()),
    ]
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! /rerank-demo is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
