from llm_caller import call_groq_from_batch
import json
import os

##############################################################################
# 0. Setup
###############################################################################

collection_name = "Breitbart"

# Batch Variables
base_dir = "data/batch_files" 
user_id = "31499533" #user_id for "1Tiamo"
llm_name_groq = "deepseek-r1-distill-llama-70b"
batch_size =  100 # set to "all" if you want all Data in the Batch

# Prompt engeniering 
prompt_type = "open_target" # choose among ["open_target", "closed_target"]
targets_list = None # Pass the list of Closed Targets IFF prompt_type = "Closed Target"

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


# Open the JSONL file and read one line
with open(file_path, "r", encoding="utf-8") as file:
    first_line = file.readline().strip()  # Read the first line and remove trailing newline
    data = json.loads(first_line)  # Convert JSON string to a Python dictionary


##############################################################################

call_groq_from_batch(data, temp=0.5)