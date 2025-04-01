import requests 
import os 
from dotenv import load_dotenv
import json

def create_batch(api_key, input_file_id):
    url = "https://api.groq.com/openai/v1/batches"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "input_file_id": input_file_id,
        "endpoint": "/v1/chat/completions",
        "completion_window": "24h"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Usage example
load_dotenv(dotenv_path='.env')
api_key = os.getenv('GROQ_API_FULL')

# file id (from upload)
with open('data/groq/upload.json', 'r') as f:
    upload = json.load(f)
file_id = upload.get('id')

try:
    result = create_batch(api_key, file_id)
    with open('data/groq/result.json', 'w') as f: 
        json.dump(result, f)

except Exception as e:
    print(f"Error: {e}")