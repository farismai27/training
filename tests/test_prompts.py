#!/usr/bin/env python3
"""Test MCP Prompts implementation."""

import asyncio
from mcp import ClientSession


async def test_prompts():
    """Test MCP prompts from the document server."""
    
    # Start the document server process
    proc = await asyncio.create_subprocess_exec(
        ".venv/Scripts/python",
        "document_server.py",
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        cwd="."
    )
    
    read = proc.stdout
    write = proc.stdin
    
    try:
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            print("=" * 60)
            print("Testing MCP Prompts Implementation")
            print("=" * 60)
            
            # Test 1: List prompts
            print("\n1. Testing list_prompts()")
            try:
                result = await session.list_prompts()
                if result and hasattr(result, 'prompts'):
                    print(f"   Found {len(result.prompts)} prompt(s):")
                    for prompt in result.prompts:
                        print(f"   - {prompt.name}: {prompt.description}")
                    print("   Status: PASS")
                else:
                    print("   Status: FAIL (no prompts)")
            except Exception as e:
                print(f"   Error: {e}")
                print("   Status: FAIL")
            
            # Test 2: Get format prompt with arguments
            print("\n2. Testing get_prompt('format', {'doc_id': 'document1'})")
            try:
                result = await session.get_prompt("format", {"doc_id": "document1"})
                if result:
                    print(f"   Description: {result.description}")
                    print(f"   Messages: {len(result.messages)} message(s)")
                    if result.messages:
                        msg = result.messages[0]
                        print(f"   Role: {msg.role}")
                        print(f"   Content preview: {str(msg.content.text)[:100]}...")
                    print("   Status: PASS")
                else:
                    print("   Status: FAIL (no result)")
            except Exception as e:
                print(f"   Error: {e}")
                print("   Status: FAIL")
            
            print("\n" + "=" * 60)
            print("Prompt Testing Complete")
            print("=" * 60)
    finally:
        try:
            proc.terminate()
            await asyncio.wait_for(proc.wait(), timeout=5)
        except:
            proc.kill()
            await proc.wait()


if __name__ == "__main__":
    asyncio.run(test_prompts())
