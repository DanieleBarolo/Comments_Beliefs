import pandas as pd
import random
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Add the parent directory to sys.path to import from Batch_calling
sys.path.append(str(Path(__file__).parent))
from configs.create_experiment import create_experiment_config
from batch_1_prepare import write_jsonl_file
from batch_2_upload import upload_file_to_groq

def load_users():
    users_df = pd.read_csv('data/selected_users_list.csv')
    return users_df

def sample_users(users_df, sample_size):
    if sample_size > len(users_df):
        print(f"Warning: Requested sample size {sample_size} is larger than available users {len(users_df)}")
        sample_size = len(users_df)
    
    return users_df.sample(n=sample_size)

def upload_to_groq(exp_key, api_key):
    """Upload a batch file to Groq and save the response"""
    # Construct the path to the batch file
    batch_file = Path("data/batch_files") / f"{exp_key}.jsonl"
    
    if not batch_file.exists():
        raise FileNotFoundError(f"Batch file not found: {batch_file}")
    
    try:
        # Upload to Groq
        result = upload_file_to_groq(api_key, str(batch_file))
        
        # Save the upload response
        upload_dir = Path("data/groq/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        upload_file = upload_dir / f"{exp_key}_upload.json"
        with open(upload_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        return result
    except Exception as e:
        print(f"Error uploading {exp_key} to Groq: {str(e)}")
        return None

def main():
    # Load environment variables
    load_dotenv(dotenv_path='.env')
    api_key = os.getenv('GROQ_API_FULL')
    if not api_key:
        raise ValueError("GROQ_API_FULL not found in environment variables")
    
    # Configuration parameters
    sample_size = 3  # Number of users to sample
    
    # Experiment parameters
    description = "Batch experiment for sampled users"
    model = "deepseek-r1-distill-llama-70b"
    batch_size = 10
    prompt_type = "closed_target"
    
    # Context settings
    context = {
        "include_article_body": False,
        "include_most_liked_comment": True,
        "include_parent_comment": True,
        "include_oldest_comment": True
    }
    
    # Load and sample users
    users_df = load_users()
    sampled_users = sample_users(users_df, sample_size)
    
    # Create experiment configurations, batch files, and upload to Groq
    experiment_results = []
    for _, user in sampled_users.iterrows():
        result = {
            'user_name': user['user_name'],
            'user_id': user['user_id'],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Create experiment configuration
            config_path = create_experiment_config(
                user_id=str(user['user_id']),
                description=f"{description} - User: {user['user_name']}",
                username=user['user_name'],
                model=model,
                batch_size=batch_size,
                prompt_type=prompt_type,
                context=context
            )
            print(f"Created experiment configuration for user {user['user_name']} at {config_path}")
            
            # Extract experiment key from config path (exp_XXXXX)
            exp_key = Path(config_path).stem
            result['experiment_key'] = exp_key
            
            # Create batch file
            write_jsonl_file(exp_key)
            print(f"Created batch file for experiment {exp_key}")
            
            # Upload to Groq
            upload_result = upload_to_groq(exp_key, api_key)
            if upload_result:
                result['groq_file_id'] = upload_result.get('id')
                result['groq_status'] = 'success'
                print(f"Successfully uploaded {exp_key} to Groq")
            else:
                result['groq_status'] = 'failed'
                
        except Exception as e:
            print(f"Error processing user {user['user_name']}: {str(e)}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        experiment_results.append(result)
    
    print(f"\nProcessed {len(sampled_users)} users")
    
    # Save detailed results
    results_dir = Path("experiments")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON for detailed logging
    results_file = results_dir / f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(experiment_results, f, indent=2)
    print(f"Saved detailed results to {results_file}")
    
    # Save summary as CSV
    summary_df = pd.DataFrame(experiment_results)
    summary_file = results_dir / f"experiment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"Saved summary to {summary_file}")

if __name__ == "__main__":
    main() 