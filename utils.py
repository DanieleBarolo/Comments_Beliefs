import pandas as pd
import os
import gzip
import json
from pathlib import Path

# Function to load comments for a specific user from compressed JSONL (.jsonl.gz)
def load_comments_from_jsonl_gz(user_name):
    """
    Load all comments for a specific user from a compressed JSONL file (.jsonl.gz).
    """
    script_dir = Path(__file__).parent
    base_dir = script_dir / "selected_users_data" / "selected_users_comments_compressed"
    user_path = base_dir / f"{user_name}.jsonl.gz"
    if not user_path.exists():
        raise FileNotFoundError(f"File not found: {user_path}\nCheck the file name and directory!")

    comments_list = []

    # Open the compressed file with gzip
    with gzip.open(user_path, "rt", encoding="utf-8") as file:
        for line in file:
            comment = json.loads(line)
            comments_list.append(comment)

    comments_df = pd.DataFrame(comments_list)
    # Ensure 'createdAt' exists and is in datetime format
    if "createdAt" in comments_df.columns:
        comments_df["createdAt"] = pd.to_datetime(comments_df["createdAt"], errors="coerce")

    return comments_df