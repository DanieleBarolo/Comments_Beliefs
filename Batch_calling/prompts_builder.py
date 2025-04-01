##############################################################################
# Loadings 
##############################################################################
from setup import *

##############################################################################
# Utils 
##############################################################################

def generate_context(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, article_date):
    sections = [
        f"Comment posted on date:\n{article_date}", 
        f"# News comment title:\n{article_title}",
        f"# News comment article:\n{article_body}" if article_body else None,
        f"# Oldest comment (from the thread):\n{oldest_comment}" if oldest_comment else None,
        f"# Most liked comment (from the thread):\n{most_liked_comment}" if most_liked_comment else None,
        f"# News comment directly above the focal comment:\n{parent_comment}" if parent_comment else None,
        ">>> COMMENT UNDER ANALYSIS<<<",
        f"\n{target_comment}",
        ">>> END COMMENT <<<"
    ]
    
    return "\n\n".join(filter(None, sections))

##############################################################################
# Open Target 
##############################################################################
def write_prompt_ot(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, comment_date):

    prompt = f"""

    ### Overview ###

    Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
    Your task is to analyze the news comment, generate the main targets expressed by the user, and determine its stance towards the found targets. 
    A target should be the topic on which the comment is talking. 
    To help you in this task, you will be provided with a broader context where the comment happened. 
    You will have the title and body of the article, together with the time when the comment was posted. Also, if any, the news comment directly above the focal comment will be provided.
   
    ### Context ###
    {generate_context(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, comment_date)}

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
            - Each key claim should be expressed impersonalizing the user in the form of "I agree with the following: <extracted claim>".

    ### Output Format: ###

    You must output only JSON format:
    {{
    "results": [
        {{
        "target": "<target description - maximum 4 words>", 
        "stance": "<one among [FAVOR, AGAINST, NONE]>", 
        "stance_type": "<one among [EXPLICIT, IMPLICIT]>",
        "key_claims": "<[ "I agree with the following: <extracted claim 1>", ...,"I agree with the following: <extracted claim 2>"]>", 
        "explanation": "<explanation of how the key claims support the stance classification>"
        }},
        // Repeat for each target expressed by the user's comment
    ]
    }}

    ONLY return the JSON object itself.
    """
    return prompt
##############################################################################
# Closed Target (to be modified)
##############################################################################

def bullet_points_target(targets): 
    return "\n".join(f"•{target}" for num, target in enumerate(targets))

def write_prompt_ct(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, comment_date, targets):

    prompt = f"""

    ### Overview ###

    Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
    Your task is to analyze the news comment and determine its stances towards specific targets. 
    
    ### Context ###
    {generate_context(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, comment_date)}

    ### Targets ###
    {bullet_points_target(targets)}

    ### Task Description ###

    For each target, determine the stance in the comment:
    - If the stance is in favor of the target or agrees with the target, write FAVOR
    - If the stance is against the target or disagrees with the target, write AGAINST
    - If the stance is ambiguous, write NONE
    - If the comment is not related to the target, write NOT RELATED

    ### KEY CLAIM ###
    - Extract the fundamental assertion or belief that form the basis of the commenter's stance
    - The key claim should be expressed impersonalizing the user in the form of "I agree with the following: <extracted claim>".
    - If no stance is expressed (NOT RELATED, NONE) then leave the explanation field empty. 

    ### Output Format: ###

    You must output only JSON format:
    {{
      "results": [
        {{
          "target": "<original_target>", 
          "stance": "<one among [FAVOR, AGAINST, NONE, NOT RELATED]>", 
          "stance_type": "<one among [EXPLICIT, IMPLICIT, NONE]>",
          "explanation": "<I agree with the following: ...> if stance in FAVOR/AGAINST"
        }},
        // Repeat for each target
      ]
    }}
    
    ONLY return the JSON object itself.
    """
    return prompt


##### NEW PROMPT #####

def write_prompt_ct_new(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, comment_date, targets):

    prompt = f"""

    ### Overview ###

    Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
    Your task is to analyze the news comment and determine its stances towards specific targets. 
    
    ### Context ###
    {generate_context(article_title, article_body, parent_comment, oldest_comment, most_liked_comment, target_comment, comment_date)}

    ### Targets ###
    {bullet_points_target(targets)}
    
    ### Task Description ###

    1. Identify which targets from the list are actually mentioned or referenced in the comment, either explicitly or implicitly. Ignore targets that are not present.
    
    2. For each identified target, determine the stance in the comment:
       - If the stance is in favor of the target, write FAVOR
       - If it is against the target, write AGAINST
       - If it is ambiguous, write NONE

    ### Explanation ### 
    Together with the stance for a given target, provide evidence-based reasoning that quotes or references specific text from the comment that reveals the commenter's stance toward the target.

    ### Output Format: ###

    You must output only JSON format:
    {{
      "results": [
        {{
          "target": "<original_target>", 
          "stance": "<one among [FAVOR, AGAINST, NONE]>", 
          "stance_type": <one among [EXPLICIT, IMPLICIT, NONE]
          "explanation": <brief explanation of the stance>
        }},
        // Repeat for each target that are mentioned in the comment
      ]
    }}
    
    ONLY return the JSON object itself.
    """
    return prompt 