#!/usr/bin/env python3
"""Test MCP tool execution with the new thread executor approach."""

import subprocess
import sys
import time

# Run demo.py in the background
process = subprocess.Popen(
    [sys.executable, "demo.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

def send_command(cmd):
    """Send a command to the demo and read output."""
    print(f"\n>>> Sending: {cmd}")
    process.stdin.write(cmd + "\n")
    process.stdin.flush()
    
    # Read output until we see "You:" prompt
    output = []
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line, end='')
        output.append(line)
        if "You:" in line:
            break
        # Safety timeout
        if len(output) > 200:
            break
    return "".join(output)

try:
    # Wait for initialization
    time.sleep(3)
    
    # Test 1: List MCP tools
    print("\n" + "="*70)
    print("TEST 1: List available MCP tools")
    print("="*70)
    send_command("/mcp-tools")
    
    # Test 2: Ask Claude to list documents
    print("\n" + "="*70)
    print("TEST 2: Ask Claude to read a KB document")
    print("="*70)
    send_command("Can you please read the kb-guide document and tell me what's in it?")
    
    # Test 3: Clean exit
    print("\n" + "="*70)
    print("TEST 3: Exit")
    print("="*70)
    send_command("exit")
    
finally:
    process.terminate()
    process.wait(timeout=5)
    print("\n[Test Complete]")
