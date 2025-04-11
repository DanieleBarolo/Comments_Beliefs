import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from typing import Dict, Optional

def check_batch_status(api_key: str, batch_id: str) -> Dict:
    """Check the status of a batch job.
    
    Args:
        api_key: Groq API key
        batch_id: ID of the batch job
        
    Returns:
        Dict containing the batch job status
    """
    url = f"https://api.groq.com/openai/v1/batches/{batch_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error checking batch status: {response.text}")
    
    return response.json()

def check_batch_step(user_id: str, user_run_dir: Path) -> Optional[Dict]:
    """Check the status of a batch job for a user.
    
    Args:
        run_id: The run identifier
        user_id: The user ID
        user_run_dir: Directory containing the batch job response
        
    Returns:
        Dict containing the batch job status or None if not found
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GROQ_API_FULL')
    if not api_key:
        raise ValueError("GROQ_API_FULL not found in environment variables")
    
    # Load batch job response to get batch_id
    batch_path = user_run_dir / "batch_job.json"
    if not batch_path.exists():
        print(f"Batch job response not found at {batch_path}")
        return None
    
    with open(batch_path, 'r') as f:
        batch_response = json.load(f)
    
    batch_id = batch_response.get('id')
    if not batch_id:
        print(f"No batch ID found in batch response: {batch_response}")
        return None
    
    # Check batch status
    print(f"\nChecking batch status for user {user_id} with batch {batch_id}")
    status_response = check_batch_status(api_key, batch_id)
    
    # Save status response
    status_path = user_run_dir / "batch_status.json"
    with open(status_path, 'w') as f:
        json.dump(status_response, f, indent=2)
    
    print(f"Batch status response saved to {status_path}")
    return status_response

def check_batches_step(run_id: str) -> None:
    """Check the status of all batch jobs for a run.
    
    Args:
        run_id: The run identifier
    """
    from paths import ExperimentPaths
    
    paths = ExperimentPaths(base_dir=str(Path(__file__).parent.absolute() / "data" / "experiments"))
    
    # Load users
    users_path = paths.get_users_path(run_id)
    with open(users_path, "r") as f:
        users = json.load(f)["users"]
    
    success = True
    # Check batch status for each user
    for user_id in users:
        try:
            user_run_dir = paths.get_user_run_dir(user_id, run_id)
            status_response = check_batch_step(str(user_id), user_run_dir)
            
            if status_response:
                # Check if batch is completed
                if status_response.get('status') == 'completed':
                    print(f"Batch for user {user_id} is completed")
                else:
                    print(f"Batch for user {user_id} is still processing")
                    success = False
            else:
                success = False
        except Exception as e:
            print(f"Error checking batch status for user {user_id}: {str(e)}")
            success = False
    
    if success:
        print("\nAll batches are completed successfully")
    else:
        print("\nSome batches are still processing or failed. Check the status files for details.")

if __name__ == "__main__":
    # Example usage:
    check_batches_step("20250411_CT_DS70B_005")
    # pass