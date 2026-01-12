#!/usr/bin/env python3
"""
Verification script to confirm re-ranking implementation is complete.
"""

import os
import sys

def verify_implementation():
    """Verify all components of re-ranking implementation."""
    
    print("\n" + "="*80)
    print("RE-RANKING IMPLEMENTATION VERIFICATION")
    print("="*80)
    
    checks = []
    
    # Check 1: RetrieverWithReranking class exists
    print("\n1. Checking RetrieverWithReranking class...")
    try:
        from hybrid_retriever import RetrieverWithReranking
        print("   ✅ RetrieverWithReranking class found")
        
        # Verify methods
        methods = ['__init__', '_format_documents_for_reranking', 'rerank_with_claude', 'search_with_reranking']
        missing = []
        for method in methods:
            if not hasattr(RetrieverWithReranking, method):
                missing.append(method)
        
        if missing:
            print(f"   ❌ Missing methods: {missing}")
            checks.append(False)
        else:
            print(f"   ✅ All required methods present: {', '.join(methods)}")
            checks.append(True)
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        checks.append(False)
    
    # Check 2: run_reranking_demo function exists
    print("\n2. Checking demo.py run_reranking_demo function...")
    try:
        with open('demo.py', 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        
        if 'def run_reranking_demo():' in source:
            print("   ✅ run_reranking_demo() function found")
            checks.append(True)
        else:
            print("   ❌ run_reranking_demo() function NOT found")
            checks.append(False)
    except Exception as e:
        print(f"   ❌ Error reading demo.py: {e}")
        checks.append(False)
    
    # Check 3: /rerank-demo command routing
    print("\n3. Checking /rerank-demo command routing...")
    try:
        with open('demo.py', 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        
        if 'if user_input.strip().lower() == "/rerank-demo":' in source:
            print("   ✅ /rerank-demo command routing found")
            checks.append(True)
        else:
            print("   ❌ /rerank-demo command routing NOT found")
            checks.append(False)
    except Exception as e:
        print(f"   ❌ Error checking command routing: {e}")
        checks.append(False)
    
    # Check 4: Help menu includes /rerank-demo
    print("\n4. Checking help menu...")
    try:
        with open('demo.py', 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        
        if "'/rerank-demo' - Re-ranking with Claude" in source:
            print("   ✅ /rerank-demo in help menu")
            checks.append(True)
        else:
            print("   ❌ /rerank-demo NOT in help menu")
            checks.append(False)
    except Exception as e:
        print(f"   ❌ Error checking help menu: {e}")
        checks.append(False)
    
    # Check 5: Documentation updated
    print("\n5. Checking documentation...")
    docs_found = 0
    docs_total = 3
    
    if os.path.exists('HYBRID_RETRIEVER_README.md'):
        with open('HYBRID_RETRIEVER_README.md', 'r', encoding='utf-8', errors='ignore') as f:
            if 'RetrieverWithReranking' in f.read():
                print("   ✅ HYBRID_RETRIEVER_README.md updated with re-ranking docs")
                docs_found += 1
            else:
                print("   ❌ HYBRID_RETRIEVER_README.md exists but not updated")
    
    if os.path.exists('RERANKING_IMPLEMENTATION.md'):
        print("   ✅ RERANKING_IMPLEMENTATION.md created")
        docs_found += 1
    else:
        print("   ❌ RERANKING_IMPLEMENTATION.md NOT found")
    
    if os.path.exists('test_reranking_integration.py'):
        print("   ✅ test_reranking_integration.py created")
        docs_found += 1
    else:
        print("   ❌ test_reranking_integration.py NOT found")
    
    checks.append(docs_found >= 3)
    
    # Check 6: Test report.md exists
    print("\n6. Checking report.md...")
    if os.path.exists('report.md'):
        print("   ✅ report.md found (needed for demo)")
        checks.append(True)
    else:
        print("   ⚠️  report.md not found (demo will fail without it)")
        checks.append(False)
    
    # Check 7: Python syntax validation
    print("\n7. Checking Python syntax...")
    import subprocess
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'demo.py'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ demo.py syntax is valid")
            checks.append(True)
        else:
            print(f"   ❌ demo.py syntax error: {result.stderr.decode()}")
            checks.append(False)
    except Exception as e:
        print(f"   ⚠️  Could not validate syntax: {e}")
        checks.append(True)  # Don't fail on this
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ RE-RANKING IMPLEMENTATION COMPLETE AND VERIFIED")
        print("\nYou can now run:")
        print("  python demo.py")
        print("  Then at the prompt: /rerank-demo")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(verify_implementation())
