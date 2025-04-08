import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import re

def get_next_exp_number(experiments_dir: Path) -> int:
    """Get the next available experiment number."""
    pattern = re.compile(r'exp_(\d{5})')
    max_num = 0
    
    if experiments_dir.exists():
        for file in experiments_dir.glob("*.yaml"):
            if match := pattern.search(file.stem):
                max_num = max(max_num, int(match.group(1)))
    
    return max_num + 1

def create_experiment_config(
    user_id: str,
    description: str,
    template: str = "base_config.yaml",
    username: Optional[str] = None,
    model: str = "deepseek-r1-distill-llama-70b",
    temperature: float = 0,
    prompt_type: str = "closed_target",
    batch_size: int = 100,
    **kwargs
) -> str:
    """
    Create a new experiment configuration file.
    
    Args:
        user_id: The user ID for the experiment
        description: Description of the experiment
        template: Template file to use (default: base_config.yaml)
        username: Optional username (defaults to user_id if not provided)
        model: Model to use (default: deepseek-r1-distill-llama-70b)
        temperature: Temperature setting for the model (default: 0)
        prompt_type: Type of prompt (default: closed_target)
        batch_size: Batch size for processing (default: 100)
        **kwargs: Additional configuration options to override
    
    Returns:
        str: Path to the created configuration file
    """
    # Load template
    template_path = Path(__file__).parent / "templates" / template
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path) as f:
        config = yaml.safe_load(f)
    
    # Get next experiment number
    experiments_dir = Path(__file__).parent / "experiments"
    exp_num = get_next_exp_number(experiments_dir)
    exp_key = f"exp_{exp_num:05d}"
    
    # Update configuration
    config["experiment"].update({
        "key": exp_key,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "description": description
    })
    
    config["user"].update({
        "user_id": user_id,
        "username": username or user_id
    })
    
    config["api"]["groq"].update({
        "model": model,
        "temperature": temperature
    })
    
    config["data"]["batch_size"] = batch_size
    config["prompts"]["type"] = prompt_type
    
    # Apply any additional overrides
    for key, value in kwargs.items():
        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            current = current[k]
        current[keys[-1]] = value
    
    # Generate filename
    filename = f"{exp_key}.yaml"
    config_path = experiments_dir / filename
    
    # Create experiments directory if it doesn't exist
    experiments_dir.mkdir(parents=True, exist_ok=True)
    
    # Save config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)
    
    print(f"Created experiment configuration: {config_path}")
    return str(config_path)




if __name__ == "__main__":

################################################################################

# SET UP: Create a new experiment configuration

################################################################################

    description = "EXAMPLE: Create a new experiment configuration"

    user_ids = ["31499533", "31499533", "31499533"]

    user_id = "31499533"
    username = "1Tiamo"

    model = "deepseek-r1-distill-llama-70b" # "llama-3.3-70b-versatile"

    batch_size = 200
    context = {"include_article_body": False,
             "include_most_liked_comment": True,
             "include_parent_comment": True,
             "include_oldest_comment": True}
    
    prompt_type = "closed_target"

    for user_id in user_ids:
        config_path = create_experiment_config(
            user_id = user_id,
            description = description,
            username = username,
            batch_size = batch_size,
            context = context,
        model = model,
        prompt_type = prompt_type
    )