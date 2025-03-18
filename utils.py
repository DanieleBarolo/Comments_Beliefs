###############################################################################
# Scrape and Store articles bodies                                            #
###############################################################################
import requests
from bs4 import BeautifulSoup
import time 
import os
import json
from urllib.parse import urlparse
from datetime import datetime
import os
import json
from typing import Union, Optional
from pydantic import BaseModel, validator
from pymongo import MongoClient
from pprint import pprint


# ------------------------------ Calling API -----------------------------------

def retrieve_body(url):
    article_title = ''
    article_body = ''
    
    max_retries = 3             # how many times to retry on 429
    default_sleep_time = 30     # how many seconds to wait if no Retry-After is given

    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 200:
            # good to parse
            break
        elif response.status_code == 429:
            # Too Many Requests
            print(f"429 received. Attempt {attempt+1}/{max_retries} - waiting before retrying.")
            # If the server sent a Retry-After header, use it; otherwise wait default_sleep_time.
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    wait_seconds = int(retry_after)
                except ValueError:
                    wait_seconds = default_sleep_time
            else:
                wait_seconds = default_sleep_time
            
            time.sleep(wait_seconds)
        else:
            # Some other HTTP error: we can either break or raise an exception
            print(f"Error fetching {url}: status {response.status_code}")
            return article_title, article_body
    else:
        # If we exit the for-loop normally, it means we never got a 200
        print("Max retries hit, giving up.")
        return article_title, article_body

    # At this point, if we're here, we got a 200 response
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the title:
    title = soup.find("h1")
    if title:
        article_title = title.get_text(strip=True)

    # Extract the article body:
    body_div = soup.find("div", class_="entry-content")
    if body_div:
        article_body = body_div.get_text(strip=True)
    
    return article_title, article_body

# --------------------------------------------- Storing Results -------------------------------------


def get_article_text(article_id: str, collection_name: str) -> dict:
    """
    Retrieve article text either from cache or by scraping the content.
    
    Args:
        article_id: The unique identifier for the article
        collection_name: Name of the collection (Atlantic, Breitbart, etc.)
    
    Returns:
        dict: Contains 'text' and 'link' of the article
    """
    # Define cache path
    cache_dir = f"./scrape_articles/article_body/{collection_name}"
    cache_file = f"{cache_dir}/{article_id}.json"
    
    # Check if cached version exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not cached, fetch from MongoDB

    BASE_DIR = "./scrape_articles/article_body"
    client = MongoClient("mongodb://localhost:27017/")
    art_db = client["Articles"]
    collection = art_db[collection_name]
    
    # Fetch article data
    article_data = collection.find_one({"_id": article_id})
    if not article_data:
        return {"text": "", "link": ""}
    
    # Extract link from MongoDB
    article_link = article_data.get('link', '')
    
    # Scrape article content
    article_title, article_text = retrieve_body(article_link)
    
    # Prepare results
    result = {
        "title": article_title,
        "body": article_text,
        "link": article_link
    }
    
    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)
    
    # Save to cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
    
    return result


###############################################################################
# Comment threads                                                             #
###############################################################################

def trace_comment_thread(comment_id, collection = 'Breitbart', verbose=False, retrieve_article=False):
    # MongoDB setup
    client = MongoClient("mongodb://localhost:27017/")
    comment_db = client["Comments"]
    comment_collection = comment_db[collection]
    
    art_db = client["Articles"]
    art_collection = art_db[collection]
    
    # Initialize thread tracking lists
    comments_thread_txt = []
    comments_thread_ids = []
    article = None
    article_title = ''
    article_link = ''
    article_body = ''
    
    current_comment_id = comment_id

    while current_comment_id is not None:
        comment = comment_collection.find_one({"_id": current_comment_id})
        if not comment:
            if verbose:
                print(f"Comment with ID {current_comment_id} not found.")
            break

        # Add current comment to the thread
        comments_thread_txt.insert(0, comment.get('raw_message', ''))
        comments_thread_ids.insert(0, current_comment_id)

        # Fetch the article only once
        if article is None and comment.get('art_id'):
            art_id = str(int(comment['art_id']))
            article = get_article_text(art_id, collection)
            
            if article:
                article_title = article.get('title')
                article_link = article.get('link')
                article_body = article.get('body')

            elif verbose:
                print(f"Article with ID {art_id} not found.")

        # if verbose:
        #     print("-" * 50)
        #     print(f"Comment ID: {current_comment_id}")
        #     pprint(comment)

        # Move to the parent comment
        current_comment_id = str(int(comment['parent'])) if comment.get('parent') else None

    # Verbose Output
    if verbose:
        print("#" * 75)
        print("Article Title:")
        pprint(article_title or "No title found")
        print("Article Link:")
        pprint(article_link or "No link found")
        if retrieve_article:
            print("Article Body:")
            pprint(article_body or "No body content found")
        print("#" * 75)

        for idx, txt in enumerate(comments_thread_txt):
            if idx == len(comments_thread_txt) - 1:
                print(">>> TARGET COMMENT <<<")
                pprint(txt)
                print(">>> END TARGET <<<")
            else:
                pprint(txt)
            print("-" * 50)

    return {
        "article_title": article_title,
        "article_link": article_link,
        "article_body": article_body if retrieve_article else None,
        "comment_ids": comments_thread_ids,
        "comment_texts": comments_thread_txt
    }



###############################################################################
# Import and plot data (to ignore for now)                                    #
###############################################################################

# import matplotlib.pyplot as plt
import gzip          
import json          
import pandas as pd  
from pathlib import Path  

def load_comments_from_jsonl_gz(user_name, base_dir):
    """
    Load all comments for a specific user from a compressed JSONL file (.jsonl.gz).
    
    Parameters:
    - user_name: The name of the user.
    - base_dir: The base directory where the JSONL files are stored.
    """
    base_dir = Path(base_dir)
    user_path = base_dir / f"{user_name}.jsonl.gz"
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


# def plot_top_users_activity(cv_dataframe, num_users=10, min_comments=100):
#     """
#     Plots the commenting activity over time for the top users based on low Coefficient of Variation 
#     and high comment count.
    
#     Parameters:
#     - cv_dataframe: DataFrame containing 'Coefficient of Variation' and 'count' columns.
#     - num_users: Number of top users to plot.
#     - min_comments: Minimum comment count threshold.
#     """

#     # Filter and sort users
#     filtered_df = cv_dataframe[cv_dataframe['count'] >= min_comments]
#     filtered_df = filtered_df.sort_values(by=['cv', 'count'], ascending=[True, False])

#     # Select top users
#     top_users = filtered_df.index[:num_users]

#     plt.figure(figsize=(12, 6))

#     for example_user in top_users:
#         user_file = f"longevity_users_comments_breitbart/{example_user}.jsonl"

#         # Load comments from JSONL file
#         comments = []
#         try:
#             with open(user_file, "r", encoding="utf-8") as f:
#                 for line in f:
#                     comment = json.loads(line)
#                     comments.append(comment)

#             # Convert to DataFrame and process dates
#             user_df = pd.DataFrame(comments)
#             user_df['createdAt'] = pd.to_datetime(user_df['createdAt'])
#             user_df['year_month'] = user_df['createdAt'].dt.to_period('M')
#             comment_counts = user_df.groupby('year_month').size()

#             # Plot the series
#             plt.plot(comment_counts.index.to_timestamp(), comment_counts.values, marker="o", label=example_user)

#         except FileNotFoundError:
#             print(f"Warning: File not found for user {example_user}")

#     plt.title(f"Commenting Activity Over Time for Top {num_users} Users")
#     plt.xlabel("Time (Year-Month)")
#     plt.ylabel("Number of Comments")
#     plt.xticks(rotation=45)
#     plt.grid()
#     plt.legend()  # Add legend so each line is labeled
#     plt.show()


# ###############################################################################
# TOPICS UTILS # 

