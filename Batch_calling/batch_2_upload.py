import json
import os
from pathlib import Path
from paths import ExperimentPaths
from dotenv import load_dotenv
import requests

def upload_file_to_groq(api_key: str, file_path: str) -> dict:
    """Upload a file to Groq API."""
    url = "https://api.groq.com/openai/v1/files"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (os.path.basename(file_path), f, 'application/jsonl')
        }
        data = {
            "purpose": "batch"  # Required by Groq API
        }
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Error uploading file: {response.text}")
    
    return response.json()

def upload_batch(run_id: str, user_id: str, user_run_dir: Path) -> None:
    """Upload a batch file to Groq API.
    
    Args:
        run_id: The run identifier
        user_id: The user ID
        user_run_dir: Directory containing the batch file
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GROQ_API_FULL')
    if not api_key:
        raise ValueError("GROQ_API_FULL not found in environment variables")
    
    # Get batch file path
    batch_path = user_run_dir / "batch.jsonl"
    if not batch_path.exists():
        raise FileNotFoundError(f"Batch file not found at {batch_path}")
    
    # Upload file
    print(f"\nUploading batch file for user {user_id} from {batch_path}")
    response = upload_file_to_groq(api_key, str(batch_path))
    
    # Save upload response
    upload_path = user_run_dir / "upload.json"
    with open(upload_path, 'w') as f:
        json.dump(response, f, indent=2)
    
    print(f"Upload response saved to {upload_path}")

if __name__ == "__main__":

    BATCH_CALLING_DIR = Path(__file__).parent.absolute()
    # upload_batch(
    #     "20250408_CT_DS70B_004", 
    #     "243896279", 
    #     Path("/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/Batch_calling/data/experiments/users/243896279/20250408_CT_DS70B_004/batch.jsonl")
    # )