import requests
import os 
import json 
from batch_4_status import check_batches_step
from dotenv import load_dotenv
from pathlib import Path 
from paths import ExperimentPaths

def download_file_content(api_key, output_file_id, output_file):
    url = f"https://api.groq.com/openai/v1/files/{output_file_id}/content"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    
    # Write the content to a file
    with open(output_file, 'wb') as f:
        f.write(response.content)

    return f"File downloaded successfully to {output_file}"

# get all completed files 
def complete_runs(run_id, api_key):
    
    paths = ExperimentPaths(base_dir=str(Path(__file__).parent.absolute() / "data" / "experiments"))
    
    # Load users
    users_path = paths.get_users_path(run_id)
    with open(users_path, "r") as f:
        users = json.load(f)["users"]
    
    # Find path 
    for user_id in users:
        user_run_dir = paths.get_user_run_dir(user_id, run_id)
    
        # Extract file 
        with open(os.path.join(user_run_dir, 'batch_status.json'), 'r') as f: 
            batch_status = json.load(f)
        
        status = batch_status['status']
        output_file_id = batch_status['output_file_id']
        error_file_id = batch_status['error_file_id']
        
        # Download + save
        if status == 'completed': # consider expired 
            download_file_content(api_key, output_file_id, os.path.join(user_run_dir, 'batch_results.jsonl'))
            download_file_content(api_key, error_file_id, os.path.join(user_run_dir, 'batch_errors.jsonl'))
            
    return user_run_dir  

# Usage example
load_dotenv()
api_key = os.getenv('GROQ_API_FULL')
run_id = '20250411_CT_DS70B_005' # MOTHERJONES UPDATED
check_batches_step(run_id)
complete_runs(run_id, api_key)