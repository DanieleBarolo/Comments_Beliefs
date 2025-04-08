''' new document instead of generate_batch.py '''

import json
import numpy as np
from targets import target_list
from prompts.prompts_builder import *
from utils import *
from setup import *
import os
from datetime import datetime
import yaml
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# def get_model_schema(prompt_type):
    
#     if prompt_type == 'open_target': 
#         model_json_schema = FullStancesOT.model_json_schema()
#     elif prompt_type == 'closed_target': 
#         model_json_schema = FullStancesCT.model_json_schema()
#     elif prompt_type == 'closed_target_new':
#         model_json_schema = FullStancesCTN.model_json_schema()
        
#     return model_json_schema 

def write_jsonl_line(target_comment_id, llm_name_groq, user_content, default_sys_prompt, temperature):

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
            "response_format": {"type": "json_object"}, # modified from "response_model"
            "temperature": temperature
        }
    }
    return jsonl_line 

################################################################################
# we might want to change the sampling method here
################################################################################
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

def write_text_prompt_from_comment_data(
    prompt_type, 
    article_title_text,
    article_body_text,
    parent_comment_text,
    oldest_comment_text,
    liked_comment_text,
    target_comment_text,
    comment_date,
    target_list=False
): 
    """"
    return the prompt for that given comment
    """
    kwargs = {
        'article_title': article_title_text, # for ablation study
        'article_body': article_body_text,
        'parent_comment': parent_comment_text,
        'oldest_comment': oldest_comment_text,
        'most_liked_comment': liked_comment_text,
        'target_comment': target_comment_text, # for abltion study 
        'comment_date': comment_date,
    }

    if prompt_type == "open_target": 
        user_content = write_prompt_ot(**kwargs)

    elif prompt_type == "closed_target":
        user_content = write_prompt_ct(**kwargs, targets=target_list)

    else:
        user_content = ''

    return user_content

def write_line(
    file_path, 
    prompt_type,
    default_sys_prompt,
    comment, 
    temperature,
    llm_name_groq = 'deepseek-r1-distill-llama-70b',
    collection_name = 'Breitbart', 
    target_comment = True,
    article_title = True,
    parent_comment = True,
    oldest_comment = False,
    liked_comment = False,
    article_body = False,
    target_list = False):
    
    # initialize collections
    comment_collection = init_mongo(dbs = "Comments", collection = collection_name)
    article_collection = init_mongo(dbs = "Articles", collection = collection_name)

    # comment info 
    target_comment_text = comment.get('raw_message') if target_comment else ''
    target_comment_id = comment.get('_id')
    comment_date = comment.get('createdAt')
    
    # article title 
    article_id = comment.get('art_id')
    
    article_obj = article_collection.find_one({'_id': article_id})
    article_title_text = article_obj.get('clean_title') if article_title else ''
    
    # retreive artcle body 
    if article_body: 
        article_obj = get_article_text(
            article_id = article_id, 
            collection_name = collection_name)
        article_body_text = article_obj.get('body')
    else: # do we need this?
        article_body_text = ''
    
    # same logic for parent comment
    parent_comment_id = comment.get('parent')
    parent_comment_obj = comment_collection.find_one({'_id': parent_comment_id})
    oldest_comment_obj = comment_collection.find_one(
        {'art_id': article_id},
        sort=[('createdAt', 1)] # is it really 1 here and not 0?
    )
    liked_comment_obj = comment_collection.find_one(
        {'art_id': article_id},
        sort=[('likes', -1)]
    )
    
    # context around comments 
    parent_comment_text = parent_comment_obj.get('raw_message') if parent_comment and parent_comment_obj else ''
    oldest_comment_text = oldest_comment_obj.get('raw_message') if oldest_comment and oldest_comment_obj else ''
    liked_comment_text = liked_comment_obj.get('raw_message') if liked_comment and liked_comment_obj else ''
    
    # user content (main prompt)
    user_content = write_text_prompt_from_comment_data(
        prompt_type, 
        article_title_text,
        article_body_text,
        parent_comment_text,
        oldest_comment_text,
        liked_comment_text,
        target_comment_text,
        comment_date,
        target_list) 

    # json line (combining everything)
    jsonl_line = write_jsonl_line(target_comment_id, llm_name_groq, user_content, default_sys_prompt, temperature)
    
    # write 
    with open(file_path, "a") as f:
        f.write(json.dumps(jsonl_line) + "\n")



################################################################################
# Change by using the config file
################################################################################   

def write_jsonl_file(config_file_path):

    with open(f"data/experiments/configs/{config_file_path}.yaml", 'r') as f:
        config = yaml.safe_load(f)


    user_id = config.get('user', {}).get('user_id')
    llm_name_groq = config.get('api', {}).get('groq', {}).get('model', "deepseek-r1-distill-llama-70b")
    temperature = config.get('api', {}).get('groq', {}).get('temperature', 0)

    prompt_type = config.get('prompts', {}).get('type', "closed_target")
    default_sys_prompt = config.get('prompts', {}).get('system_prompt')

    batch_size = config.get('data', {}).get('batch_size', 100)
    collection_name = config.get('data', {}).get('collection_name', "Breitbart")

    article_body = config.get('context', {}).get('include_article_body')
    most_liked_comment = config.get('context', {}).get('include_most_liked_comment')
    parent_comment = config.get('context', {}).get('include_parent_comment')
    oldest_comment = config.get('context', {}).get('include_oldest_comment')


    # sample comments
    comment_collection = init_mongo(dbs = "Comments", collection = collection_name)
    comments = comment_collection.find({"user_id": user_id})
    sampled_comments = sample_comments(comments, batch_size)

    file_path = "data/experiments/batches"
    save_path = os.path.join(file_path, f"{config_file_path}.jsonl")

    target_list = config.get('prompts', {}).get('targets')

    # write jsonl file
    for comment in sampled_comments:
        write_line(
            save_path,
            prompt_type,
            default_sys_prompt,
            comment,
            temperature,
            llm_name_groq=llm_name_groq,
            collection_name=collection_name, 
            target_comment = True,  # default
            article_title = True, #default
            parent_comment = parent_comment,
            oldest_comment = oldest_comment,
            liked_comment = most_liked_comment,
            article_body = article_body,
            target_list=target_list)

if __name__ == "__main__":
    write_jsonl_file("exp_00001")