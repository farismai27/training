#!/usr/bin/env python3
"""
Test script to verify MCP tool execution in demo.py with the fresh connection approach.
"""
import subprocess
import sys
import time
import threading

def test_demo():
    """Run demo and test MCP tool execution."""
    
    process = subprocess.Popen(
        [sys.executable, "demo.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )
    
    def send_command(cmd, wait_lines=20):
        """Send command and collect output."""
        print(f"\n>>> COMMAND: {cmd}")
        print("-" * 70)
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        
        lines = []
        start = time.time()
        while time.time() - start < 20 and len(lines) < wait_lines:
            try:
                line = process.stdout.readline()
                if not line:
                    break
                lines.append(line)
                print(line, end='')
            except:
                break
        return lines
    
    try:
        # Wait for init
        print("[Waiting for demo to initialize...]")
        time.sleep(4)
        
        # Test 1: List documents
        print("\n" + "="*70)
        print("TEST: Ask Claude to list available documents")
        print("="*70)
        send_command("Please list all available documents using the tools.", wait_lines=30)
        
        time.sleep(1)
        
        # Test 2: Read KB guide
        print("\n" + "="*70)
        print("TEST: Ask Claude to read the kb-guide document")
        print("="*70)
        send_command("Can you read the kb-guide document and tell me what it contains?", wait_lines=30)
        
        time.sleep(1)
        
        # Exit
        print("\n" + "="*70)
        print("Exiting...")
        print("="*70)
        send_command("exit", wait_lines=5)
        
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()
        print("\n[Test Complete]")

if __name__ == "__main__":
    test_demo()
