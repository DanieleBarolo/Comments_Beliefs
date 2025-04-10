import pandas as pd
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import yaml
from typing import List, Dict, Optional

# Add the parent directory to sys.path to import from Batch_calling
sys.path.append(str(Path(__file__).parent))
from configs.create_experiment import create_experiment_config
from batch_1_prepare import write_jsonl_file
from batch_2_upload import upload_batch
from batch_3_create import create_batch_step
from batch_4_status import check_batches_step
from paths import ExperimentPaths

# Get the Batch_calling directory
BATCH_CALLING_DIR = Path(__file__).parent.absolute()

def load_users():
    """Load the list of users from CSV."""
    users_file = BATCH_CALLING_DIR / "data" / "selected_users_list.csv"
    if not users_file.exists():
        raise FileNotFoundError(f"Users list file not found at {users_file}")
    return pd.read_csv(users_file)

def sample_users(users_df, sample_size):
    """Sample users from the dataframe.
    
    Returns:
        tuple: (list of user_ids, list of usernames)
    """
    if sample_size > len(users_df):
        print(f"Warning: Requested sample size {sample_size} is larger than available users {len(users_df)}")
        sample_size = len(users_df)
    
    sampled = users_df.sample(n=sample_size)
    return sampled['user_id'].tolist(), sampled['user_name'].tolist()

def create_run_id(prompt_type: str, model: str, run_number: Optional[int] = None) -> str:
    """Create a run ID following the format YYYYMMDD_TYPE_MODEL_XXX."""
    date = datetime.now().strftime("%Y%m%d")
    
    # Map prompt type to short code
    type_code = "CT" if prompt_type == "closed_target" else "OT"
    
    # Map model to short code
    model_code = "DS70B" if "deepseek" in model.lower() else "L70B"
    
    # Get next run number if not provided
    if run_number is None:
        paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
        runs_dir = paths.base_dir / "runs"
        existing_runs = list(runs_dir.glob(f"{date}_{type_code}_{model_code}_*"))
        run_number = len(existing_runs) + 1
    
    return f"{date}_{type_code}_{model_code}_{run_number:03d}"

def create_experiment_directories(run_id: str, user_ids: List[str]) -> Dict[str, Path]:
    """Create all necessary directories for the experiment."""
    paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
    
    # Create run directory structure
    run_dir = paths.get_run_dir(run_id)
    
    # Create user directories
    user_dirs = {}
    for user_id in user_ids:
        user_dir = paths.get_user_run_dir(user_id, run_id)
        user_dirs[user_id] = user_dir
    
    return {
        "run_dir": run_dir,
        "user_dirs": user_dirs
    }

def create_status_file(run_dir: Path, description: str) -> None:
    """Create and initialize the status.json file."""
    status = {
        "created": datetime.now().isoformat(),
        "steps": {
            "config_created": False,
            "batches_created": False,
            "uploads_completed": False,
            "results_received": False
        },
        "last_updated": datetime.now().isoformat(),
        "description": description
    }
    
    with open(run_dir / "status.json", "w") as f:
        json.dump(status, f, indent=2)

def update_status(run_id: str, step: str, value: bool = True) -> None:
    """Update the status.json file for a specific step."""
    paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
    status_path = paths.get_status_path(run_id)
    
    with open(status_path, "r") as f:
        status = json.load(f)
    
    status["steps"][step] = value
    status["last_updated"] = datetime.now().isoformat()
    
    with open(status_path, "w") as f:
        json.dump(status, f, indent=2)

def create_experiment_config_step(run_id: str, config_params: Dict) -> None:
    """Create and save experiment configuration files."""
    paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
    
    # Create config
    config = create_experiment_config(**config_params)
    
    # Save config.yaml
    config_path = paths.get_config_path(run_id)
    with open(config_path, "w") as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    
    # Save users.json
    users_data = {"users": config_params["user_ids"]}
    users_path = paths.get_users_path(run_id)
    with open(users_path, "w") as f:
        json.dump(users_data, f, indent=2)
    
    update_status(run_id, "config_created", True)

def create_batches_step(run_id: str) -> None:
    """Create batch files for all users."""
    paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
    
    # Load users
    users_path = paths.get_users_path(run_id)
    with open(users_path, "r") as f:
        users = json.load(f)["users"]
    
    # Create batch files for each user
    for user_id in users:
        # Get the full path for the batch file
        user_run_dir = paths.get_user_run_dir(user_id, run_id)
        batch_path = user_run_dir / "batch.jsonl"
        print(f"\nCreating batch file at: {batch_path}")
        
        write_jsonl_file(
            run_id=run_id, 
            user_id=str(user_id), 
            output_dir=user_run_dir,
            base_dir=str(BATCH_CALLING_DIR / "data" / "experiments")
        )
    
    update_status(run_id, "batches_created", True)

def upload_batches_step(run_id: str) -> None:
    """Upload batch files to Groq."""
    paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
    
    # Load users
    users_path = paths.get_users_path(run_id)
    with open(users_path, "r") as f:
        users = json.load(f)["users"]
    
    success = True
    # Upload batches for each user
    for user_id in users:
        try:
            user_run_dir = paths.get_user_run_dir(user_id, run_id)
            upload_batch(run_id, str(user_id), user_run_dir)
        except Exception as e:
            print(f"Error uploading batch for user {user_id}: {str(e)}")
            success = False
    
    if success:
        update_status(run_id, "uploads_completed", True)
    else:
        print("\nSome uploads failed. Check the errors above.")

def create_batch_jobs_step(run_id: str) -> None:
    """Create batch jobs for uploaded files."""
    paths = ExperimentPaths(base_dir=str(BATCH_CALLING_DIR / "data" / "experiments"))
    
    # Load users
    users_path = paths.get_users_path(run_id)
    with open(users_path, "r") as f:
        users = json.load(f)["users"]
    
    success = True
    # Create batch jobs for each user
    for user_id in users:
        try:
            user_run_dir = paths.get_user_run_dir(user_id, run_id)
            create_batch_step(run_id, str(user_id), user_run_dir)
        except Exception as e:
            print(f"Error creating batch job for user {user_id}: {str(e)}")
            success = False
    
    if success:
        update_status(run_id, "batch_jobs_created", True)
    else:
        print("\nSome batch job creations failed. Check the errors above.")

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GROQ_API_FULL')
    if not api_key:
        raise ValueError("GROQ_API_FULL not found in environment variables")
    
    # Configuration parameters
    sample_size = 5  # Number of users to sample
    
    # Experiment parameters
    description = "First batches for sampled users"
    model = "deepseek-r1-distill-llama-70b"
    batch_size = 500
    prompt_type = "closed_target"
    
    # Context settings
    context = {
        "include_article_body": False,
        "include_most_liked_comment": True,
        "include_parent_comment": True,
        "include_oldest_comment": True
    }
    
    try:
        # Step 1: Load and sample users
        users_df = load_users()
        user_ids, usernames = sample_users(users_df, sample_size)
        
        # Step 2: Create run ID
        run_id = create_run_id(prompt_type, model)
        
        # Step 3: Create directory structure
        dirs = create_experiment_directories(run_id, user_ids)
        create_status_file(dirs["run_dir"], description)
        
        # Step 4: Create and save configuration
        config_params = {
            "user_ids": user_ids,
            "usernames": usernames,
            "description": description,
            "model": model,
            "batch_size": batch_size,
            "prompt_type": prompt_type,
            "context": context
        }
        create_experiment_config_step(run_id, config_params)
        
        # Step 5: Create batch files
        create_batches_step(run_id)
        
        # Step 6: Upload to Groq
        upload_batches_step(run_id)
        
        # Step 7: Create batch jobs
        create_batch_jobs_step(run_id)
        
        # Step 8: Check batch status
        check_batches_step(run_id)
        
        print(f"\nExperiment {run_id} completed successfully")
        
    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running experiment: {str(e)}")
        raise

if __name__ == "__main__":
    """
    # Run everything
    main()
    """
    
    # # Load environment variables
    # load_dotenv()
    # api_key = os.getenv('GROQ_API_FULL')
    # if not api_key:
    #     raise ValueError("GROQ_API_FULL not found in environment variables")
    
    # # Configuration parameters
    # sample_size = 5  # Number of users to sample
    
    # # Experiment parameters
    # description = "First batches for sampled users"
    # model = "deepseek-r1-distill-llama-70b"
    # batch_size = 500
    # prompt_type = "closed_target"
    
    # # Context settings
    # context = {
    #     "include_article_body": False,
    #     "include_most_liked_comment": True,
    #     "include_parent_comment": True,
    #     "include_oldest_comment": True
    # }
    
    # # Step 1: Load and sample users
    # users_df = load_users()
    # user_ids, usernames = sample_users(users_df, sample_size)
    
    # # Step 2: Create run ID
    # run_id = create_run_id(prompt_type, model)
    
    # # Step 3: Create directory structure
    # dirs = create_experiment_directories(run_id, user_ids)
    # create_status_file(dirs["run_dir"], description)
    
    # # Step 4: Create and save configuration
    # config_params = {
    #     "user_ids": user_ids,
    #     "usernames": usernames,
    #     "description": description,
    #     "model": model,
    #     "batch_size": batch_size,
    #     "prompt_type": prompt_type,
    #     "context": context
    # }
    # create_experiment_config_step(run_id, config_params)
    
    # # Step 5: Create batch files
    # create_batches_step(run_id)
    
    # # Step 6: Upload to Groq
    # upload_batches_step(run_id)
    
    run_id = "20250409_CT_DS70B_002"
    # Step 7: Create batch jobs
    # create_batch_jobs_step(run_id)
    
    # # Step 8: Check batch status
    check_batches_step(run_id)
