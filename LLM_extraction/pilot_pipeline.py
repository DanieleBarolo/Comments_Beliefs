import numpy as np 
import pandas as pd 
from datetime import datetime
import os 
import pyarrow.feather as feather 
import pyarrow.compute as pc
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import json 
import numpy as np
from utils import trace_comment_thread, get_article_text, load_comments_from_jsonl_gz
from pprint import pprint
from pymongo import MongoClient

# setup
model='gpt-4o-mini' # gpt-4o being the flagship
temperature=0.8

load_dotenv(".env")
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

def json_persona(model, background, question, format):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": background},
            {"role": "user", "content": question},
            ],
        response_format=format,
    )
    return completion.choices[0].message.parsed.model_dump()

def init_mongo(collection): 
    client = MongoClient("mongodb://localhost:27017/")
    comment_db = client["Comments"]
    comment_collection = comment_db[collection]
    return comment_collection

# construct query: # 
def trace_comment_thread(comment_collection, comment_id, parent_id, collection='Breitbart'):

    # Initialize thread tracking lists
    article = None
    article_title = ''
    article_link = ''
    article_body = ''
    parent_text = ''
    
    # retrieve comment
    comment = comment_collection.find_one({"_id": comment_id})
    comment_text = comment.get('raw_message')
    
    # retrieve parent 
    parent = comment_collection.find_one({"_id": parent_id})
    if parent: 
        parent_text = parent.get('raw_message') 
    
    # retrieve article 
    # something to load instead if it exists 
    article_id = str(int(comment['art_id']))
    article = get_article_text(article_id, collection)
    if article: 
        article_title = article.get('title')
        article_link = article.get('link')
        article_body = article.get('body')

    return {
        "article_title": article_title,
        "article_link": article_link,
        "article_body": article_body,
        "parent_id": parent_id,  
        "parent_text": parent_text, 
        "comment_ids": comment_id,
        "comment_texts": comment_text
    }

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

# extract the components of the thread + topic 
comm_list = []
for comment, parent in zip(comm_id, parent_id):
    # get all of the essential components
    # ahh of course this will take a while if we need to fetch many articles.
    comm_dict = trace_comment_thread(comment_collection, comment, parent, collection = 'Breitbart')

    # add user name 
    comm_dict['user_name'] = user_name
    
    # add topic 
    comm_dict['topic'] = get_topic(user_name, comment)

    comm_list.append(comm_dict)

# which topics do we have for this user? 
from collections import Counter
topic_lst = []
for dict_ in comm_list: 
    topic = dict_['topic'] 
    topic_lst.append(topic)
counted = Counter(topic_lst)
sorted_dict = dict(sorted(counted.items(), key=lambda item: item[1], reverse=True))

# hmmm okay this guy has mostly: 
# -1: no topic
# 1: bullshit topic
# 14: climate change
# 8: god, jesus stuff. 
# ... 

# but sure let us see whether we can "find" the climate + god things. 
topics = [1, 8, 14]
sub_list = []
for topic in topics: 
    sub_list.append([dict_ for dict_ in comm_list if dict_['topic'] == topic])

# now we need to create the prompt ...

# pipeline: 
background = ...
question = ... 