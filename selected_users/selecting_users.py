import pymongo
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Users"]
collection = db["Breitbart"]

# Peek at one document
doc = collection.find_one()
pprint(doc)

# estimated count 
estimated_count = collection.estimated_document_count()
print(f"Estimated count: {estimated_count}")

##################################################
# Querying the full User Database (Breitbart)

# Query to fetch only necessary fields
query = {}
projection = {
    "_id": 1,  # user_id
    "comments_count": 1,
    "first_comment": 1,
    "last_comment": 1,
    # "user_names": 1,
}

# Fetch data
cursor = collection.find(query, projection)

# Convert to DataFrame
df = pd.DataFrame(list(cursor))
df.rename(columns={"_id": "user_id"}, inplace=True)
df["years_active"] = (df["last_comment"] - df["first_comment"]).dt.total_seconds() / (3600 * 24 * 365)
# df.drop(df.index[0], inplace=True) # removing users with None name (outlier)
df

#filter raw that have more than one element in user_names

# df[df['user_names'].apply(lambda x: len(x) > 1)]

df[df['user_id'] == 'anonymous_user']
df[df['user_id'] == 'unknown_user']

# remove the anonymous_user and unknown_user
df = df[df['user_id'] != 'anonymous_user']
df = df[df['user_id'] != 'unknown_user']

df
##################################################
# Users Statistics 

# count rows with count == 1
percentage = (df[df["comments_count"] == 1].shape[0] / df.shape[0]) * 100
print(f"commenters with just one comment: {df[df['comments_count'] == 1].shape[0]} | {percentage:.2f}%")


# -----------------------------
# First Plot: 
# Distribution of numb of comments per user

# Step 1: Count how many users made X comments
count_distribution = df["comments_count"].value_counts().sort_index()
# Step 2: Compute cumulative fraction of users
cumulative_users = np.cumsum(count_distribution) / count_distribution.sum()
# Replot to add reference lines
fig, ax1 = plt.subplots(figsize=(12, 6))
# Histogram
sns.histplot(df["comments_count"], bins=50, kde=True, log_scale=(True, False), ax=ax1, color="blue", alpha=0.6)
ax1.set_xlabel("Number of Comments per User (Log Scale)")
ax1.set_ylabel("Number of Users", color="blue")
ax1.set_title("Distribution of Comment Counts in Breitbart")
# Cumulative Line
ax2 = ax1.twinx()
ax2.plot(cumulative_users.index, cumulative_users.values, color="red", marker="o", linestyle="-", alpha=0.7)
ax2.set_ylabel("Cumulative Fraction of Users", color="red")

percentile_90 = cumulative_users[cumulative_users >= 0.9].index[0]  # First value where cumulative fraction ≥ 0.9
percentile_95 = cumulative_users[cumulative_users >= 0.95].index[0]  # First value where cumulative fraction ≥ 0.95

# Draw Reference Lines at 90th and 95th Percentiles
ax2.axhline(y=0.9, color="black", linestyle="dashed", alpha=0.7)  # Horizontal line at 90% users
ax1.axvline(x=percentile_90, color="black", linestyle="dashed", alpha=0.7)  # Vertical line at 90th percentile

ax2.axhline(y=0.95, color="green", linestyle="dashed", alpha=0.7)  # Horizontal line at 95% users
ax1.axvline(x=percentile_95, color="green", linestyle="dashed", alpha=0.7)  # Vertical line at 95th percentile

# Annotate the points
ax2.annotate(f"90% of users ≤ {percentile_90} comments",
             xy=(percentile_90, 0.9),
             xytext=(percentile_90 * 1.5, 0.8),
             arrowprops=dict(facecolor='black', shrink=0.05),
             fontsize=12)

ax2.annotate(f"95% of users ≤ {percentile_95} comments",
             xy=(percentile_95, 0.95),
             xytext=(percentile_95 * 1.5, 0.85),
             arrowprops=dict(facecolor='green', shrink=0.05),
             fontsize=12)

plt.grid()
plt.show()


# -----------------------------
# Second Plot: 
# Distribution of years of activity across users 

plt.figure(figsize=(10, 6))

# Plot the histogram of "years_active"
sns.histplot(df["years_active"], bins=30, kde=True, color="blue")

plt.xlabel("Years Active")
plt.ylabel("Number of Users")
plt.title("Distribution of Years Active in Breitbart")
plt.grid()
plt.show()

# -----------------------------
# Third Plot: 
# Correlation between years active and num of comments

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x="years_active",
    y="comments_count",
    alpha=0.3  # transparency, so dense areas are darker
)

plt.xlabel("Years Active")
plt.ylabel("Comment Count") 
# plt.yscale("log")  # often needed if 'count' has a wide range
plt.title("Comment Count vs. Years Active")
plt.show()

# Compute the correlation
correlation = df["years_active"].corr(df["comments_count"])
print(f"Correlation between years active and comment count: {correlation:.2f}")

# -----------------------------
# Fourth Plot: 
# Zoom on top 5% most active users (>= 492 comments)
# Distribution of numb of comments per user

percentile_95 = df["comments_count"].quantile(0.95)
df_top5 = df[df["comments_count"] >= percentile_95]

plt.figure(figsize=(10, 6))

sns.histplot(df_top5["years_active"], bins=20, kde=True, color="red")

plt.xlabel("Years Active")
plt.ylabel("Number of Users")
plt.title("Distribution of Years Active (Top 5% Most Active Users)")
plt.grid()
plt.show()

# -----------------------------
# Fifth Plot: 
# Zoom on top 5% most longevity users 

# Compute the 95th percentile threshold for years active
percentile_95_time = df["years_active"].quantile(0.95)

print(f"Users in the top 5% longest active have been active for at least {percentile_95_time:.2f} years.")

df_top5_time = df[df["years_active"] >= percentile_95_time]

plt.figure(figsize=(10, 6))

# Plot histogram for "comment count" among longest active users
sns.histplot(df_top5_time["comments_count"], bins=50, kde=True, log_scale=False, color="green")

plt.xlabel("Number of Comments per User")
plt.ylabel("Number of Users")
plt.title("Distribution of Comment Counts (Top 5% Longest Active Users)")
plt.grid()
plt.show()

# Log plot

df_top5_time = df[df["years_active"] >= percentile_95_time]


plt.figure(figsize=(10, 6))

# Plot histogram for "comment count" among longest active users
sns.histplot(df_top5_time["comments_count"], bins=50, kde=True, log_scale=True, color="green")

plt.xlabel("Number of Comments per User (Log Scale)")
plt.ylabel("Number of Users")
plt.title("Distribution of Comment Counts (Top 5% Longest Active Users)")
plt.grid()
plt.show()


##################################################
# ## Investigate users with a long commenting history 
# import os
# import json
# from collections import defaultdict
# from tqdm import tqdm

# # 1) Build list of top users
# top_users_list = df_top5_time['user_id'].to_list()
# print(f"Number of top users: {len(top_users_list)}")

# # 2) Single query to fetch all top-user comments
# query = {"user_id": {"$in": top_users_list}}
# total_comments = collection.count_documents(query)

# cursor = collection.find(query)

# # 3) Create base output directory
# output_base_dir = "longevity_users_comments_breitbart"
# os.makedirs(output_base_dir, exist_ok=True)

# # 4) Stream the cursor and append to files
# #    (so we don't hold *all* in memory at once)
# #    For each doc, open or append to a file named after the user
# file_handles = {}  # dictionary user_name -> file handle

# for doc in tqdm(cursor, total=total_comments, desc="Collecting comments"):
#     user_id = doc["user_id"]
#     if user_id not in file_handles:
#         # Open a file in append mode (or 'w' if you want to start fresh)
#         # make sure user_id is sanitized if needed
#         file_path = os.path.join(output_base_dir, f"{user_id}.jsonl")
#         file_handles[user_id] = open(file_path, "a", encoding="utf-8")
    
#     # Write doc as a JSON line
#     file_handles[user_id].write(json.dumps(doc, default=str) + "\n")

# # 5) Close all file handles
# for fh in file_handles.values():
#     fh.close()



# Use the fact I have already query them with the names 

import os 
import json
import shutil
from collections import defaultdict
from tqdm import tqdm

top_users = df_top5_time['user_id'].to_list()
print(f"Number of top users: {len(top_users)}")
top_users_list = df_top5_time['user_id'].to_list()

# convert ids list to name list
users_collection = client["Users"]["Breitbart"]
# Query to fetch user names based on user_ids
top_acitve_users_names_pipeline = [
    {"$match": {"_id": {"$in": top_users_list}}},
    {"$project": {"_id": 1, "first_name": {"$arrayElemAt": ["$user_names", 0]}}}
]
# Fetch the user names with the specified query and projection
top_acitve_users_names_cursor = users_collection.aggregate(top_acitve_users_names_pipeline)

# Convert the cursor to a list and then to a DataFrame
top_acitve_users_names = list(top_acitve_users_names_cursor)
top_acitve_users_names_df = pd.DataFrame(top_acitve_users_names)
top_acitve_users_names_df


# check which of this names I do not have data already saved. 
top_acitve_users_directory = "/Users/barolo/Desktop/PhD/Code/Comments_Project/longevity_users_comments_breitbart"
# Get the list of user IDs from the DataFrame
df_user_names = set(top_acitve_users_names_df["first_name"].tolist())

# Get the list of user IDs from the filenames in the directory
folder_user_names = set()
for filename in os.listdir(top_acitve_users_directory):
    if filename.endswith(".jsonl.gz"):
        user_id = filename.replace(".jsonl.gz", "")
        folder_user_names.add(user_id)

# Find users in the DataFrame but not in the folder
users_in_df_not_in_folder = df_user_names - folder_user_names
print(f"Users in DataFrame but not in folder: {len(users_in_df_not_in_folder)}")
print(users_in_df_not_in_folder)

# Find users in the folder but not in the DataFrame
users_in_folder_not_in_df = folder_user_names - df_user_names
print(f"Users in folder but not in DataFrame: {len(users_in_folder_not_in_df)}")
print(users_in_folder_not_in_df)

#___________________________________________________
# replace 
client = pymongo.MongoClient("mongodb://localhost:27017/")
comments_collection = client["Comments"]["Breitbart"]

# Source and new directories
source_dir = "/Users/barolo/Desktop/PhD/Code/Comments_Project/longevity_users_comments_breitbart"
new_dir = "/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/longevity_users_comments_breitbart"

# Create the new directory if it doesn't exist
os.makedirs(new_dir, exist_ok=True)

# Copy all existing files from the source directory to the new directory
for filename in os.listdir(source_dir):
    if filename.endswith(".jsonl.gz"):
        shutil.copy(os.path.join(source_dir, filename), new_dir)

# Get the list of user IDs from the DataFrame
df_user_names = set(top_acitve_users_names_df["first_name"].tolist())

# Get the list of user IDs from the filenames in the new directory
new_dir_user_ids = set()
for filename in os.listdir(new_dir):
    if filename.endswith(".jsonl.gz"):
        user_id = filename.replace(".jsonl.gz", "")
        new_dir_user_ids.add(user_id)

# Find users in the DataFrame but not in the new directory
users_in_df_not_in_new_dir = df_user_names - new_dir_user_ids
print(f"Users in DataFrame but not in new directory: {len(users_in_df_not_in_new_dir)}")
print(users_in_df_not_in_new_dir)

# Query the database and save the missing users
missing_users_query = {"user_id": {"$in": list(users_in_df_not_in_new_dir)}}
missing_users_total_comments = comments_collection.count_documents(missing_users_query)

# Fetch the comments with the specified query and projection
missing_users_cursor = comments_collection.find(missing_users_query)

# Stream the cursor and append to files
file_handles = {}  # dictionary user_id -> file handle

for doc in tqdm(missing_users_cursor, total=missing_users_total_comments, desc="Collecting comments"):
    user_id = doc["user_id"]
    if user_id not in file_handles:
        # Open a file in append mode (or 'w' if you want to start fresh)
        file_path = os.path.join(new_dir, f"{user_id}.jsonl.gz")
        file_handles[user_id] = open(file_path, "a", encoding="utf-8")
    
    # Write doc as a JSON line
    file_handles[user_id].write(json.dumps(doc, default=str) + "\n")

# Close all file handles
for fh in file_handles.values():
    fh.close()

### Sanity check: Do I have the people I wanted in the folder?

# check wheter in folder_user_names there are all and only df_user_names

top_acitve_users_directory = "/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/longevity_users_comments_breitbart"

# Get the list of user IDs from the filenames in the directory
new_folder_user_names = set()
for filename in os.listdir(top_acitve_users_directory):
    if filename.endswith(".jsonl.gz"):
        user_id = filename.replace(".jsonl.gz", "")
        new_folder_user_names.add(user_id)


# # check wheter in folder_user_names there are all and only df_user_names

# len(set(new_folder_user_names) - set(df_user_names))

# # remove from the folder the files within this set:
# # Define the set of files to be removed
# files_to_remove = set(new_folder_user_names) - set(df_user_names)
# # Remove the files from the folder
# for user_id in files_to_remove:
#     file_path = os.path.join(top_acitve_users_directory, f"{user_id}.jsonl.gz")
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print(f"Removed file: {file_path}")


##################################################
# -----------------------------
## Select Best Users (in terms of consistency of comment behaviour)
import pandas as pd
import os
import gzip
import json
from pathlib import Path
import sys
import os
# Add the directory containing utils.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_comments_from_jsonl_gz, plot_top_users_activity


# Define your date format according to your data.
# For example, if dates look like "2022-07-18T12:34:56", use:
date_format = "%Y-%m-%dT%H:%M:%S"

# Base directory containing user comment files
top_acitve_users_directory = "/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/longevity_users_comments_breitbart"

def load_comments_from_jsonl_gz(user_name, base_dir):
    """
    Load all comments for a specific user from a compressed JSONL file (.jsonl.gz).
    
    Parameters:
    - user_name: The name of the user.
    - base_dir: The base directory where the JSONL files are stored.
    """
    base_dir = Path(base_dir)
    user_name_gz =  user_name if ".jsonl.gz" in user_name else f"{user_name}.jsonl.gz"
    user_path = base_dir / user_name_gz
    if not user_path.exists():
        raise FileNotFoundError(f"File not found: {user_path}\nCheck the file name and directory!")

    comments_list = []

    # Open the compressed file with gzip
    with gzip.open(user_path, "rt", encoding="utf-8") as file:
        for line in file:
            comment = json.loads(line)
            comments_list.append(comment)

    comments_df = pd.DataFrame(comments_list)
    # Ensure 'createdAt' exists and is in datetime format
    if "createdAt" in comments_df.columns:
        comments_df["createdAt"] = pd.to_datetime(comments_df["createdAt"], errors="coerce")

    return comments_df


# Example usage
user_name = "zzzzzap"
comments_df = load_comments_from_jsonl_gz(user_name, top_acitve_users_directory)
print(comments_df)


# Option: Specify a subsample size for testing.
# Set subsample_size to None to process all user files.
subsample_size = None 
all_user_files = os.listdir(top_acitve_users_directory)
user_files = all_user_files[:subsample_size] if subsample_size is not None else all_user_files

# Dictionary to store Coefficient of Variation (CV) results
cv_results = {}

# Iterate over all selected user files with a progress bar
for user_filename in tqdm(user_files, desc="Processing user files"):
    # Load the user's comments into a DataFrame
    user_comments_df = load_comments_from_jsonl_gz(user_filename, base_dir=top_acitve_users_directory)
    
    # Convert 'createdAt' to datetime using the specified format to avoid warnings.
    # Using errors='coerce' to handle any unparsable values.
    user_comments_df['createdAt'] = pd.to_datetime(user_comments_df['createdAt'],
                                                     format=date_format,
                                                     errors='coerce')
    # Optionally, drop rows where 'createdAt' could not be parsed
    user_comments_df = user_comments_df.dropna(subset=['createdAt'])
    
    # Aggregate comment count per month
    user_comments_df['year_month'] = user_comments_df['createdAt'].dt.to_period('M')
    comment_counts_series = user_comments_df.groupby('year_month').size()

    # Calculate Coefficient of Variation (CV)
    if len(comment_counts_series) > 1:  # Only compute if there are multiple months
        mean_comments = comment_counts_series.mean()
        std_dev_comments = comment_counts_series.std()
        cv_value = std_dev_comments / mean_comments if mean_comments != 0 else None
        cv_results[user_filename] = {"mean": mean_comments, "std": std_dev_comments, "cv": cv_value}

# Convert results to a DataFrame for sorting and visualization
cv_dataframe = pd.DataFrame.from_dict(cv_results, orient='index')
cv_dataframe = cv_dataframe.sort_values(by="cv", ascending=True)  # Sort from stable to unstable based on CV

# Save the results to a CSV file
cv_dataframe.to_csv("cv_results_longevity_users.csv", index=True)

# Display the DataFrame
cv_dataframe


# -----------------------------
## 

