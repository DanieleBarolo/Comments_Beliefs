# Given the years longevity (in the Users database) take top 5% and  query the statistics: Mean and STD (for the CV score)
# This will be used to determine the users most constantly active throught time: those are going to be our sampel target.

# Imports 
import pymongo
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tqdm import tqdm
import csv
import os


##################################################
# 1. Query the Users DB to extract a sub sample of longly active users and at least 100 comments

# 1.1 Querying the full User Database (Breitbart)

client = pymongo.MongoClient("mongodb://localhost:27017/")
users_db = client["Users"]
users_breit_collection = users_db["Breitbart"]


# Query to fetch only necessary fields
query = {}
projection = {
    "_id": 1,  # user_id
    "comments_count": 1,
    "first_comment": 1,
    "last_comment": 1,
}

print("Start query all users ids")
# Fetch data
cursor = users_breit_collection.find(query, projection)
print("Finished query all users ids")

# Convert to DataFrame
df = pd.DataFrame(list(cursor))
df.rename(columns={"_id": "user_id"}, inplace=True)
df["years_active"] = (df["last_comment"] - df["first_comment"]).dt.total_seconds() / (3600 * 24 * 365)
df.drop(df.index[0], inplace=True) # removing users with None name (outlier)

# 1.2 Selct longest active users and with at least 100 comments 
percentile_95_time = df["years_active"].quantile(0.95)
df_top5_time = df[df["years_active"] >= percentile_95_time]
sub_sample_df = df_top5_time[df_top5_time['comments_count'] >= 100]

sub_sample_ids = sub_sample_df['user_id'].tolist()
print(f"Computed sub sample ids. Users are {len(sub_sample_ids)}")

##################################################
# 2. Compute the Coefficient of Variance for each sub_sampled user

# 2.1 Use the sub sample of ids to query the Comments DB: 
client = pymongo.MongoClient("mongodb://localhost:27017/")
comments_db = client["Comments"]
comments_breit_collection = comments_db["Breitbart"]

output_csv = "sub_sample_monthly_stats_breitbart.csv"
write_header = not os.path.exists(output_csv)

# Chunk size for incremental saving
CHUNK_SIZE = 1000  

# Process users in chunks to control memory usage
sub_sample_id_chunks = [
    sub_sample_ids[i:i + CHUNK_SIZE] for i in range(0, len(sub_sample_ids), CHUNK_SIZE)
]

print("Processing statistics using chunks")

for chunk in tqdm(sub_sample_id_chunks, desc="Processing User Chunks"):

    pipeline = [
        {"$match": {"user_id": {"$in": chunk}}},
        {"$project": {
            "user_id": 1,
            "yearMonth": {"$dateToString": {"format": "%Y-%m", "date": "$Created_At"}},
        }},
        {"$group": {
            "_id": {"user_id": "$user_id", "yearMonth": "$yearMonth"},
            "comment_count": {"$sum": 1}
        }},
    ]

    cursor = comments_breit_collection.aggregate(pipeline, allowDiskUse=True)
    df_chunk = pd.DataFrame(list(cursor))

    if df_chunk.empty:
        continue

    # Compute statistics per user directly with Pandas
    user_stats = (
        df_chunk.groupby("_id.user_id")["comment_count"]
        .agg(['mean', 'std', 'sum', 'count'])
        .reset_index()
        .rename(columns={
            'mean': 'mean_comments_per_month',
            'std': 'std_comments_per_month',
            'sum': 'total_comments',
            'count': 'months_counted',
            '_id.user_id': 'user_id'
        })
    )

    user_stats['cv_comments_per_month'] = (
        user_stats['std_comments_per_month'] / user_stats['mean_comments_per_month']
    ).replace([np.inf, -np.inf], np.nan)

    # Save immediately to CSV
    header = write_header
    user_stats.to_csv(output_csv, mode='a', header=header, index=False)
    write_header = False  # Ensure header is written only once

print(f"Finished collecting statistics. Results saved in {output_csv}")







# client = pymongo.MongoClient("mongodb://localhost:27017/")
# comments_db = client["Comments"]
# comments_breit_collection = comments_db["Breitbart"]

# # CSV file to store results incrementally
# output_csv = "sub_sample_monthly_stats_breitbart.csv"

# # Check if file exists to manage headers
# write_header = not os.path.exists(output_csv)

# print("Processing statistics for each of this users and saving the file")

# # 3. save the results for further visualisation.

# with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
#     writer = csv.DictWriter(file, fieldnames=[
#         "user_id", 
#         "mean_comments_per_month", 
#         "std_comments_per_month", 
#         "cv_comments_per_month", 
#         "months_counted", 
#         "total_comments"
#     ])
    
#     # Write header only once
#     if write_header:
#         writer.writeheader()

#     for user_id in tqdm(sub_sample_ids, desc="Processing Users"):
#         pipeline = [
#             {"$match": {"user_id": user_id}},
#             {"$project": {
#                 "yearMonth": {"$dateToString": {"format": "%Y-%m", "date": "$Created_At"}},
#             }},
#             {"$group": {
#                 "_id": "$yearMonth",
#                 "comment_count": {"$sum": 1}
#             }},
#             {"$sort": {"_id": 1}}
#         ]

#         cursor = comments_breit_collection.aggregate(pipeline)
#         df_user_comments = pd.DataFrame(list(cursor))

#         if df_user_comments.empty or len(df_user_comments) < 2:
#             continue  # Skip if insufficient data to calculate stats

#         # Compute statistics directly
#         mean_comments = df_user_comments["comment_count"].mean()
#         std_comments = df_user_comments["comment_count"].std()
#         cv_comments = std_comments / mean_comments if mean_comments != 0 else np.nan
#         total_comments = df_user_comments["comment_count"].sum()

#         # Save results directly to file, freeing memory immediately
#         writer.writerow({
#             "user_id": user_id,
#             "mean_comments_per_month": mean_comments,
#             "std_comments_per_month": std_comments,
#             "cv_comments_per_month": cv_comments,
#             "months_counted": len(df_user_comments),
#             "total_comments": total_comments
#         })

# print(f"Finish to collect statistics and saved in {output_csv}")

##################################################
# 3. Selecting only users with best statistics



##################################################
# 4 Collecting data . Selecting only users with best statistics