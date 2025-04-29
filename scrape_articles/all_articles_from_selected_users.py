from pymongo import MongoClient

########################################################################################
# Take all comments from selected users 

###############################################################################
# Import and plot data (to ignore for now)                                    #
###############################################################################

# import matplotlib.pyplot as plt
import gzip          
import json          
import pandas as pd  
from pathlib import Path  
import os

def load_comments_from_jsonl_gz(user_name, base_dir):
    """
    Load all comments for a specific user from a compressed JSONL file (.jsonl.gz).
    
    Parameters:
    - user_name: The name of the user.
    - base_dir: The base directory where the JSONL files are stored.
    """
    base_dir = Path(base_dir)
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




########################################################################################

# Directory containing the compressed user comment files
base_dir = "../selected_users_data/selected_users_comments_compressed"

# Initialize an empty set to store unique article IDs
articles_ids_set = set()

def load_comments_from_jsonl_gz(filename, base_dir):
    """Load comments from a JSONL.GZ file into a DataFrame."""
    file_path = os.path.join(base_dir, filename)
    data = []
    
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    return pd.DataFrame(data)

# Loop through all .jsonl.gz files in the directory
for filename in os.listdir(base_dir):
    if filename.endswith(".jsonl.gz"):  # Process only the correct file type
        user_df = load_comments_from_jsonl_gz(filename, base_dir)
        
        if "art_id" in user_df.columns:  # Ensure column exists
            articles_ids_set.update(user_df["art_id"].dropna().astype(str).tolist())

########################################################################################
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/") 
db = client["Articles"]  

collection = db["Breitbart"] 

# Step 2: Query MongoDB for matching article IDs
query = {"_id": {"$in": list(articles_ids_set)}}
projection = {"_id": 1, "link":1}  # Retrieve only art_id and link

articles_data = list(collection.find(query, projection))  # Get matching documents

# Step 3: Save results to a CSV file
df = pd.DataFrame(articles_data)
csv_filename = "breitbart_articles_links.csv"
df.to_csv(csv_filename, index=False)

print(f"✅ Saved {len(df)} articles to {csv_filename}")