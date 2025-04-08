import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from typing import Dict

def create_batch_job(api_key: str, file_id: str) -> Dict:
    """Create a batch job using the uploaded file.
    
    Args:
        api_key: Groq API key
        file_id: ID of the uploaded file from step 2
        
    Returns:
        Dict containing the batch job details
    """
    url = "https://api.groq.com/openai/v1/batches"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "input_file_id": file_id,
        "endpoint": "/v1/chat/completions",
        "completion_window": "24h"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        raise Exception(f"Error creating batch job: {response.text}")
    
    return response.json()

def create_batch_step(run_id: str, user_id: str, user_run_dir: Path) -> None:
    """Create a batch job for a user's uploaded file.
    
    Args:
        run_id: The run identifier
        user_id: The user ID
        user_run_dir: Directory containing the upload response
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GROQ_API_FULL')
    if not api_key:
        raise ValueError("GROQ_API_FULL not found in environment variables")
    
    # Load upload response to get file_id
    upload_path = user_run_dir / "upload.json"
    if not upload_path.exists():
        raise FileNotFoundError(f"Upload response not found at {upload_path}")
    
    with open(upload_path, 'r') as f:
        upload_response = json.load(f)
    
    file_id = upload_response.get('id')
    if not file_id:
        raise ValueError(f"No file ID found in upload response: {upload_response}")
    
    # Create batch job
    print(f"\nCreating batch job for user {user_id} with file {file_id}")
    batch_response = create_batch_job(api_key, file_id)
    
    # Save batch job response
    batch_path = user_run_dir / "batch_job.json"
    with open(batch_path, 'w') as f:
        json.dump(batch_response, f, indent=2)
    
    print(f"Batch job response saved to {batch_path}")
    return batch_response

if __name__ == "__main__":
    BATCH_CALLING_DIR = Path(__file__).parent.absolute()
    # Example usage:
    # create_batch_step(
    #     "20250408_CT_DS70B_004",
    #     "243896279",
    #     Path("/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/Batch_calling/data/experiments/users/243896279/20250408_CT_DS70B_004")
    # )