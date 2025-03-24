from utils import init_mongo, load_comments_from_jsonl_gz, trace_comment_thread, get_topic
import numpy as np
from collections import Counter
import pyarrow.feather as feather
import json


# define functions

def top_n_comments(user_name, top_n, base_dir="../selected_users_data/selected_users_comments_compressed"):
    user_df = load_comments_from_jsonl_gz(user_name, base_dir)
    # extract the requested comments 
    user_selection = user_df.head(top_n)
    # get the comment and parent ids
    comm_id, parent_id = user_selection['_id'].tolist(), user_selection['parent'].tolist()
    # clean the parent ids 
    parent_id = ["" if np.isnan(x) else str(int(x)) for x in parent_id]
    return comm_id, parent_id

def get_topic(
    user_name, 
    comment_id, 
    base_dir="../selected_users_data/selected_users_comments_compressed",
    topic_path="/Volumes/Untitled/seungwoong.ha/collmind/transform_global/breitbart/breitbart_new_s3_r19_h225_u20_t10"):
    
    user_df = load_comments_from_jsonl_gz(user_name, base_dir)
    full_date = user_df[user_df['_id'] == comment_id]['createdAt'].iloc[0]
    mmyy = full_date.strftime("%m%y")
    
    arrow_name = f"batch-{mmyy}.arrow"
    topic_table = feather.read_table(os.path.join(topic_path, arrow_name))
    topic_df = topic_table.to_pandas()
    topic_int = topic_df[topic_df['id'] == comment_id]['topic'].iloc[0]
    
    return int(topic_int) 



# first init mongo database comments
comment_collection = init_mongo('Breitbart')

# select a user + get some comments
user_name = '1Tiamo'
base_dir = "../selected_users_data/selected_users_comments_compressed"
top_n = 100
comm_id, parent_id = top_n_comments(user_name, top_n, base_dir)

# comment_id = '1000896130'
# # retrieve comment
# comment = comment_collection.find_one({"_id": comment_id})
# comment_text = comment.get('raw_message')

# # retrieve article 
# # something to load instead if it exists 
# article_id = str(int(comment['art_id']))
# article = get_article_text(article_id, 'Breitbart')
# if article: 
#     article_title = article.get('title')
#     article_link = article.get('link')
#     article_body = article.get('body')


#saving data
file_name = f"pilot_users/{user_name}_top_{top_n}.jsonl"
# extract the components of the thread + topic 


for comment, parent in zip(comm_id, parent_id):

    with open(file_name, "a") as f: 
    # get all of the essential components
    # ahh of course this will take a while if we need to fetch many articles.
        comm_dict = trace_comment_thread(comment_collection, comment, parent, collection = 'Breitbart')

        # add user name 
        comm_dict['user_name'] = user_name
        
        # add topic 
        comm_dict['topic'] = get_topic(user_name, comment)

        f.write(json.dumps(comm_dict) + "\n")


