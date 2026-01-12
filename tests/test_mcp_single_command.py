#!/usr/bin/env python3
"""
Simple test: ask Claude to list documents using MCP tools.
"""
import subprocess
import sys
import time

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

# Wait for initialization
print("[Waiting for initialization...]")
time.sleep(5)

# Send command
print("\nSending command to Claude...")
process.stdin.write("Please list all documents using the tools and tell me what each one contains.\n")
process.stdin.flush()

# Read output for 30 seconds
print("\n" + "="*70)
print("OUTPUT:")
print("="*70 + "\n")

start = time.time()
while time.time() - start < 30:
    try:
        line = process.stdout.readline()
        if line:
            print(line, end='')
        else:
            break
    except:
        break

# Send exit
print("\n\nSending exit...")
process.stdin.write("exit\n")
process.stdin.flush()

# Cleanup
process.terminate()
try:
    process.wait(timeout=5)
except:
    process.kill()

print("\n[Done]")
