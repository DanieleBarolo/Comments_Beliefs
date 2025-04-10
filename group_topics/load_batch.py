import os 
import json 
from pymongo import MongoClient
import pandas as pd 

def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

# get all completed files 
def load_users_from_run(run_id):
    basepath = '../Batch_calling/data/experiments'
    runpath = os.path.join(basepath, 'runs', run_id)
    userspath = os.path.join(basepath, 'users')

    # load user 
    with open(os.path.join(runpath, 'users.json'), "r") as f:
        users = json.load(f)["users"]
    
    # Find path 
    userlist = []
    for user_id in users:
        userpath = os.path.join(userspath, str(user_id), run_id)
        
        # Extract file 
        data = []
        with open(os.path.join(userpath, 'batch_results.jsonl'), 'r') as f: 
            for line in f: 
                data.append(json.loads(line))
        
        userlist.append((user_id, data))
    return userlist

def get_comment_metadata(comment_id, collection_name):
    # initialize collections
    comment_collection = init_mongo(dbs = "Comments", collection = collection_name)
    comment = comment_collection.find_one(comment_id)
    comment_date = comment.get('createdAt')
    '''
    # article title 
    article_id = comment.get('art_id')
    parent_comment_id = comment.get('parent')
    oldest_comment_obj = comment_collection.find_one(
        {'art_id': article_id},
        sort=[('createdAt', 1)] # is it really 1 here and not 0?
    )
    oldest_comment_id = oldest_comment_obj.get('_id')
    liked_comment_obj = comment_collection.find_one(
        {'art_id': article_id},
        sort=[('likes', -1)]
    )
    liked_comment_id = liked_comment_obj.get('_id')
    '''
    return comment_date

def process_line(line):
    answer = line['response']['body']['choices'][0]['message']['content']
    answer = json.loads(answer)
    comment_id = line['custom_id']
    return answer['results'], comment_id #, comment_id

def collect_user_nodes(user_lines, collection='Breitbart'): 
    dataframe_lines = []
    for user_line in user_lines: 
        answers, comment_id = process_line(user_line)
        answers_df = pd.DataFrame(answers)
        comment_date = get_comment_metadata(comment_id, collection)
        answers_df['comment_id'] = comment_id
        answers_df['comment_date'] = comment_date
        dataframe_lines.append(answers_df)
    node_data = pd.concat(dataframe_lines)
    node_data = node_data[
        (node_data['stance'] == 'AGAINST') | 
        (node_data['stance'] == 'FAVOR')
        ]
    return node_data

# actually run it 
run_id = '20250409_CT_DS70B_002'
resultlist = load_users_from_run(run_id)

# make directory 
outdir = os.path.join('data', run_id)

if not os.path.exists(outdir): 
    os.makedirs(outdir)

for user_id, user_lines in resultlist: 
    # collect user nodes    
    user_df = collect_user_nodes(user_lines)
    # occasionally there are duplicates because of LLM hallucinations
    user_df = user_df.drop_duplicates()
    user_df.to_csv(os.path.join(outdir, f"{user_id}_raw.csv"), index=False)
