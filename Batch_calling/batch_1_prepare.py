''' new document instead of generate_batch.py '''

import json
import os
import numpy as np
from targets import target_list
from prompts_builder import *
from utils import *
from setup import FullStancesCT, FullStancesOT
from datetime import datetime

def create_dir(base_dir, user_id, llm_name_groq, prompt_type, timestamp):
    
    # basedirectory  
    os.makedirs(base_dir, exist_ok=True) 
    
    # subdirectory 
    user_dir = os.path.join(base_dir, user_id)
    model_dir = os.path.join(user_dir, llm_name_groq)
    prompt_dir = os.path.join(model_dir, prompt_type) 
    date_dir = os.path.join(prompt_dir, timestamp)
    os.makedirs(date_dir, exist_ok=True)

    return date_dir

def create_filename(batch_size, article_body, directory):

    # generate filename 
    batch_str = f"batch_size_{batch_size}"
    article_str = "with_body" if article_body else "no_body"
    context_str = "with_context" if article_comments else "no_parent"
    file_type = "jsonl"
    file_name = f"{batch_str}_{article_str}_{context_str}.{file_type}"
    file_path = os.path.join(directory, file_name)
    
    # remove file if exists
    if os.path.isfile(file_path): 
        os.remove(file_path)
    
    return file_path 

def get_model_schema(prompt_type):
    
    if prompt_type == 'open_target': 
        model_json_schema = FullStancesOT.model_json_schema()
    elif prompt_type == 'closed_target': 
        model_json_schema = FullStancesCT.model_json_schema()
    elif prompt_type == 'closed_target_new':
        model_json_schema = FullStancesCTN.model_json_schema()
        
    return model_json_schema 

def write_jsonl_line(target_comment_id, llm_name_groq, user_content, model_json_schema):
    default_sys_prompt = """"
You are an advanced stance classification AI that analyzes news comments. 
Your task is to determine the stance of a given comment toward specified targets. 
Be precise, objective, and base your stance classification on clear textual evidence. 
Only return output in valid JSON format, strictly following the specified schema.
"""

    # Create the line to be written to the file
    jsonl_line = {
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
    return jsonl_line 

def sample_comments(comments, batch_size): 
    sorted_comments = list(comments.sort("createdAt", 1))

    # Handle batch_size logic
    if batch_size == "all" or batch_size >= len(sorted_comments):
        sampled_comments = sorted_comments  # Use all comments
    else:
        # Select batch_size evenly distributed samples (it is already sorted by time)
        indices = np.linspace(0, len(sorted_comments) - 1, batch_size, dtype=int)
        sampled_comments = [sorted_comments[i] for i in indices]
    
    return sampled_comments

def get_user_content(
    prompt_type, 
    article_title,
    article_body,
    parent_comment_text,
    oldest_comment_text,
    liked_comment_text,
    target_comment_text,
    comment_date,
    target_list=False
): 
    kwargs = {
        'article_title': article_title,
        'article_body': article_body,
        'parent_comment': parent_comment_text,
        'oldest_comment': oldest_comment_text,
        'most_liked_comment': liked_comment_text,
        'target_comment': target_comment_text,
        'comment_date': comment_date,
    }

    if prompt_type == "open_target": 
        user_content = write_prompt_ot(**kwargs)

    elif prompt_type == "closed_target":
        user_content = write_prompt_ct(**kwargs, targets=target_list)

    elif prompt_type == "closed_target_new":
        user_content = write_prompt_ct_new(**kwargs, targets=target_list)

    else:
        user_content = ''

    return user_content

def write_line(
    file_path, 
    prompt_type,
    comment, 
    article_collection, 
    llm_name_groq = 'deepseek-r1-distill-llama-70b',
    collection_name = 'Breitbart', 
    article_comments = True,
    article_body = False,
    target_list = False):
    
    parent_comment = ''
    oldest_comment = ''
    liked_comment = ''
    
    # comment info 
    target_comment_text = comment.get('raw_message')
    target_comment_id = comment.get('_id')
    comment_date = comment.get('createdAt')
    
    # article title 
    article_id = comment.get('art_id')
    article_obj = article_collection.find_one({'_id': article_id})
    article_title = article_obj.get('clean_title')
    
    # retreive artcle body 
    if article_body: 
        article_obj = get_article_text(
            article_id = article_id, 
            collection_name = collection_name)
        article_body = article_obj.get('body')
    else: # do we need this?
        article_body = ''
    
    # same logic for parent comment
    if article_comments: 
        parent_comment_id = comment.get('parent')
        parent_comment = comment_collection.find_one({'_id': parent_comment_id})
        oldest_comment = comment_collection.find_one(
            {'art_id': article_id},
            sort=[('createdAt', 1)] # is it really 1 here and not 0?
        )
        liked_comment = comment_collection.find_one(
            {'art_id': article_id},
            sort=[('likes', -1)]
        )
    
    # context around comments 
    parent_comment_text = parent_comment.get('raw_message') if parent_comment else ''
    oldest_comment_text = oldest_comment.get('raw_message') if oldest_comment else ''
    liked_comment_text = liked_comment.get('raw_message') if liked_comment else ''
    
    # user content (main prompt)
    user_content = get_user_content(
        prompt_type, 
        article_title,
        article_body,
        parent_comment_text,
        oldest_comment_text,
        liked_comment_text,
        target_comment_text,
        comment_date,
        target_list) 

    # json line (combining everything)
    jsonl_line = write_jsonl_line(target_comment_id, llm_name_groq, user_content, model_json_schema)
    
    # write 
    with open(file_path, "a") as f:
        f.write(json.dumps(jsonl_line) + "\n")

# setup 
collection_name = "Breitbart" 
base_dir = "data/batch_files" 
user_id = "31499533" #user_id for "1Tiamo" 
llm_name_groq = "deepseek-r1-distill-llama-70b" 
batch_size = 500 # set to "all" if you want all Data in the Batch
prompt_type = "closed_target" # choose among ["open_target", "closed_target", "closed_target_new"]
targets_list = target_list # Pass the list of Closed Targets IFF prompt_type = "Closed Target"
article_body = False 
article_comments = True 
timestamp = datetime.now().strftime("%Y-%m-%d-%m")

# paths 
directory = create_dir(
    base_dir,
    user_id,
    llm_name_groq,
    prompt_type,
    timestamp
)
file_path = create_filename(
    batch_size,
    article_body,
    directory
)

# comments, articles, model schema
comment_collection = init_mongo(dbs = "Comments", collection = collection_name)
comments = comment_collection.find({"user_id": user_id})
sampled_comments = sample_comments(comments, batch_size) # sample comments
model_json_schema = get_model_schema(prompt_type)
article_collection = init_mongo(dbs = "Articles", collection = collection_name)

for comment in sampled_comments: 
    write_line(
        file_path,
        prompt_type,
        comment,
        article_collection,
        llm_name_groq=llm_name_groq, # default
        collection_name=collection_name, #default
        article_comments=article_comments, # default
        article_body=article_body, #default
        target_list=target_list
    )
