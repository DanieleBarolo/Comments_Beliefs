from utils import trace_comment_thread, get_article_text, load_comments_from_jsonl_gz
from pprint import pprint
from pymongo import MongoClient


# Example User:

user_name = "2bills"  # Ensure this matches the actual filename in selected_users_comments_compressed/
base_dir = "./selected_users_data/selected_users_comments_compressed"
user_df = load_comments_from_jsonl_gz(user_name, base_dir)
user_df

# check the rows that do not have nan under parent
print(f"User's name {user_name}")
print(f"Number of comments {user_df.shape[0]}")
print(f"Number of comments that are answers to other comments: {user_df[user_df['parent'].notna()].shape[0]}")

answer_comments_df = user_df[user_df['parent'].notna()].reset_index().copy()
answer_comments_df['art_id'].value_counts()


####
answer_comments_df._id.tolist()[0]

for threat_comments in answer_comments_df._id.tolist()[:10]:
    print()
    trace_comment_thread(comment_id=threat_comments, collection = 'Breitbart', verbose=True, retrieve_article=True)

