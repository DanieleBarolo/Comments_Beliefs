# Experiment Configuration System

Simple configuration system.

## Structure

```
configs/
├── templates/           # Base template
│   └── base_config.yaml
├── experiments/         # Generated configs
└── create_experiment.py # Generation script
```

## Usage

Create a new experiment:
```python
from configs.create_experiment import create_experiment_config, get_experiment_filenames

# Create new experiment (automatically gets next number: exp_001, exp_002, etc.)
config_path = create_experiment_config(
    user_id="31499533",
    description="Test experiment with larger size for user x",
    batch_size=500,
    batch={
        "include_article_body": False,
        "include_article_comments": True,
        "include_parent_comment": True,
        "include_oldest_comment": True,
        "include_most_liked_comment": True
    }  # override batch options
)

# Get related files
files = get_experiment_filenames(config_path)
print(f"Config: {files['config']}")     # exp_001.yaml
print(f"Batch: {files['batch']}")       # exp_001.jsonl
print(f"Results: {files['results']}")   # exp_001.jsonl 