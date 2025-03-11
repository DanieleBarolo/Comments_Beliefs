from utils import trace_comment_thread, get_article_text, load_comments_from_jsonl_gz
from pprint import pprint
from pymongo import MongoClient


# Example User:

user_name = "2bills"  # Ensure this matches the actual filename in selected_users_comments_compressed/
base_dir = "./selected_users_data/selected_users_comments_compressed"
user_df = load_comments_from_jsonl_gz(user_name, base_dir)
user_df

get_article_text("5098126553", "Breitbart")

# check the rows that do not have nan under parent
print(user_df.shape)
pprint(user_df[user_df['parent'].notna()].loc[18,'raw_message'])
user_df[user_df['parent'].notna()].reset_index()['art_id'].value_counts()
pprint(user_df[user_df['parent'].notna()].reset_index().loc[0,'parent'])

answer_comments_df = user_df[user_df['parent'].notna()].reset_index().copy()
answer_comments_df['art_id'].value_counts()


####
answer_comments_df._id.tolist()[0]

for threat_comments in answer_comments_df._id.tolist()[:10]:
    print()
    trace_comment_thread(comment_id=threat_comments, collection = 'Breitbart', verbose=True, retrieve_article=True)

