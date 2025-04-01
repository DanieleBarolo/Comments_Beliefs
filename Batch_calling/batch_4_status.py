import requests 
import os 
from dotenv import load_dotenv
import json

def get_batch_status(api_key, batch_id):
    url = f"https://api.groq.com/openai/v1/batches/{batch_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.json()

# Usage example
load_dotenv(dotenv_path='.env')
api_key = os.getenv('GROQ_API_FULL')

# batch ID (from results)
with open('data/groq/result.json', 'r') as f:
    results = json.load(f)
batch_id = results.get('id')

try:
    status = get_batch_status(api_key, batch_id)
    with open('data/groq/batch.json', 'w') as f: 
        json.dump(status, f)

except Exception as e:
    print(f"Error: {e}")