# =========================
# ITERATIVE PROMPT ENGINEERING FRAMEWORK
# =========================
# This module implements the iterative prompt engineering process:
# 1. Set a goal
# 2. Write an initial prompt
# 3. Evaluate the prompt
# 4. Apply prompt engineering techniques
# 5. Re-evaluate and repeat

import os
import json
import re
import statistics
from dotenv import load_dotenv
from anthropic import Anthropic
import ast

# =========================
# SETUP
# =========================
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

client = Anthropic(api_key=api_key)
model = "claude-haiku-4-5"

# =========================
# HELPER FUNCTIONS
# =========================
def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages, system=None, temperature=1.0, stop_sequences=None):
    params = {
        "model": model,
        "max_tokens": 1500,
        "messages": messages,
        "temperature": temperature
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    response = client.messages.create(**params)
    return response.content[0].text

# =========================
# PROMPT EVALUATOR CLASS
# =========================
class PromptEvaluator:
    def __init__(self, max_concurrent_tasks=3):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.evaluation_history = []
    
    def generate_dataset(self, task_description, prompt_inputs_spec, output_file, num_cases=3):
        """
        Generate test cases for prompt evaluation.
        
        Args:
            task_description: What the prompt should accomplish
            prompt_inputs_spec: Dict of input field names and descriptions
            output_file: Where to save the dataset
            num_cases: Number of test cases to generate
        """
        print(f"Generating {num_cases} test cases for: {task_description}")
        
        spec_str = "\n".join([f"- {key}: {desc}" for key, desc in prompt_inputs_spec.items()])
        
        prompt = f"""
You are a test case generator. Generate {num_cases} diverse test cases for the following task:

Task: {task_description}

Each test case should include:
{spec_str}

Generate the test cases as a JSON array. Each object should have fields matching the input spec above.
Example format:
[
  {{{", ".join([f'"{key}": "value"' for key in prompt_inputs_spec.keys()])}}}
]

Generate diverse, realistic test cases that will thoroughly test the prompt.
"""
        
        messages = []
        add_user_message(messages, prompt)
        add_assistant_message(messages, "```json")
        text = chat(messages, stop_sequences=["```"])
        
        try:
            dataset = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing dataset: {e}")
            print(f"Raw output: {text}")
            return None
        
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Dataset saved to {output_file}")
        return dataset
    
    def evaluate_output(self, test_case, output, extra_criteria=""):
        """
        Grade a prompt output using the LLM as a judge.
        
        Args:
            test_case: The input test case
            output: The model's output to evaluate
            extra_criteria: Additional evaluation criteria
        """
        test_case_str = json.dumps(test_case, indent=2)
        
        eval_prompt = f"""You are an expert evaluator. Grade the following output based on how well it meets the requirements.

Input:
{test_case_str}

Output to Evaluate:
{output}

Evaluation Criteria:
- Completeness: Does it address all inputs and requirements?
- Quality: Is the output well-structured and useful?
- Accuracy: Is the information correct and relevant?
{f"Additional Criteria:{extra_criteria}" if extra_criteria else ""}

Respond with ONLY valid JSON (no other text):
{{
  "score": <number 1-10>,
  "strengths": [<list of 1-3 key strengths>],
  "weaknesses": [<list of 1-3 key areas for improvement>],
  "reasoning": "<brief explanation of the score>"
}}
"""
        
        messages = []
        add_user_message(messages, eval_prompt)
        add_assistant_message(messages, "```json")
        eval_text = chat(messages, stop_sequences=["```"])
        
        try:
            eval_text = eval_text.strip()
            if eval_text.startswith('```json'):
                eval_text = eval_text[7:]
            if eval_text.startswith('```'):
                eval_text = eval_text[3:]
            if eval_text.endswith('```'):
                eval_text = eval_text[:-3]
            return json.loads(eval_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing evaluation: {e}")
            return {
                "score": 5,
                "strengths": [],
                "weaknesses": ["Could not evaluate"],
                "reasoning": f"Parse error: {str(e)}"
            }
    
    def run_evaluation(self, run_prompt_function, dataset_file, extra_criteria=""):
        """
        Run evaluation on a dataset using a prompt function.
        
        Args:
            run_prompt_function: Function that takes test_case and returns output
            dataset_file: Path to dataset JSON file
            extra_criteria: Additional evaluation criteria
        
        Returns:
            Results with scores and detailed feedback
        """
        print(f"\n{'='*60}")
        print("RUNNING EVALUATION")
        print(f"{'='*60}\n")
        
        with open(dataset_file, 'r') as f:
            dataset = json.load(f)
        
        results = []
        scores = []
        
        for i, test_case in enumerate(dataset):
            print(f"Test Case {i+1}/{len(dataset)}")
            print(f"Input: {json.dumps(test_case, indent=2)}")
            
            # Run the prompt
            output = run_prompt_function(test_case)
            print(f"Output: {output[:200]}...\n" if len(output) > 200 else f"Output: {output}\n")
            
            # Evaluate the output
            evaluation = self.evaluate_output(test_case, output, extra_criteria)
            score = evaluation.get('score', 5)
            scores.append(score)
            
            print(f"Score: {score}/10")
            print(f"Strengths: {', '.join(evaluation.get('strengths', []))}")
            print(f"Weaknesses: {', '.join(evaluation.get('weaknesses', []))}")
            print(f"Reasoning: {evaluation.get('reasoning', '')}\n")
            
            results.append({
                "test_case": test_case,
                "output": output,
                "evaluation": evaluation
            })
        
        avg_score = statistics.mean(scores)
        print(f"{'='*60}")
        print(f"AVERAGE SCORE: {avg_score:.2f}/10")
        print(f"{'='*60}\n")
        
        # Store in history
        self.evaluation_history.append({
            "average_score": avg_score,
            "results": results,
            "timestamp": str(os.popen("date").read().strip())
        })
        
        return {
            "average_score": avg_score,
            "results": results
        }
    
    def show_history(self):
        """Display evaluation history showing improvements."""
        print(f"\n{'='*60}")
        print("EVALUATION HISTORY")
        print(f"{'='*60}\n")
        
        for i, eval_run in enumerate(self.evaluation_history):
            print(f"Evaluation {i+1}: {eval_run['average_score']:.2f}/10")
        
        if len(self.evaluation_history) > 1:
            first = self.evaluation_history[0]['average_score']
            last = self.evaluation_history[-1]['average_score']
            improvement = last - first
            print(f"\nImprovement: {improvement:+.2f} points")
        
        print()

# =========================
# PROMPT ENGINEERING TECHNIQUES
# =========================

TECHNIQUE_1_STRUCTURE = """
TECHNIQUE 1: Clear Structure
- Break down the task into clear sections
- Use explicit formatting (headers, lists, steps)
- Make expectations obvious
"""

TECHNIQUE_2_EXAMPLES = """
TECHNIQUE 2: Few-Shot Examples
- Include 1-2 example input/output pairs
- Show exactly what good output looks like
- Help the model understand the pattern
"""

TECHNIQUE_3_CONSTRAINTS = """
TECHNIQUE 3: Explicit Constraints
- State exactly what to include/exclude
- Specify format requirements
- Add validation rules
"""

TECHNIQUE_4_PERSONA = """
TECHNIQUE 4: Persona/Role
- Give the model a specific role (e.g., "You are an expert nutritionist")
- Set context for the task
- Guide reasoning style
"""

TECHNIQUE_5_CHAIN_OF_THOUGHT = """
TECHNIQUE 5: Chain of Thought
- Ask the model to explain its reasoning
- Break complex tasks into steps
- Help the model think through the problem
"""

# =========================
# EXAMPLE: MEAL PLAN PROMPT
# =========================

# Version 1: Baseline (naive)
def run_prompt_v1_baseline(prompt_inputs):
    """Baseline: Very simple prompt with minimal instruction."""
    prompt = f"""
What should this person eat?

- Height: {prompt_inputs.get('height', '')}
- Weight: {prompt_inputs.get('weight', '')}
- Goal: {prompt_inputs.get('goal', '')}
- Dietary restrictions: {prompt_inputs.get('restrictions', '')}
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

# Version 2: Structure (add clear structure and formatting)
def run_prompt_v2_structure(prompt_inputs):
    """Add clear structure and formatting."""
    prompt = f"""
Create a one-day meal plan for an athlete.

ATHLETE INFORMATION:
- Height: {prompt_inputs.get('height', '')}
- Weight: {prompt_inputs.get('weight', '')}
- Goal: {prompt_inputs.get('goal', '')}
- Dietary restrictions: {prompt_inputs.get('restrictions', '')}

MEAL PLAN REQUIREMENTS:
- Include breakfast, lunch, dinner, and 2 snacks
- For each meal, list: meal name, foods with portions, approximate calories
- Include a daily macronutrient breakdown
- Total daily calories should be appropriate for the athlete's goal and weight

FORMAT YOUR RESPONSE AS:
MEAL 1: [Name]
- Food 1: [portion]
- Food 2: [portion]
Calories: [X]

[Continue for all meals]

DAILY SUMMARY:
- Total Calories: [X]
- Protein: [Xg]
- Carbs: [Xg]
- Fats: [Xg]
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

# Version 3: Add examples
def run_prompt_v3_examples(prompt_inputs):
    """Add few-shot examples."""
    prompt = f"""
Create a one-day meal plan for an athlete.

ATHLETE INFORMATION:
- Height: {prompt_inputs.get('height', '')}
- Weight: {prompt_inputs.get('weight', '')}
- Goal: {prompt_inputs.get('goal', '')}
- Dietary restrictions: {prompt_inputs.get('restrictions', '')}

EXAMPLE OUTPUT:
---
MEAL 1: Protein-Rich Breakfast
- Eggs: 3 large (scrambled)
- Whole wheat toast: 2 slices
- Berries: 1 cup
Calories: 450

MEAL 2: Mid-morning Snack
- Greek yogurt: 150g
- Granola: 30g
Calories: 200

[Continue...]

DAILY SUMMARY:
- Total Calories: 2500
- Protein: 150g
- Carbs: 300g
- Fats: 85g
---

Now create the meal plan for:
- Height: {prompt_inputs.get('height', '')}
- Weight: {prompt_inputs.get('weight', '')}
- Goal: {prompt_inputs.get('goal', '')}
- Dietary restrictions: {prompt_inputs.get('restrictions', '')}

FORMAT YOUR RESPONSE EXACTLY LIKE THE EXAMPLE ABOVE.
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

# Version 4: Add persona + chain of thought
def run_prompt_v4_persona_cot(prompt_inputs):
    """Add expert persona and chain of thought."""
    prompt = f"""
You are a certified sports nutritionist with 10 years of experience creating personalized meal plans for athletes.

Your task is to create a one-day meal plan that:
1. Optimizes for the athlete's specific goal
2. Respects all dietary restrictions
3. Provides balanced macronutrients
4. Includes proper calorie allocation

ATHLETE PROFILE:
- Height: {prompt_inputs.get('height', '')}
- Weight: {prompt_inputs.get('weight', '')}
- Goal: {prompt_inputs.get('goal', '')}
- Dietary restrictions: {prompt_inputs.get('restrictions', '')}

STEP 1: Calculate daily calorie needs based on weight and goal
STEP 2: Design meals that hit macronutrient targets
STEP 3: Ensure all foods comply with dietary restrictions
STEP 4: Format clearly with portions and nutrition info

EXAMPLE OUTPUT:
---
MEAL 1: Protein-Rich Breakfast
- Eggs: 3 large (scrambled)
- Whole wheat toast: 2 slices
- Berries: 1 cup
Calories: 450
Macros: 18g protein, 45g carbs, 12g fat

[Continue...]

DAILY SUMMARY:
- Total Calories: 2500
- Protein: 150g
- Carbs: 300g
- Fats: 85g
---

Now create the optimized meal plan:
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

# =========================
# INTERACTIVE PROMPT ENGINEERING WORKFLOW
# =========================

def run_prompt_engineering_demo():
    """Run the iterative prompt engineering workflow."""
    
    evaluator = PromptEvaluator(max_concurrent_tasks=3)
    
    print("\n" + "="*60)
    print("ITERATIVE PROMPT ENGINEERING DEMO")
    print("="*60 + "\n")
    
    # Step 1: Generate dataset
    print("STEP 1: Setting a Goal and Generating Test Data\n")
    
    dataset = evaluator.generate_dataset(
        task_description="Create a one-day meal plan for an athlete based on their physical profile and goals",
        prompt_inputs_spec={
            "height": "Athlete's height in cm",
            "weight": "Athlete's weight in kg",
            "goal": "Training goal (e.g., weight loss, muscle gain, endurance)",
            "restrictions": "Dietary restrictions (e.g., vegetarian, gluten-free)"
        },
        output_file="meal_plan_dataset.json",
        num_cases=2  # Keep low during development
    )
    
    if dataset is None:
        print("Failed to generate dataset")
        return
    
    print("\n" + "="*60)
    print("STEP 2: Running Baseline Evaluation (Version 1)\n")
    
    results_v1 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v1_baseline,
        dataset_file="meal_plan_dataset.json",
        extra_criteria="""
- Daily caloric total is reasonable for the athlete
- Macronutrient breakdown is provided
- Meals include specific foods and portions
- Plan respects dietary restrictions
"""
    )
    
    input("\nPress Enter to continue to Version 2...")
    
    print("\n" + "="*60)
    print("STEP 3: Applying Technique 1 - Clear Structure (Version 2)\n")
    print(TECHNIQUE_1_STRUCTURE + "\n")
    
    results_v2 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v2_structure,
        dataset_file="meal_plan_dataset.json",
        extra_criteria="""
- Daily caloric total is reasonable for the athlete
- Macronutrient breakdown is provided
- Meals include specific foods and portions
- Plan respects dietary restrictions
"""
    )
    
    input("\nPress Enter to continue to Version 3...")
    
    print("\n" + "="*60)
    print("STEP 4: Applying Technique 2 - Few-Shot Examples (Version 3)\n")
    print(TECHNIQUE_2_EXAMPLES + "\n")
    
    results_v3 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v3_examples,
        dataset_file="meal_plan_dataset.json",
        extra_criteria="""
- Daily caloric total is reasonable for the athlete
- Macronutrient breakdown is provided
- Meals include specific foods and portions
- Plan respects dietary restrictions
"""
    )
    
    input("\nPress Enter to continue to Version 4...")
    
    print("\n" + "="*60)
    print("STEP 5: Applying Technique 4 & 5 - Persona + Chain of Thought (Version 4)\n")
    print(TECHNIQUE_4_PERSONA + TECHNIQUE_5_CHAIN_OF_THOUGHT + "\n")
    
    results_v4 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v4_persona_cot,
        dataset_file="meal_plan_dataset.json",
        extra_criteria="""
- Daily caloric total is reasonable for the athlete
- Macronutrient breakdown is provided
- Meals include specific foods and portions
- Plan respects dietary restrictions
"""
    )
    
    # Show final history
    evaluator.show_history()
    
    print("="*60)
    print("SUMMARY: Iterative Prompt Engineering Workflow Complete")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Started with a naive baseline prompt")
    print("2. Applied engineering techniques one at a time")
    print("3. Measured improvement with each iteration")
    print("4. Each technique should show measurable gains")
    print("\nYou can continue this cycle to further improve your prompt!")

if __name__ == "__main__":
    run_prompt_engineering_demo()
