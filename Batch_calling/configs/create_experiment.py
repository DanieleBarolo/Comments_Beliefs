import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import re
import sys
# Add the parent directory to sys.path to import from Batch_calling
sys.path.append(str(Path(__file__).parent.parent))
from targets import target_list

def get_next_exp_number(experiments_dir: Path) -> int:
    """Get the next available experiment number."""
    pattern = re.compile(r'exp_(\d{5})')
    max_num = 0
    
    if experiments_dir.exists():
        for file in experiments_dir.glob("*.yaml"):
            if match := pattern.search(file.stem):
                max_num = max(max_num, int(match.group(1)))
    
    return max_num + 1

def load_prompt_template(prompt_type: str) -> str:
    """Load the prompt template for the given prompt type."""
    template_path = Path(__file__).parent.parent / "prompts" / prompt_type / "template.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    
    with open(template_path) as f:
        return f.read().strip()

def load_system_prompt() -> str:
    """Load the system prompt from the system_prompt.txt file."""
    system_prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"
    if not system_prompt_path.exists():
        raise FileNotFoundError(f"System prompt file not found: {system_prompt_path}")
    
    with open(system_prompt_path) as f:
        return f.read().strip()

def create_experiment_config(
    user_ids: List[str],
    description: str,
    template: str = "base_config.yaml",
    usernames: Optional[List[str]] = None,
    model: str = "deepseek-r1-distill-llama-70b",
    temperature: float = 0,
    prompt_type: str = "closed_target",
    batch_size: int = 100,
    **kwargs
) -> Dict:
    """
    Create a new experiment configuration.
    
    Args:
        user_ids: List of user IDs for the experiment
        description: Description of the experiment
        template: Template file to use (default: base_config.yaml)
        usernames: Optional list of usernames corresponding to user_ids
        model: Model to use (default: deepseek-r1-distill-llama-70b)
        temperature: Temperature setting for the model (default: 0)
        prompt_type: Type of prompt (default: closed_target)
        batch_size: Batch size for processing (default: 100)
        **kwargs: Additional configuration options to override
    
    Returns:
        Dict: The configuration dictionary
    """
    # Load template
    template_path = Path(__file__).parent / "templates" / template
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path) as f:
        config = yaml.safe_load(f)
    
    # Create a new ordered dictionary with sections in the desired order
    ordered_config = {}
    
    # Experiment section
    ordered_config["experiment"] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "description": description
    }
    
    # Users section
    ordered_config["users"] = {
        "user_ids": user_ids,
        "user_names": usernames if usernames else []
    }
    
    # API section
    ordered_config["api"] = config["api"]
    ordered_config["api"]["groq"].update({
        "model": model,
        "temperature": temperature
    })
    
    # Data section
    ordered_config["data"] = config["data"]
    ordered_config["data"]["batch_size"] = batch_size
    
    # Context section
    ordered_config["context"] = config.get("context", {})
    if "context" in kwargs:
        ordered_config["context"].update(kwargs.pop("context"))
    
    # Paths section (if exists in template)
    if "paths" in config:
        ordered_config["paths"] = config["paths"]
    
    # Prompts section
    ordered_config["prompts"] = {
        "type": prompt_type,
        "system_prompt": load_system_prompt(),
        "prompt_template": load_prompt_template(prompt_type),
        "targets": list(target_list) if prompt_type == "closed_target" else None
    }
    
    # Apply any additional overrides
    for key, value in kwargs.items():
        keys = key.split(".")
        current = ordered_config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    return ordered_config


if __name__ == "__main__":

################################################################################

# SET UP: Create a new experiment configuration

################################################################################

    description = "EXAMPLE: Create a new experiment configuration"

    user_ids = ["31499533", "31499534"]
    usernames = ["1Tiamo", "JohnDoe"]

    model = "deepseek-r1-distill-llama-70b" # "llama-3.3-70b-versatile"

    batch_size = 300
    context = {"include_article_body": False,
             "include_most_liked_comment": True,
             "include_parent_comment": True,
             "include_oldest_comment": True}
    
    prompt_type = "closed_target"

    config = create_experiment_config(
            user_ids = user_ids,
            description = description,
            usernames = usernames,
            batch_size = batch_size,
            context = context,
            model = model,
            prompt_type = prompt_type
    )

    #save config example
    config_path = Path(__file__).parent / "experiments" / "example_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)

    print(f"Experiment configuration saved to {config_path}")
