from pathlib import Path
from datetime import datetime
import os

class ExperimentPaths:
    """Handles all experiment-related paths and directory creation."""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.absolute()
            self.base_dir = project_root / "data" / "experiments"
        else:
            self.base_dir = Path(base_dir)
        self._ensure_base_dirs()
    
    def _ensure_base_dirs(self):
        """Ensure all base directories exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        (self.base_dir / "users").mkdir(exist_ok=True)
        (self.base_dir / "runs").mkdir(exist_ok=True)
    
    def get_run_id(self, experiment_type: str, model: str, run_number: int = 1) -> str:
        """Generate a run ID in the format YYYYMMDD_TYPE_MODEL_XXX."""
        date = datetime.now().strftime("%Y%m%d")
        type_abbr = self._get_type_abbreviation(experiment_type)
        model_abbr = self._get_model_abbreviation(model)
        return f"{date}_{type_abbr}_{model_abbr}_{run_number:03d}"
    
    def _get_type_abbreviation(self, experiment_type: str) -> str:
        """Get abbreviation for experiment type."""
        type_map = {
            "closed_target": "CT",
            "open_target": "OT"
        }
        return type_map.get(experiment_type.lower(), experiment_type[:2].upper())
    
    def _get_model_abbreviation(self, model: str) -> str:
        """Get abbreviation for model name."""
        model_map = {
            "deepseek-r1-distill-llama-70b": "DS70B",
            "llama-3.3-70b-versatile": "L70B"
        }
        return model_map.get(model.lower(), model[:5].upper())
    
    def get_run_dir(self, run_id: str) -> Path:
        """Get the path for a specific run."""
        run_dir = self.base_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
    
    def get_user_dir(self, user_id: str) -> Path:
        """Get the path for a specific user."""
        user_dir = self.base_dir / "users" / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def get_user_run_dir(self, user_id: str, run_id: str) -> Path:
        """Get the path for a specific user's run."""
        run_dir = self.get_user_dir(user_id) / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
    
    def get_config_path(self, run_id: str) -> Path:
        """Get the path for a run's config file."""
        return self.get_run_dir(run_id) / "config.yaml"
    
    def get_users_path(self, run_id: str) -> Path:
        """Get the path for a run's users file."""
        return self.get_run_dir(run_id) / "users.json"
    
    def get_status_path(self, run_id: str) -> Path:
        """Get the path for a run's status file."""
        return self.get_run_dir(run_id) / "status.json"
    
    def get_batch_path(self, user_id: str, run_id: str) -> Path:
        """Get the path for a user's batch file."""
        return self.get_user_run_dir(user_id, run_id) / "batch.jsonl"
    
    def get_upload_path(self, user_id: str, run_id: str) -> Path:
        """Get the path for a user's upload file."""
        return self.get_user_run_dir(user_id, run_id) / "upload.json"
    
    def get_results_path(self, user_id: str, run_id: str) -> Path:
        """Get the path for a user's results file."""
        return self.get_user_run_dir(user_id, run_id) / "results.json"
    
    def update_status(self, run_id: str, step: str, status: bool = True):
        """Update the status of a specific step in a run."""
        status_path = self.get_status_path(run_id)
        if not status_path.exists():
            status_data = {
                "created": datetime.now().isoformat(),
                "steps": {},
                "last_updated": datetime.now().isoformat()
            }
        else:
            import json
            with open(status_path) as f:
                status_data = json.load(f)
        
        status_data["steps"][step] = status
        status_data["last_updated"] = datetime.now().isoformat()
        
        with open(status_path, 'w') as f:
            json.dump(status_data, f, indent=2)
