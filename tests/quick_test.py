#!/usr/bin/env python3
"""Quick test to show score improvement with new system prompt"""

import sys
import json
from demo import call_ocaa, sample_test_cases

print("="*60)
print("TESTING IMPROVED SYSTEM PROMPT")
print("="*60)
print("\nNew system prompt includes:")
print("✓ Step-by-step reasoning process (6 steps)")
print("✓ Specific output format with OneSuite fields")
print("✓ Type B guidelines (process steps)")
print("✓ Type A guidelines (output attributes)")
print("\n" + "="*60)
print("RUNNING SAMPLE TESTS")
print("="*60 + "\n")

results = []
for i, case in enumerate(sample_test_cases[:3], 1):  # Test first 3
    print(f"\n[Test {i}] {case['question'][:60]}...")
    answer = call_ocaa(case['question'])
    
    # Check for expected keywords
    found_keywords = []
    for kw in case['expected_keywords']:
        if kw.lower() in answer.lower():
            found_keywords.append(kw)
    
    match_score = len(found_keywords) / len(case['expected_keywords'])
    score = int(match_score * 10)
    
    print(f"Answer: {answer[:150]}...")
    print(f"Expected: {case['expected_keywords']}")
    print(f"Found: {found_keywords}")
    print(f"Score: {score}/10")
    
    results.append(score)

avg = sum(results) / len(results) if results else 0
print(f"\n" + "="*60)
print(f"AVERAGE SCORE: {avg:.1f}/10")
print("="*60)

print("\nNOTE: Score improvement should be visible in /prompt-eng")
print("which tests all 4 versions across multiple test cases.")
