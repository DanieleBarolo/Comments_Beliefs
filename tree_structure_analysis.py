from utils import load_comments_from_jsonl_gz
from pprint import pprint

# Example Usage:
user_name = "cb75075"  # Ensure this matches the actual filename in selected_users_comments_compressed/
user_df = load_comments_from_jsonl_gz(user_name)

user_df.columns


# check the rows that do not have nan under parent
print(user_df.shape)
user_df[user_df['parent'].notna()]['parent']


user_df.columns