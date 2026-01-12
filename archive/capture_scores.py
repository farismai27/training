#!/usr/bin/env python3
"""Run prompt engineering evaluation and save scores to CSV table"""

import sys
import csv
import time
from demo import run_iterative_prompt_engineering, PromptEvaluator, generate_pm_dataset
from demo import run_prompt_v1_baseline, run_prompt_v2_structure, run_prompt_v3_examples, run_prompt_v4_persona_cot

print("="*70)
print("PROMPT ENGINEERING EVALUATION - SCORE CAPTURE")
print("="*70 + "\n")

# Generate dataset once
print("Generating test dataset...")
dataset = generate_pm_dataset()

if dataset is None:
    print("Failed to generate dataset")
    sys.exit(1)

print(f"✓ Dataset ready with {len(dataset)} test cases\n")

# Create evaluator
evaluator = PromptEvaluator()

# Version 1
print("Running Version 1: Baseline...")
results_v1 = evaluator.run_evaluation(
    run_prompt_function=run_prompt_v1_baseline,
    dataset_file="pm_dataset.json",
    extra_criteria="Should include clear structure and proper formatting"
)
v1_score = results_v1['average_score']
print(f"V1 Score: {v1_score:.2f}\n")

# Version 2
print("Running Version 2: Structure...")
results_v2 = evaluator.run_evaluation(
    run_prompt_function=run_prompt_v2_structure,
    dataset_file="pm_dataset.json",
    extra_criteria="Should include clear structure and proper formatting"
)
v2_score = results_v2['average_score']
print(f"V2 Score: {v2_score:.2f}\n")

# Version 3
print("Running Version 3: Examples...")
results_v3 = evaluator.run_evaluation(
    run_prompt_function=run_prompt_v3_examples,
    dataset_file="pm_dataset.json",
    extra_criteria="Should include clear structure and proper formatting"
)
v3_score = results_v3['average_score']
print(f"V3 Score: {v3_score:.2f}\n")

# Version 4
print("Running Version 4: Persona + CoT...")
results_v4 = evaluator.run_evaluation(
    run_prompt_function=run_prompt_v4_persona_cot,
    dataset_file="pm_dataset.json",
    extra_criteria="Should include clear structure and proper formatting"
)
v4_score = results_v4['average_score']
print(f"V4 Score: {v4_score:.2f}\n")

# Create score table
print("\n" + "="*70)
print("SCORE SUMMARY TABLE")
print("="*70 + "\n")

scores_data = [
    ["Version", "Description", "Score/10", "Improvement", "% Improvement"],
    ["V1", "Baseline", f"{v1_score:.2f}", "-", "-"],
    ["V2", "Add Structure", f"{v2_score:.2f}", f"{v2_score - v1_score:+.2f}", f"{((v2_score - v1_score) / v1_score * 100):+.1f}%" if v1_score > 0 else "-"],
    ["V3", "Add Examples", f"{v3_score:.2f}", f"{v3_score - v1_score:+.2f}", f"{((v3_score - v1_score) / v1_score * 100):+.1f}%" if v1_score > 0 else "-"],
    ["V4", "Persona + CoT", f"{v4_score:.2f}", f"{v4_score - v1_score:+.2f}", f"{((v4_score - v1_score) / v1_score * 100):+.1f}%" if v1_score > 0 else "-"],
]

# Print table
col_widths = [8, 20, 12, 15, 15]
for row in scores_data:
    print(" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))
    if row == scores_data[0]:
        print("-" * sum(col_widths) + "-" * 4)

# Save to CSV
csv_file = "prompt_eng_scores.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(scores_data)

print(f"\n✓ Scores saved to {csv_file}\n")

# Final summary
print("="*70)
print("ANALYSIS")
print("="*70)
print(f"Total improvement (V4 vs V1): {v4_score - v1_score:+.2f} points")
if v1_score > 0:
    print(f"Percentage improvement: {((v4_score - v1_score) / v1_score * 100):+.1f}%")
print(f"Best version: V4 ({v4_score:.2f}/10)")
print("\nKey techniques added progressively:")
print("  V1 → V2: Structure + OneSuite context")
print("  V2 → V3: Few-shot examples")
print("  V3 → V4: Expert persona + 6-step reasoning process")
