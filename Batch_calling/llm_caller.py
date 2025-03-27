import os
from groq import Groq
from dotenv import load_dotenv
import instructor
from utils import *

###############################################################################
# Setup                                                                       #
###############################################################################

load_dotenv()

###############################################################################
# Groq API                                                                    #
###############################################################################

def call_groq_from_batch(batch_line, temp: float = 0.75):
    
    # Initialize Groq client with API key from environment variable
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    #TO-DO ADD THE VALIADTOR in Batch Calling
    # # Patch client with instructor for structured output support
    # client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

    # Generate structured output based on provided schema (FullStances)
    response = client.chat.completions.create(
        model=batch_line.get("body").get("model"),
        messages=batch_line.get("body").get("messages"),
        # response_model=response_model, 
        temperature=temp
    )
    return response