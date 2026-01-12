#!/usr/bin/env python3
"""
Interactive test to verify MCP tool execution with the document server.
"""
import subprocess
import sys
import time

# Run demo.py
process = subprocess.Popen(
    [sys.executable, "demo.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    encoding='utf-8',
    errors='replace'  # Handle encoding errors gracefully
)

def send_command(cmd, timeout=15):
    """Send a command and collect output."""
    print(f"\n>>> SENDING: {cmd}")
    print("-" * 70)
    process.stdin.write(cmd + "\n")
    process.stdin.flush()
    
    output_lines = []
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            line = process.stdout.readline()
            if not line:
                break
            output_lines.append(line)
            print(line, end='', flush=True)
            
            # Stop when we see the next prompt
            if "You:" in line and len(output_lines) > 5:
                break
        except Exception as e:
            print(f"[Error reading line: {e}]")
            break
    
    return "".join(output_lines)

try:
    # Wait for initialization (longer timeout for first run)
    print("[Waiting for MCP initialization...]")
    time.sleep(4)
    
    # Test 1: List available MCP tools
    print("\n" + "=" * 70)
    print("TEST 1: List available MCP tools")
    print("=" * 70)
    send_command("/mcp-tools")
    
    time.sleep(1)
    
    # Test 2: Ask Claude to list available documents
    print("\n" + "=" * 70)
    print("TEST 2: Ask Claude to list available documents")
    print("=" * 70)
    send_command("What documents are available in the system? Please use the tools to list them.")
    
    time.sleep(1)
    
    # Test 3: Ask Claude to read kb-guide
    print("\n" + "=" * 70)
    print("TEST 3: Ask Claude to read the kb-guide document")
    print("=" * 70)
    send_command("Can you read the kb-guide document and tell me what it contains?")
    
    time.sleep(1)
    
    # Test 4: Exit
    print("\n" + "=" * 70)
    print("TEST 4: Exit")
    print("=" * 70)
    send_command("exit")
    
finally:
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    print("\n\n[Test Complete]")
