import json
from pathlib import Path

def read_prompts(jsonl_file: str, num_prompts: int = 5, output_dir: str = "example_prompts"):
    """
    Read and save prompts from a JSONL file.
    
    Args:
        jsonl_file: Path to the JSONL file
        num_prompts: Number of prompts to save (default: 5)
        output_dir: Directory to save the prompts (default: example_prompts)
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Read prompts from JSONL file
    prompts = []
    with open(jsonl_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= num_prompts:
                break
            data = json.loads(line)
            
            # Extract system prompt and user content
            system_prompt = data['body']['messages'][0]['content']
            user_content = data['body']['messages'][1]['content']
            comment_id = data['custom_id']
            
            # Save to individual files
            prompt_file = output_path / f"prompt_{comment_id}.txt"
            with open(prompt_file, 'w') as pf:
                pf.write(f"System Prompt:\n{'-' * 80}\n{system_prompt}\n\n")
                pf.write(f"User Content:\n{'-' * 80}\n{user_content}\n")
            
            prompts.append({
                'comment_id': comment_id,
                'system_prompt': system_prompt,
                'user_content': user_content
            })
            
    print(f"Saved {len(prompts)} prompts to {output_path}")
    return prompts

if __name__ == "__main__":
    # Read prompts from exp_00001.jsonl
    jsonl_file = "data/batch_files/exp_00001.jsonl"
    prompts = read_prompts(jsonl_file, num_prompts=5, output_dir="example_prompts") 