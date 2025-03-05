from utils import load_comments_from_jsonl_gz
from pprint import pprint

# Example Usage:
user_name = "2bills"  # Ensure this matches the actual filename in selected_users_comments_compressed/
user_df = load_comments_from_jsonl_gz(user_name)

user_df.columns

for message in user_df['raw_message']:
    pprint(message)
    print("-"*50)


user_df['art_id'].value_counts()

user_df.shape