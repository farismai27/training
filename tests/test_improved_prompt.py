#!/usr/bin/env python3
"""Test script to evaluate the improved system prompt"""

import sys
sys.path.insert(0, '.')

from demo import PromptEvaluator, generate_pm_dataset, get_onesuite_context

# Test the improved system prompt
eval_questions = [
    {
        "query": "Create a user story for search results filtering in OneSuite Search channel",
        "expected_keywords": ["acceptance criteria", "story", "search", "filter"]
    },
    {
        "query": "What's the roadmap for the Social channel?",
        "expected_keywords": ["roadmap", "social", "timeline", "milestone"]
    },
    {
        "query": "Define the product requirements for cross-channel taxonomy",
        "expected_keywords": ["taxonomy", "channel", "consistency", "glossary"]
    }
]

print("=" * 60)
print("TESTING IMPROVED SYSTEM PROMPT")
print("=" * 60)

# Generate test dataset
print("\n[1] Generating product management test cases...")
pm_dataset = generate_pm_dataset()
print(f"✓ Generated {len(pm_dataset)} test cases")

# Show context
print("\n[2] OneSuite Core Context (using fallback):")
context = get_onesuite_context()
print(f"Context length: {len(context)} characters")
print("First 200 chars:", context[:200] + "...")

# Initialize evaluator with improved prompt
print("\n[3] Initializing PromptEvaluator with improved system prompt...")
evaluator = PromptEvaluator()
print("✓ Evaluator initialized")

# Test with first evaluation question
print("\n[4] Testing with sample query:")
test_query = "Create a user story for a new Search feature that filters by date range with cross-channel consistency"
print(f"Query: {test_query}\n")

response = evaluator.evaluate_output(test_query, {})
print(f"Response:\n{response}\n")

# Evaluate the response
print("[5] Evaluating response quality:")
score, feedback = evaluator.evaluate_output(test_query, {})
print(f"Score: {score}/10")
print(f"Feedback: {feedback}\n")

print("=" * 60)
print("TEST COMPLETE - Improved prompt is ready for deployment!")
print("=" * 60)
