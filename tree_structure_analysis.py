from utils import load_comments_from_jsonl_gz
from pprint import pprint
from pymongo import MongoClient


# Example Usage:
user_name = "2bills"  # Ensure this matches the actual filename in selected_users_comments_compressed/
user_df = load_comments_from_jsonl_gz(user_name)

user_df.loc[0, 'user_id']


# check the rows that do not have nan under parent
print(user_df.shape)
user_df[user_df['parent'].notna()][['parent', 'art_id', 'raw_message']]
pprint(user_df[user_df['parent'].notna()].loc[18,'raw_message'])
pprint(user_df[user_df['parent'].notna()].reset_index().loc[0,'art_id'])


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update connection string if needed
db = client["Articles"]  # Database name
collection = db["Breitbart"]

article_id = user_df[user_df['parent'].notna()].reset_index().loc[0,'art_id']
article = collection.find_one({ "_id": article_id })
article_link = pprint(article['link'])
article

# check the parent of the comment 




