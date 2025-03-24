import os
from typing import List
from pydantic import BaseModel
from groq import Groq
from ollama import chat
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
import instructor
from utils import *

###############################################################################
# Setup                                                                       #
###############################################################################

load_dotenv()

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

###############################################################################
# Ollama local LLM call                                                       #
###############################################################################


def call_ollama(content_prompt: str, model_name: str = 'llama3.1:8b', temp: int = 0):

    # schema = {'type': 'object', 'properties': {'friends': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'age': {'type': 'integer'}, 'is_available': {'type': 'boolean'}}, 'required': ['name', 'age', 'is_available']}}}, 'required': ['friends']}
    response = chat(
    model=model_name,
    messages=[{'role': 'user', 'content': content_prompt}],
    format=FullStances.model_json_schema(),  # Use Pydantic to generate the schema or format=schema
    options={'temperature': temp},  # Make responses more deterministic
    )

    return response


###############################################################################
# Groq API                                                                    #
###############################################################################

def call_groq(content_prompt: str, model_name: str = 'deepseek-r1-distill-llama-70b', temp: float = 0.75, response_model =  FullStances):

    # Initialize Groq client with API key from environment variable
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    # Patch client with instructor for structured output support
    client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

    # Generate structured output based on provided schema (FullStances)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": content_prompt}],
        response_model=response_model,
        temperature=temp,
    )

    return response


###############################################################################
# OpenAI API                                                                    #
###############################################################################

# OpenAI API call
def call_openai(api_key: str, model_name: str, prompt: str) -> str:
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

# old prompt 
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