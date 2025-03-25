from utils import init_mongo
import numpy as np 
import pandas as pd 
from datetime import datetime
import os 
import pyarrow.feather as feather 
import pyarrow.compute as pc
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import json 
import numpy as np
from utils import *
from pprint import pprint
from pymongo import MongoClient
from collections import Counter
from llm_caller import write_prompt
import json
from pydantic import BaseModel
from llm_caller import call_groq
import os
import json
import time
from datetime import datetime
from tqdm import tqdm


# 1. Connect to MongoDB# 


# 2. load the pilot comments (top_n)
user_name = "1Tiamo"
top_n = 100
file_name = f"pilot_users/{user_name}_top_{top_n}.jsonl"
# Read the JSONL file into a list
with open(file_name, "r") as f:
    comm_list = [json.loads(line) for line in f]


# 3. Sub-sample

# but sure let us see whether we can "find" the climate + god things. 
topics = [1, 8, 14] # pick relevant topics
sub_list = []
for topic in topics: 
    sub_list.extend([dict_ for dict_ in comm_list if dict_['topic'] == topic])
comm_list = sub_list #Overwriting!!

# 4. Select targets (for the LLMs calls)
TARGETS = ["global warming", "fossil fuels", 
           "God", "church",
           "Obama", "Trump",
           "Republicans", "Democrats",
           "Immigration", "Taxes",  
           "European Union", "Social Security", 
           "Harry Potter", "Soccer"]
import random 
random_TARGETS = random.sample(TARGETS, len(TARGETS))
def bullet_points_target(targets = TARGETS): 
    return "\n".join(f"•{target}" for num, target in enumerate(targets))

# 5. generate the prompt

class CommentStance(BaseModel):
    target: str
    stance: str 
    explanation: str 

class FullStances(BaseModel):
    results: List[CommentStance]

class CommentStanceX(BaseModel): 
    target: str
    stance: str 
    stance_type: str
    explanation: List[str]

class FullStancesX(BaseModel): 
    results: List[CommentStanceX]

class CommentStanceOT(BaseModel): 
    target: str
    stance: str 
    stance_type: str
    key_claims: List[str]
    explanation: str

class FullStancesOT(BaseModel): 
    results: List[CommentStanceOT]

####### try with GROQ
####### Pilot Runs

def generate_context(article_title, article_body, parent_comment, target_comment, article_date):
    sections = [
        f"Comment posted on date:\n{article_date}", 
        f"# News comment title:\n{article_title}",
        f"# News comment article:\n{article_body}" if article_body else None,
        f"# News comment directly above the focal comment:\n{parent_comment}" if parent_comment else None,
        ">>> COMMENT UNDER ANALYSIS<<<",
        f"\n{target_comment}",
        ">>> END COMMENT <<<"
    ]
    
    return "\n\n".join(filter(None, sections))


#### okay new attempt organize later (sorry future Victor and Daniele) #### 
def write_prompt2(comment, targets):
    article_title=comment.get('article_title'),
    article_body=comment.get('article_body'),
    parent_comment=comment.get('parent_text'),
    target_comment=comment.get('comment_texts'),
    comment_date = comment.get('comment_date'),
    prompt = f"""

    ### Overview ###

    Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
    Your task is to analyze the news comment and determine its stances towards specific targets. 
    
    ### Context ###
    {generate_context(article_title, article_body, parent_comment, target_comment, comment_date)}

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
          "stance_type": <one among [EXPLICIT, IMPLICIT, NONE]
          "explanation": ["atomic argument", "atomic argument", ...]
        }},
        // Repeat for each target
      ]
    }}
    
    ONLY return the JSON object itself.
    """
    return prompt

def write_prompt_open_target(comment, targets):
    article_title = comment.get('article_title')
    article_body = comment.get('article_body')
    parent_comment = comment.get('parent_text')
    target_comment = comment.get('comment_texts')
    comment_date = comment.get('comment_date')
    prompt = f"""

    ### Overview ###

    Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
    Your task is to analyze the news comment, generate the main targets expressed by the user, and determine its stance towards the found targets. 
    A target should be the topic on which the comment is talking. 
    To help you in this task, you will be provided with a broader context where the comment happened. 
    You will have the title and body of the article, together with the time when the comment was posted. Also, if any, the news comment directly above the focal comment will be provided.
   
    ### Context ###
    {generate_context(article_title, article_body, parent_comment, target_comment, comment_date)}

    ### Task Description ###

    1. Identify all the expressed targets from the user's comment. 
        - The targets can be a single word or a phrase, but its maximum length MUST be 4 words.

    2. For each target, determine the stance in the comment:
        2.1 Classify the Stance
            - If the stance is in favor of the target, write FAVOR.
            - If it is against the target, write AGAINST.
            - If it is ambiguous, write NONE - that means the user is clearly speaking about the topic but the stance is not clear. 
            
        2.2. Provide the stance type:
            - EXPLICIT: when the stance is directly stated in the comment
            - IMPLICIT: when the stance is implied but not explicitly stated

    2.3 Extract key claims
        - Extract the fundamental assertions or beliefs that form the basis of the commenter's stance
        - Each key claim should represent a distinct assertion presented as directly stated by the commenter
        - Express claims in direct form (e.g., "Climate change is accelerating due to human activities.") rather than reported speech (e.g., "The user said that climate change was accelerating due to human activities.")
        - DeprecationWarningistill the essential claims expressed in the comment text

    ### Output Format: ###

    You must output only JSON format:
    {{
    "results": [
        {{
        "target": "<target description - maximum 4 words>", 
        "stance": "<one among [FAVOR, AGAINST, NONE]>", 
        "stance_type": "<one among [EXPLICIT, IMPLICIT]>",
        "key_claims": "<[claim 1, claim 2, ...]>", 
        "explanation": "<explanation of how the key claims support the stance classification>"
        }},
        // Repeat for each target expressed by the user's comment
    ]
    }}

    ONLY return the JSON object itself.
    """
    return prompt


from vars import GROQ_MODELS
prompt_ot = write_prompt_open_target(comm_list[8], targets=TARGETS)
with open("prompts_tests/prompt_ot.txt", "w") as f: 
    f.write(prompt_ot)

model_name = GROQ_MODELS[1]
# lets call the API for just one comment 

# groq_response = call_groq(model_name=model_name, content_prompt=prompt_ot, response_model=FullStancesOT)
# llm_output = json.loads(groq_response.model_dump_json(indent=2))
# llm_output
pprint(prompt_ot)
# use ollama 
from llm_caller import call_ollama
model_name = "gemma3:27b"
llm_output = call_ollama(response_model = FullStancesOT, content_prompt = prompt_ot, model_name = model_name)
json.loads(llm_output['message']['content'])
# old_output 

# call for all subsample of comments. 


def prompt_model(base_dir, model_name, comm_list, TARGETS, prompt: str, response_model=FullStances, verbose=True): 
    model_dir = os.path.join(base_dir, model_name)
    timestamp = datetime.now().strftime("%Y_%m%d_%H%M")
    output_dir = f"{model_dir}/{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    processed = 0
    verbose = True  # Set to False if you don't want detailed output

    for comment in tqdm(comm_list):
        # Create prompt
        prompt = write_prompt2(
            comment,
            targets=TARGETS
        )
        
        # Call API with rate limiting
        try:
            groq_response = call_groq(model_name=model_name, content_prompt=prompt, response_model=response_model)
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

'''
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
'''
###
# I need these changes: 
# make sure if there is an API problem it waits and retry same query
# optimise the waiting time
# read 1078561314 comment, it's crazy conspirationist 


TARGETS = [
    "global warming", "fossil fuels", "God", "church", "Obama", "Trump", 
    "Republicans", "Democrats", "Immigration", "Social services and welfare"
    ]

base_dir = "pilot_llm_results"
model_name = 'llama3-70b-8192'
prompt_model(
    base_dir=base_dir,
    model_name=model_name,
    sub_list=sub_list,
    TARGETS=TARGETS,
    response_model=FullStancesX 
)

#### play with actually open-ended ####
comm_list