import pandas as pd
import pyarrow.parquet as pq

#############
# Constants (From /Volumes/Untitled/seungwoong.ha/collmind/proj_utils_gpu.py")#
#############
from datetime import datetime

DATA_DIR = "/data/comments/valentin"

COLLECTION_NAMES = ["Atlantic", "Breitbart", "Gatewaypundit", "Motherjones", "Thehill"]

CORRECTED_DICT = {
    "Gatewaypundit": "0",
    "Breitbart": "1",
    "Thehill": "2",
    "Atlantic": "3",
    "Motherjones": "4",
}

CORRECTED_DICT_REVERSE = {
    "0": "Gatewaypundit",
    "1": "Breitbart",
    "2": "Thehill",
    "3": "Atlantic",
    "4": "Motherjones"
}

DATE_RANGES = {
    "Atlantic": (datetime(2012, 6, 1), datetime(2018, 5, 1)),
    "Breitbart": (datetime(2012, 6, 1), datetime(2023, 4, 1)),
    "Gatewaypundit": (datetime(2015, 1, 1), datetime(2023, 4, 1)),
    "Motherjones": (datetime(2012, 6, 1), datetime(2019, 9, 1)),
    "Thehill": (datetime(2012, 6, 1), datetime(2022, 3, 1))
}

MODEL_NAMES = {
    "Atlantic": 'atlantic_new_s4_r19_h200_u80_t10',
    "Breitbart": 'breitbart_new_s3_r19_h225_u20_t10',
    "Gatewaypundit": 'gatewaypundit_new_s4_r19_h400_u30_t10',
    "Motherjones": 'motherjones_new_s5_r19_h425_u90_t10',
    "Thehill": 'thehill_new_s2_r19_h300_u80_t10',
    "global": 'global_new_s1_r19_h325_u20_t10',
    "title": 'title_new_s2_r19_h35_u50_t10'
}


# Read the schema of the Parquet file
parquet_file = pq.ParquetFile("/Volumes/T7 Shield/user_trajectory_df.parquet")

# Print the schema to inspect the columns and their data types
print(parquet_file.schema)

parquet_file = pq.ParquetFile("/Volumes/T7 Shield/user_trajectory_df.parquet")

# Define a reasonable batch size based on your memory constraints
batch_size = 1000
all_dfs = []

for batch in parquet_file.iter_batches(batch_size=batch_size):
    df_batch = batch.to_pandas()
    # Either process each batch individually or collect them
    all_dfs.append(df_batch)


# Optionally combine all batches if you need the complete dataset
full_df = pd.concat(all_dfs, ignore_index=True)
full_df


##############################################################################

# GOAL 400 COMMENTS 
# Sample 4 articles for 3 news provider: Breitbart, Motherjones, Thehill

# Per each user provider:
#  --> we will have to read 4 articles and classify 15 comments for each

# in total 200 comments classified by annotator. 

# [check] the articles should be covering fairly different topics
# [check] the comments should be from users with at least 500 comments in general


# for every provider, do:
# 1. filter the dataframe to only include users who commented on one provider
# 2. filter the dataframe to only include users who have at least 500 comments
# 3. select articles ids that are most shared across these users
# 4. select ~23 comments per article


##############################################################################
# Mother Jones
##############################################################################
collection_name = "Motherjones"

# 1. filter the dataframe to only include users who commented on one provider
# keep only rows that have 3 inside the collection_id column 


collection_id = int(CORRECTED_DICT[collection_name])
filtered_df = full_df[full_df['collection_id'].apply(lambda x: collection_id in x)]

# keep only users with at least 500 comments
filtered_df = filtered_df[filtered_df['num_comments'] >= 500]
filtered_df


# Function to check if all lists in the specified columns are of the same length
def check_list_lengths(row):
    lengths = [len(row['collection_id']), len(row['comment_id']), len(row['article_id']), len(row['createdAt'])]
    return all(length == lengths[0] for length in lengths)

# fucntion to the row by the collection_id
def filter_by_collection_id(row, collection_id):

    collection_name = CORRECTED_DICT_REVERSE[str(collection_id)]
    # Get the mask of indices where the collection_id is equal to the specified value
    mask = [index for index, val in enumerate(row['collection_id']) if val == collection_id]
    
    # Filter each list in the row based on the mask
    row['collection_id'] = [row['collection_id'][i] for i in mask]
    row['comment_id'] = [row['comment_id'][i] for i in mask]
    row['article_id'] = [row['article_id'][i] for i in mask]
    row['createdAt'] = [row['createdAt'][i] for i in mask]

    # re-compute the num_comments (length of the list)
    row[f'num_comments_{collection_name}'] = len(row['comment_id'])

    # Re-compute the age in days
    created_at_series = pd.Series(row['createdAt'])
    max_date = created_at_series.max()
    min_date = created_at_series.min()
    age_timedelta =  max_date - min_date
    
    row[f'age_{collection_name}'] = age_timedelta.days  # keep only the days

    return row

filtered_df = filtered_df.apply(filter_by_collection_id, axis=1, collection_id=collection_id) 

# 2. filter the dataframe to only include users who have at least 500 comments
filtered_df = filtered_df[filtered_df[f'num_comments_{collection_name}'] >= 500]
filtered_df 

# 3. select articles ids that are most shared across these users
# see the set of all articles ids. 
article_ids = set()
for index, row in filtered_df.iterrows():
    article_ids.update(row['article_id'])
article_ids = list(article_ids)
len(article_ids)
# count how often each article id appears in the dataframe
article_id_counts = {}
for article_id in article_ids:
    article_id_counts[article_id] = 0
for index, row in filtered_df.iterrows():
    for article_id in row['article_id']:
        article_id_counts[article_id] += 1
# sort the article ids by the number of times they appear in the dataframe
sorted_article_ids = sorted(article_id_counts.items(), key=lambda x: x[1], reverse=True)

most_shared_article_ids = [article_id for article_id, count in sorted_article_ids[:15]]

# 4. select 15 comments per article
# filter the df with only users that have that art id

from pymongo import MongoClient
def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

articles_collection = init_mongo("Articles", collection_name)
art_id_to_title_motherjones = {}
for art_id in most_shared_article_ids:
    art_object = articles_collection.find_one({'_id': art_id})
    art_id_to_title_motherjones[art_id] = art_object['clean_title']
art_id_to_title_motherjones

# TO do manually, so to selecte different topics
# Trump, O'Relly, Vaccines, Anti-Obamacare, God, Guns, 
selected_articles_idx = ['5392511582', '3530917221', '2278909220', '3501101516', '2475779307', '3740800309']

400 / 3 / 6

# Sample 23 comments per each of these articles and save them in a csv
filtered_df

import random
# filter the df with only users that have that art id
full_sampled_comments_df = pd.DataFrame()

for target_art_id in selected_articles_idx:
    # make a dict with "user_id" as key and a list of comments as value
    user_comments_dict = {}
    for index, row in filtered_df.iterrows():
        if target_art_id in row['article_id']:
            user_id = row['user_id']
            if user_id not in user_comments_dict:
                user_comments_dict[user_id] = []
            for i, art_id in enumerate(row['article_id']):
                if art_id == target_art_id:
                    user_comments_dict[user_id].append(row['comment_id'][i])
    # sample 23 of these users 
    # sample one comment id for that user
    # make a df with art_id, user_id, comment_id
    sampled_comments = []
    for user_id, comment_ids in user_comments_dict.items():
        if len(comment_ids) > 0:
            sampled_comment_id = random.choice(comment_ids)
            sampled_comments.append({
                'article_id': target_art_id,
                'user_id': user_id,
                'comment_id': sampled_comment_id
            })

    # sample 23 comments
    sampled_comments = random.sample(sampled_comments, min(23, len(sampled_comments)))
    sampled_comments_df = pd.DataFrame(sampled_comments)
    # concat the df with the full_sampled_comments_df
    full_sampled_comments_df = pd.concat([full_sampled_comments_df, sampled_comments_df], ignore_index=True)

full_sampled_comments_df.to_csv(f"sampled_comments_{collection_name.lower()}.csv", index=False)

##############################################################################
# Thehill 
##############################################################################
collection_name = "Thehill"

# 1. filter the dataframe to only include users who commented on one provider
# keep only rows that have 3 inside the collection_id column 


collection_id = int(CORRECTED_DICT[collection_name])
filtered_df = full_df[full_df['collection_id'].apply(lambda x: collection_id in x)]

# keep only users with at least 500 comments in generale
filtered_df = filtered_df[filtered_df['num_comments'] >= 500]
filtered_df
filtered_df = filtered_df.apply(filter_by_collection_id, axis=1, collection_id=collection_id) 
filtered_df

# 2. filter the dataframe to only include users who have at least 500 comments in this news provider
filtered_df = filtered_df[filtered_df[f'num_comments_{collection_name}'] >= 500]
filtered_df 

# 3. select articles ids that are most shared across these users
# see the set of all articles ids. 
article_ids = set()
for index, row in filtered_df.iterrows():
    article_ids.update(row['article_id'])
article_ids = list(article_ids)
len(article_ids)
# count how often each article id appears in the dataframe
article_id_counts = {}
for article_id in article_ids:
    article_id_counts[article_id] = 0
for index, row in filtered_df.iterrows():
    for article_id in row['article_id']:
        article_id_counts[article_id] += 1
# sort the article ids by the number of times they appear in the dataframe
sorted_article_ids = sorted(article_id_counts.items(), key=lambda x: x[1], reverse=True)
sorted_article_ids

# manually select 6 articles from top shared articles

most_shared_article_ids = [article_id for article_id, count in sorted_article_ids[:15]]

# 4. select `23` comments per article
# filter the df with only users that have that art id

from pymongo import MongoClient
def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

articles_collection = init_mongo("Articles", collection_name)
art_id_to_title_thehill = {}
for art_id in most_shared_article_ids:
    art_object = articles_collection.find_one({'_id': art_id})
    art_id_to_title_thehill[art_id] = art_object['clean_title']
art_id_to_title_thehill

# TO do 
# Trump, Zelenskyy, Biden, Shooter njuries, Senat/GOP, Iran, 
selected_articles_idx = ['8283465962', '9046450607', '8958859912', '7568558100', '8555615834', '7804760132']



# Sample 23 comments per each of these articles and save them in a csv

import random
# filter the df with only users that have that art id
full_sampled_comments_df = pd.DataFrame()

for target_art_id in selected_articles_idx:
    # make a dict with "user_id" as key and a list of comments as value
    user_comments_dict = {}
    for index, row in filtered_df.iterrows():
        if target_art_id in row['article_id']:
            user_id = row['user_id']
            if user_id not in user_comments_dict:
                user_comments_dict[user_id] = []
            for i, art_id in enumerate(row['article_id']):
                if art_id == target_art_id:
                    user_comments_dict[user_id].append(row['comment_id'][i])
    # sample 23 of these users 
    # sample one comment id for that user
    # make a df with art_id, user_id, comment_id
    sampled_comments = []
    for user_id, comment_ids in user_comments_dict.items():
        if len(comment_ids) > 0:
            sampled_comment_id = random.choice(comment_ids)
            sampled_comments.append({
                'article_id': target_art_id,
                'user_id': user_id,
                'comment_id': sampled_comment_id
            })

    # sample 23 comments
    sampled_comments = random.sample(sampled_comments, min(23, len(sampled_comments)))
    sampled_comments_df = pd.DataFrame(sampled_comments)
    # concat the df with the full_sampled_comments_df
    full_sampled_comments_df = pd.concat([full_sampled_comments_df, sampled_comments_df], ignore_index=True)

full_sampled_comments_df.to_csv(f"sampled_comments_{collection_name.lower()}.csv", index=False)


##############################################################################
# Breitbart 
##############################################################################
collection_name = "Breitbart"

# 1. filter the dataframe to only include users who commented on one provider
# keep only rows that have 3 inside the collection_id column 


collection_id = int(CORRECTED_DICT[collection_name])
filtered_df = full_df[full_df['collection_id'].apply(lambda x: collection_id in x)]

# keep only users with at least 500 comments in generale
filtered_df = filtered_df[filtered_df['num_comments'] >= 500]
filtered_df
from tqdm import tqdm

# Add tqdm to show progress
tqdm.pandas()  # This enables progress_apply() for pandas

filtered_df = filtered_df.progress_apply(filter_by_collection_id, axis=1, collection_id=collection_id)
filtered_df

# 2. filter the dataframe to only include users who have at least 500 comments in this news provider
filtered_df = filtered_df[filtered_df[f'num_comments_{collection_name}'] >= 500]
filtered_df 

# 3. select articles ids that are most shared across these users
# see the set of all articles ids. 
article_ids = set()
for index, row in filtered_df.iterrows():
    article_ids.update(row['article_id'])
article_ids = list(article_ids)
len(article_ids)
# count how often each article id appears in the dataframe
article_id_counts = {}
for article_id in article_ids:
    article_id_counts[article_id] = 0
for index, row in filtered_df.iterrows():
    for article_id in row['article_id']:
        article_id_counts[article_id] += 1
# sort the article ids by the number of times they appear in the dataframe
sorted_article_ids = sorted(article_id_counts.items(), key=lambda x: x[1], reverse=True)
sorted_article_ids

# manually select 6 articles from top shared articles

most_shared_article_ids = [article_id for article_id, count in sorted_article_ids[15:30]]

# 4. select `23` comments per article
# filter the df with only users that have that art id

from pymongo import MongoClient
def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

articles_collection = init_mongo("Articles", collection_name)
art_id_to_title_breitbart = {}
for art_id in most_shared_article_ids:
    art_object = articles_collection.find_one({'_id': art_id})
    art_id_to_title_breitbart[art_id] = art_object['clean_title']
art_id_to_title_breitbart

# TO do 
# Hillary Clinton, Mass Shooting , Donald Trump, Police, Elections results, Illegal Aliens
selected_articles_idx = ['5288423876', '6185044719', '9638510923', '6998004795', '8263361810', '6141968269']

# Sample 23 comments per each of these articles and save them in a csv

import random
# filter the df with only users that have that art id
full_sampled_comments_df = pd.DataFrame()

for target_art_id in selected_articles_idx:
    # make a dict with "user_id" as key and a list of comments as value
    user_comments_dict = {}
    for index, row in filtered_df.iterrows():
        if target_art_id in row['article_id']:
            user_id = row['user_id']
            if user_id not in user_comments_dict:
                user_comments_dict[user_id] = []
            for i, art_id in enumerate(row['article_id']):
                if art_id == target_art_id:
                    user_comments_dict[user_id].append(row['comment_id'][i])
    # sample 23 of these users 
    # sample one comment id for that user
    # make a df with art_id, user_id, comment_id
    sampled_comments = []
    for user_id, comment_ids in user_comments_dict.items():
        if len(comment_ids) > 0:
            sampled_comment_id = random.choice(comment_ids)
            sampled_comments.append({
                'article_id': target_art_id,
                'user_id': user_id,
                'comment_id': sampled_comment_id
            })

    # sample 23 comments
    sampled_comments = random.sample(sampled_comments, min(23, len(sampled_comments)))
    sampled_comments_df = pd.DataFrame(sampled_comments)
    # concat the df with the full_sampled_comments_df
    full_sampled_comments_df = pd.concat([full_sampled_comments_df, sampled_comments_df], ignore_index=True)

full_sampled_comments_df.to_csv(f"sampled_comments_{collection_name.lower()}.csv", index=False)

