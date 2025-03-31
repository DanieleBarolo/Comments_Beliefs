from llm_caller import call_groq_from_batch
import json
import os
import time
from tqdm import tqdm

##############################################################################
# 0. Setup
###############################################################################

collection_name = "Breitbart"

# Batch Variables
base_dir = "data/batch_files" 
user_id = "31499533" 
# llm_name_groq = "llama-3.3-70b-versatile"
llm_name_groq = "deepseek-r1-distill-llama-70b"
batch_size =  100 # set to "all" if you want all Data in the Batch

# Prompt engeniering 
prompt_type = "closed_target"  # choose among ["open_target", "closed_target", "closed_target_new"]

# For Ablation studies
article_body = True # Set to False if you want to exclude body in the prompts
parent_comment = True # Set to False if you want to exclude parent comment in the prompts

from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d")

##############################################################################

os.makedirs(base_dir, exist_ok=True)  # Ensure base directory exists
# Subdirectory structure
user_dir = os.path.join(base_dir, user_id)
model_dir = os.path.join(user_dir, llm_name_groq)
prompt_dir = os.path.join(model_dir, prompt_type) 
date_dir = os.path.join(prompt_dir, timestamp)
# Ensure directories exist
os.makedirs(date_dir, exist_ok=True)
# Generate filename dynamically
batch_str = f"batch_size_{batch_size}"
article_str = "with_body" if article_body else "no_body"
parent_str = "with_parent" if parent_comment else "no_parent"

file_type = "jsonl"
file_name = f"{batch_str}_{article_str}_{parent_str}.{file_type}"
file_path = os.path.join(date_dir, file_name)

##############################################################################

results_dir = "data/results"
os.makedirs(results_dir, exist_ok=True)
result_user_dir = os.path.join(results_dir, user_id)
result_model_dir = os.path.join(result_user_dir, llm_name_groq)
result_prompt_dir = os.path.join(result_model_dir, prompt_type) 
result_date_dir = os.path.join(result_prompt_dir, timestamp)
# Generate results directory
os.makedirs(result_date_dir , exist_ok=True)

# dir + file 
results_path = os.path.join(result_date_dir, file_name)
# Initialize counters
counter = 0
start_time = time.time()
temperature = 0.5

# Process file
with open(file_path, "r", encoding="utf-8") as infile, open(results_path, "w", encoding="utf-8") as outfile:
    for line in tqdm(infile, desc="Processing batch", unit="line"):
        data = json.loads(line.strip())  # Read and parse each line
        
        try:
            response = call_groq_from_batch(data, temp=temperature)  # Call function
            
            # Format output
            result = {
                "id": response.id,  # Use response ID
                "custom_id": data["custom_id"],  # Keep the original custom_id
                "response": {
                    "status_code": 200,
                    "request_id": response.x_groq.get("id", "unknown_request_id"),  # Use correct request ID
                    "body": response.model_dump()  # Convert response to dict
                },
                "error": None
            }
        
        except Exception as e:
            result = {
                "id": "error",
                "custom_id": data["custom_id"],
                "response": None,
                "error": str(e)  # Store error message
            }
            print(f"Error processing request {data['custom_id']}: {e}")

        # Write result to file
        outfile.write(json.dumps(result) + "\n")

        # Update counter
        counter += 1

        # Check if we reached the limit
        if counter == 30:
            elapsed_time = time.time() - start_time
            remaining_time = 60 - elapsed_time

            if remaining_time > 0:
                print(f"Reached 30 calls. Waiting {remaining_time:.2f} seconds...")
                time.sleep(remaining_time)

            # Reset counter and timer
            counter = 0
            start_time = time.time()

print(f"Processing complete. Results saved to {results_path}")
