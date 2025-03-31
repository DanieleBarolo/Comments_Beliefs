from llm_caller import call_groq_from_batch
import json
import os
from pricing import GROQ_PRICES
import numpy as np

##############################################################################
# 0. Setup
###############################################################################

collection_name = "Breitbart"

# Batch Variables
base_dir = "data/batch_files" 
user_id = "46279190" 
# llm_name_groq = "llama-3.3-70b-versatile" 
llm_name_groq = "deepseek-r1-distill-llama-70b" 
batch_size =  100 # set to "all" if you want all Data in the Batch

# Prompt engeniering 
prompt_type = "closed_target_new" # choose among ["open_target", "closed_target", "closed_target_new"]

# For Ablation studies
article_body = True # Set to False if you want to exclude body in the prompts
parent_comment = True # Set to False if you want to exclude parent comment in the prompts

##############################################################################

os.makedirs(base_dir, exist_ok=True)  # Ensure base directory exists
# Subdirectory structure
user_dir = os.path.join(base_dir, user_id)
model_dir = os.path.join(user_dir, llm_name_groq)
prompt_dir = os.path.join(model_dir, prompt_type) 
# Ensure directories exist
os.makedirs(prompt_dir, exist_ok=True)
# Generate filename dynamically
batch_str = f"batch_size_{batch_size}"
article_str = "with_body" if article_body else "no_body"
parent_str = "with_parent" if parent_comment else "no_parent"

file_type = "jsonl"
file_name = f"{batch_str}_{article_str}_{parent_str}.{file_type}"
file_path = os.path.join(prompt_dir, file_name)


##############################################################################

results_dir = "data/results"
os.makedirs(results_dir, exist_ok=True)
result_user_dir = os.path.join(results_dir, user_id)
result_model_dir = os.path.join(result_user_dir, llm_name_groq)
result_prompt_dir = os.path.join(result_model_dir, prompt_type) 
# Generate results directory
results_path = os.path.join(result_prompt_dir, file_name)


##############################################################################

def estimate_batch_full_cost(results_path):
    """Estimates the total cost for all lines in a JSONL file."""

    tokens_query = []
    costs = []

    with open(results_path, "r") as file:
        for line in file:
            print("error" in line)
            if line.strip():  # Skip empty lines
                data = json.loads(line)

                body = data["response"]["body"]
                model = body["model"]
                tokens_in = body["usage"]["prompt_tokens"]
                tokens_out = body["usage"]["completion_tokens"]

                input_price = GROQ_PRICES[model]["input"]
                output_price = GROQ_PRICES[model]["output"]

                input_cost = tokens_in * input_price
                output_cost = tokens_out * output_price

                tokens_query.append(tokens_in+tokens_out)
                costs.append(input_cost + output_cost)

    return tokens_query, costs

tokens_query, costs = estimate_batch_full_cost(results_path)

sum(costs) * 0.5