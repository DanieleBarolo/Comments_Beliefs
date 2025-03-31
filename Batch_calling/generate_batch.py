##############################################################################
# Loadings 
##############################################################################
import json
import os
import numpy as np
from targets import target_list
from prompts_builder import *
from utils import *
from setup import FullStancesCT, FullStancesOT

##############################################################################
# 0. Setup
###############################################################################
collection_name = "Breitbart"

# Batch Variables
base_dir = "data/batch_files" 
user_id = "31499533" #user_id for "1Tiamo"
# llm_name_groq = "llama-3.3-70b-versatile" 
llm_name_groq = "deepseek-r1-distill-llama-70b"
batch_size = 100 # set to "all" if you want all Data in the Batch

# Prompt engeniering 
prompt_type = "closed_target" # choose among ["open_target", "closed_target", "closed_target_new"]
targets_list = target_list # Pass the list of Closed Targets IFF prompt_type = "Closed Target"

# For Ablation studies
article_body = True # Set to False if you want to exclude body in the prompts
parent_comment = True # Set to False if you want to exclude parent comment in the prompts

# Date string
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d")

# Default system_prompt: 
default_sys_prompt = """"
You are an advanced stance classification AI that analyzes news comments. 
Your task is to determine the stance of a given comment toward specified targets. 
Be precise, objective, and base your stance classification on clear textual evidence. 
Only return output in valid JSON format, strictly following the specified schema.
"""

##############################################################################
# 1. Create Directory where to save the Batch 
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

print(file_path)
# # Create an empty JSONL file (if it doesn’t exist)
# if not os.path.exists(file_path):
#     print(f"Batch file will be saved at: {file_path}")
#     with open(file_path, "w") as f:
#         pass  
# else: 
#     
##############################################################################
# 2. Collect all comments for that user from MONGO DB
##############################################################################

comment_collection = init_mongo(dbs = "Comments", collection = collection_name)
comments = comment_collection.find({"user_id": user_id})

# # Print results
# for comment in comments:
#     print(comment)

##############################################################################
# 3. Select a sub-sample (based on Batch Size) evenly distributed through time
##############################################################################

#sort comments cronologically 
sorted_comments = list(comments.sort("createdAt", 1))

# Handle batch_size logic
if batch_size == "all" or batch_size >= len(sorted_comments):
    sampled_comments = sorted_comments  # Use all comments
else:
    # Select batch_size evenly distributed samples (it is already sorted by time)
    indices = np.linspace(0, len(sorted_comments) - 1, batch_size, dtype=int)
    sampled_comments = [sorted_comments[i] for i in indices]

### pydantic json schema ###
if prompt_type == 'open_target': 
    model_json_schema = FullStancesOT.model_json_schema()
elif prompt_type == 'closed_target': 
    model_json_schema = FullStancesCT.model_json_schema()
elif prompt_type == 'closed_target_new':
    model_json_schema = FullStancesCTN.model_json_schema()

# # Print Output sample
# for comment in sampled_comments:
#     print(comment)
# print(len(sampled_comments))

##############################################################################
# 4. For every comment: Curate Data -> Write Prompt -> Save in the Batch
##############################################################################

# # TOPIC (in case we will need for validation at the end)
# get_topic(comment_id = sampled_comments[0].get("_id"), 
#           full_date = sampled_comments[0].get("createdAt"))

# relevant keys: 'parent', 'raw_message', 'createdAt', 
# sampled_comments[0].get("art_id")

article_collection = init_mongo(dbs = "Articles", collection = collection_name)

for comment in sampled_comments: 
    #  comment infos
    target_comment = comment.get("raw_message")
    target_comment_id = comment.get("_id")
    comment_date = comment.get("createdAt")

    # retrieve article title
    reference_article = article_collection.find_one({"_id": comment.get("art_id")})
    art_tile = reference_article.get("clean_title")

    # If article_body is not False, try to retrieve use article_body
    if article_body: 
        reference_article = get_article_text(article_id = comment.get("art_id"), collection_name=collection_name)
        art_body = reference_article.get("body")
    else:
        art_body = article_body
    
     # Same logic for parent_comment
    par_comment = comment.get("parent") if parent_comment else parent_comment
    
    if prompt_type == "open_target": 
        user_content = write_prompt_ot(art_tile, art_body, par_comment, target_comment, comment_date)

    elif prompt_type == "closed_target":
        user_content = write_prompt_ct(art_tile, art_body, par_comment, target_comment, comment_date, 
                                       targets_list)
    elif prompt_type == "closed_target_new":
        user_content = write_prompt_ct_new(art_tile, art_body, par_comment, target_comment, comment_date,
                                        target_list)
    
    # Create the line to be written to the file
    line_to_write = {
        "custom_id": str(target_comment_id),  # Ensure it's a string 
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": str(llm_name_groq),  # Use the variable passed for the model
            "messages": [
                {"role": "system", "content": default_sys_prompt},  
                {"role": "user", "content": user_content}  # User-generated content
            ],
            "response_model": model_json_schema
        }
    }

    # Write to the file
    with open(file_path, "a") as f:
        f.write(json.dumps(line_to_write) + "\n")

print(f"Batch file {file_path} saved") # change in an error (?)


