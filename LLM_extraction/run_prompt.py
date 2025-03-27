# create a batch for each user.
# include amount of tokens.
# clean this up.
# jsonl (look at groq batch)
from utils import init_mongo
import numpy as np 
import pandas as pd 
from datetime import datetime, date 
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
#from llm_caller import call_groq
import os
import json
from groq import Groq

# 2. load the pilot comments (top_n)
user_name = "1Tiamo"
top_n = 100
file_name = f"pilot_users/{user_name}_top_{top_n}.jsonl"
# Read the JSONL file into a list
with open(file_name, "r") as f:
    comm_list = [json.loads(line) for line in f]

# 4. Select targets (for the LLMs calls)
# 4. Select targets (for the LLMs calls)
TARGETS = ["global warming", "fossil fuels", 
           "God", "church",
           "Obama", "Trump",
           "Republicans", "Democrats",
           "Immigration", "Taxes",  
           "European Union", "Social Security", 
           "Harry Potter", "Soccer"]

def bullet_points_target(targets = TARGETS): 
    return "\n".join(f"•{num}: {target}" for num, target in enumerate(targets))

# 5. generate the prompts
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

from vars import GROQ_MODELS
prompt = write_prompt2(comm_list[0], targets=TARGETS)
model_name = GROQ_MODELS[1]

from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from instructor.exceptions import InstructorRetryException
from groq import Groq
import instructor
import os

@retry(
    retry=retry_if_exception_type(InstructorRetryException),  # <-- changed here
    wait=wait_exponential(multiplier=1, min=4, max=120),  # increased max wait for safety
    stop=stop_after_attempt(5),
)
def call_groq(response_model, content_prompt: str, model_name: str = 'deepseek-r1-distill-llama-70b', temp: float = 0.75):
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": content_prompt}],
            response_model=response_model,
            temperature=temp,
        )
    except InstructorRetryException as e:
        print(f"Instructor retry triggered due to rate limit: {e}. Retrying...")
        raise e  # Re-raise to activate the retry mechanism

    return response

base_dir = 'pilot_llm_results/'
today = str(date.today())
output_dir = os.path.join(base_dir, model_name, today)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

for ele in comm_list: 
    comment_id = ele['comment_ids']
    print(comment_id)
    
    prompt = write_prompt2(ele, targets=TARGETS)
    groq_response = call_groq(response_model=FullStancesX, content_prompt=prompt, model_name=model_name)
    llm_output = json.loads(groq_response.model_dump_json(indent=2))
    
    result = {**ele, **llm_output}
    
    output_file = os.path.join(output_dir, f"{comment_id}.json")
    with open(output_file, "w") as f: 
        json.dump(result, f, indent=2)