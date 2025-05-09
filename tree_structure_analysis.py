from utils import trace_comment_thread, get_article_text, load_comments_from_jsonl_gz
from pprint import pprint
from pymongo import MongoClient


# Example User:

user_name = "1Tiamo"  # Ensure this matches the actual filename in selected_users_comments_compressed/
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



### Access global topic of one comment

# Find the topic
from datetime import datetime
import os 
import pyarrow.feather as feather 
import pyarrow.compute as pc


answer_comments_df[['_id', 'raw_message']]
sample_id = '1000981651'
user_df[user_df['_id'] == '1000981651']['createdAt']
full_date = user_df[user_df['_id'] == '1000981651']['createdAt'].iloc[0]
mm_yy = full_date.strftime("%m%y")

topic_path = "/Volumes/Untitled/seungwoong.ha/collmind/transform_global/breitbart/breitbart_new_s3_r19_h225_u20_t10"
name_file = f"batch-{mm_yy}.arrow"

gb = feather.read_table(os.path.join(topic_path, name_file))
df = gb.to_pandas()
df[df['id'] == sample_id]


#####

