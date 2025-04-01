import requests 
import os 
from dotenv import load_dotenv
import json

def upload_file_to_groq(api_key, file_path):
    url = "https://api.groq.com/openai/v1/files"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Prepare the file and form data
    files = {
        "file": ("batch_file.jsonl", open(file_path, "rb"))
    }

    data = {
        "purpose": "batch"
    }

    # Make the POST request
    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()

# usage example
load_dotenv(dotenv_path='.env')
api_key = os.getenv('GROQ_API_FULL')
file_path = "data/batch_files/31499533/deepseek-r1-distill-llama-70b/closed_target/2025-04-01-04/batch_size_500_no_body_with_context.jsonl"  

try:
    result = upload_file_to_groq(api_key, file_path)
    with open('data/groq/upload.json', 'w') as f: 
        json.dump(result, f)

except Exception as e:
    print(f"Error: {e}")