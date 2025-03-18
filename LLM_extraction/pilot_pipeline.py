import numpy as np 
import pandas as pd 
from datetime import datetime
import os 
import pyarrow.feather as feather 
import pyarrow.compute as pc
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import json 
import numpy as np
from utils import trace_comment_thread, get_article_text, load_comments_from_jsonl_gz
from pprint import pprint
from pymongo import MongoClient

def init_mongo(collection): 
    client = MongoClient("mongodb://localhost:27017/")
    comment_db = client["Comments"]
    comment_collection = comment_db[collection]
    return comment_collection

# construct query: # 
def trace_comment_thread(comment_collection, comment_id, parent_id, collection='Breitbart'):

    # Initialize thread tracking lists
    article = None
    article_title = ''
    article_link = ''
    article_body = ''
    parent_text = ''
    
    # retrieve comment
    comment = comment_collection.find_one({"_id": comment_id})
    comment_text = comment.get('raw_message')
    
    # retrieve parent 
    parent = comment_collection.find_one({"_id": parent_id})
    if parent: 
        parent_text = parent.get('raw_message') 
    
    # retrieve article 
    # something to load instead if it exists 
    article_id = str(int(comment['art_id']))
    article = get_article_text(article_id, collection)
    if article: 
        article_title = article.get('title')
        article_link = article.get('link')
        article_body = article.get('body')

    return {
        "article_title": article_title,
        "article_link": article_link,
        "article_body": article_body,
        "parent_id": parent_id,  
        "parent_text": parent_text, 
        "comment_ids": comment_id,
        "comment_texts": comment_text
    }

def top_n_comments(user_name, top_n, base_dir="../selected_users_data/selected_users_comments_compressed"):
    user_df = load_comments_from_jsonl_gz(user_name, base_dir)
    # extract the requested comments 
    user_selection = user_df.head(top_n)
    # get the comment and parent ids
    comm_id, parent_id = user_selection['_id'].tolist(), user_selection['parent'].tolist()
    # clean the parent ids 
    parent_id = ["" if np.isnan(x) else str(int(x)) for x in parent_id]
    return comm_id, parent_id

def get_topic(
    user_name, 
    comment_id, 
    base_dir="../selected_users_data/selected_users_comments_compressed",
    topic_path="/Volumes/Untitled/seungwoong.ha/collmind/transform_global/breitbart/breitbart_new_s3_r19_h225_u20_t10"):
    
    user_df = load_comments_from_jsonl_gz(user_name, base_dir)
    full_date = user_df[user_df['_id'] == comment_id]['createdAt'].iloc[0]
    mmyy = full_date.strftime("%m%y")
    
    arrow_name = f"batch-{mmyy}.arrow"
    topic_table = feather.read_table(os.path.join(topic_path, arrow_name))
    topic_df = topic_table.to_pandas()
    topic_int = topic_df[topic_df['id'] == comment_id]['topic'].iloc[0]
    
    return int(topic_int) 

# first init mongo database comments
comment_collection = init_mongo('Breitbart')

# select a user + get some comments
user_name = '1Tiamo'
base_dir = "../selected_users_data/selected_users_comments_compressed"
top_n = 100
comm_id, parent_id = top_n_comments(user_name, top_n, base_dir)

comment_id = '1000896130'
# retrieve comment
comment = comment_collection.find_one({"_id": comment_id})
comment_text = comment.get('raw_message')

# retrieve article 
# something to load instead if it exists 
article_id = str(int(comment['art_id']))
article = get_article_text(article_id, 'Breitbart')
if article: 
    article_title = article.get('title')
    article_link = article.get('link')
    article_body = article.get('body')


# extract the components of the thread + topic 
comm_list = []
for comment, parent in zip(comm_id, parent_id):
    # get all of the essential components
    # ahh of course this will take a while if we need to fetch many articles.
    comm_dict = trace_comment_thread(comment_collection, comment, parent, collection = 'Breitbart')

    # add user name 
    comm_dict['user_name'] = user_name
    
    # add topic 
    comm_dict['topic'] = get_topic(user_name, comment)

    comm_list.append(comm_dict)

# ... # 



# which topics do we have for this user? 
from collections import Counter
topic_lst = []
for dict_ in comm_list: 
    topic = dict_['topic'] 
    topic_lst.append(topic)
counted = Counter(topic_lst)
sorted_dict = dict(sorted(counted.items(), key=lambda item: item[1], reverse=True))

# # sanity check (sums to 100):
# print(sum(sorted_dict.values()))


# hmmm okay this guy has mostly: 
# -1: no topic
# 1: bullshit topic
# 14: climate change
# 8: god, jesus stuff. 
# ... 

# but sure let us see whether we can "find" the climate + god things. 
topics = [1, 8, 14]
sub_list = []
for topic in topics: 
    sub_list.extend([dict_ for dict_ in comm_list if dict_['topic'] == topic])

# now we need to create the prompt ...


# pipeline: 
background = ...
question = ...

# ['climate', 'warming', 'energy', 'global', 'coal', 'solar', 
# # 'water', 'change', 'carbon', 'fossil']

# count: 26699
# ['god', 'church', 'jesus', 'catholic', 'pope', 'christian', 'bible', 
# 'religion', 'christ', 'christians']

# count: 104974
# ['obama', 'trump', 'democrats', 'election', 'republicans', 'president', 'gop', 
# 'vote', 'party', 'republican']

TARGETS = ["global warming", "fossil fuels", 
           "God", "church",
           "Obama", "Trump"
           ]

def bullet_points_target(targets = TARGETS): 
    return "\n".join(f"•{num}: {target}" for num, target in enumerate(targets))

def generate_context(article_title, article_body, parent_comment, target_comment):
    sections = [
        f"# News comment title:\n{article_title}",
        f"# News comment article:\n{article_body}" if article_body else None,
        f"# News comment directly above the focal comment:\n{parent_comment}" if parent_comment else None,
        ">>> COMMENT UNDER ANALYSIS<<<",
        f"\n{target_comment}",
        ">>> END COMMENT <<<"
    ]
    
    return "\n\n".join(filter(None, sections))

def write_prompt(article_title, article_body, parent_comment, target_comment, targets): 
    prompt = f"""

    ### Overview ###

    Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
    Your task is to analyze the news comment and determine its stances towards specific targets. 
    
    ### Context ###
    {generate_context(article_title, article_body, parent_comment, target_comment)}

    ### Targets ###
    {bullet_points_target(targets)}

    ### Task Description ###

    For each target, determine the stance in the comment:
    - If the stance is in favor of the target, write FAVOR
    - If it is against the target, write AGAINST
    - If it is ambiguous, write NONE
    - If the comment is not related to the target, write NOT RELATED

    ### Explanation ### 
    Together with the stance for a given target, provide evidence-based reasoning that quotes or references specific text from the comment that reveals the commenter's stance toward the target.

    ### Output Format: ###

    You must output only JSON format:
    {{
      "results": [
        {{
          "target": "<original_target>", 
          "stance": "<one among [FAVOR, AGAINST, NONE, NOT RELATED]>", 
          "explanation": "<Brief explanation of the detected stance>"
        }},
        // Repeat for each target
      ]
    }}
    
    ONLY return the JSON object itself.
    """
    return prompt

first_comment = sub_list[0]
first_comment.get('article_title')
from pprint import pprint
pprint(write_prompt(article_title = first_comment.get('article_title'), 
             article_body = first_comment.get('article_body'), 
             parent_comment = first_comment.get('parent_text'), 
             target_comment = first_comment.get('comment_texts'), 
             targets=TARGETS))

####### try with OLLAMA
from llm_caller import call_ollama, FullStances

# Use Pydantic to validate the response
prompt = write_prompt(article_title = first_comment.get('article_title'), 
             article_body = first_comment.get('article_body'), 
             parent_comment = first_comment.get('parent_text'), 
             target_comment = first_comment.get('comment_texts'), 
             targets=TARGETS)
full_response = call_ollama(model_name= 'tinyllama', content_prompt = prompt)
stances_response = FullStances.model_validate_json(full_response.message.content)
print('-' * 50)
print(full_response)
print(full_response.message.content)
print(stances_response)

####### try with GROQ
from llm_caller import call_groq
# List of models to test
GROQ_MODELS_KEYS = [
    'gemma2-9b-it',
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'llama3-70b-8192',
    'deepseek-r1-distill-llama-70b',
    'deepseek-r1-distill-qwen-32b',
    'mixtral-8x7b-32768'
]
print('-'* 50)
print('GROQ')
groq_response = call_groq(model_name= 'deepseek-r1-distill-llama-70b', content_prompt = prompt)
pprint(groq_response)
print(json.loads(groq_response.model_dump_json(indent=2)))


####### Pilot Runs

import os
import json
import time
from datetime import datetime
from tqdm import tqdm

# Create more structured directory
base_dir = "pilot_llm_results"
model_name = 'llama3-70b-8192'
model_dir = f"{base_dir}/{model_name}"
timestamp = datetime.now().strftime("%Y_%m%d_%H%M")
output_dir = f"{model_dir}/{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# Process all comments with rate limiting
processed = 0
verbose = True  # Set to False if you don't want detailed output

for comment in tqdm(sub_list):
    # Create prompt
    prompt = write_prompt(
        article_title=comment.get('article_title'),
        article_body=comment.get('article_body'),
        parent_comment=comment.get('parent_text'),
        target_comment=comment.get('comment_texts'),
        targets=TARGETS
    )
    
    # Call API with rate limiting
    try:
        groq_response = call_groq(model_name=model_name, content_prompt=prompt)
        llm_output = json.loads(groq_response.model_dump_json(indent=2))
        print(llm_output)

        # Store original comment with LLM response
        result = {**comment, **llm_output}
        
        # Save result
        output_file = os.path.join(output_dir, f"{comment['comment_ids']}.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        
        # Print verbose output if enabled
        if verbose:
            print(f"\nTitle: {comment.get('article_title')}")
            print(f"Comment: {comment.get('comment_texts')}")
            print(f"Response: {json.dumps(llm_output, indent=2)}")
            
        # Rate limiting (30 requests per minute = 2 seconds per request)
        processed += 1
        if processed % 30 == 0:
            print(f"Processed {processed} comments. Waiting 60 seconds...")
            time.sleep(10)
            
    except Exception as e:
        print(f"Error processing comment {comment['comment_ids']}: {e}")
        time.sleep(5)  # Wait longer on error

print(f"Processing complete. Results saved to {output_dir}")


###
# I need these changes: 
# make sure if there is an API problem it waits and retry same query
# optimise the waiting time
# read 1078561314 comment, it's crazy conspirationist 