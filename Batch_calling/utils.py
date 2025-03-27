from pymongo import MongoClient
import pyarrow.feather as feather
import os

###############################################################################
# MONGODB Utils                                            #
###############################################################################

def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

def get_topic(
        comment_id, 
        full_date, 
        topic_path="/Volumes/Untitled/seungwoong.ha/collmind/transform_global/breitbart/breitbart_new_s3_r19_h225_u20_t10"):
    
    mmyy = full_date.strftime("%m%y")
    
    arrow_name = f"batch-{mmyy}.arrow"
    topic_table = feather.read_table(os.path.join(topic_path, arrow_name))
    topic_df = topic_table.to_pandas()
    topic_int = topic_df[topic_df['id'] == comment_id]['topic'].iloc[0]
    
    return int(topic_int) 


###############################################################################
# Scrape and Store articles bodies                                            #
###############################################################################

import requests
from bs4 import BeautifulSoup
import time 
import json
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
    title = ""
    body = ""
    link = ""

    # For the moment I set this directory to keep on updating the folder with already present articles
    base_dir = "../LLM_extraction/" # If error, change with the correct directory!

    cache_dir = os.path.join(base_dir, "scrape_articles", "article_body", collection_name) 
    cache_file = f"{cache_dir}/{article_id}.json"
    cached = False 
    # Check if cached version exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            article_json = json.load(f)
            if article_json['title']: 
                return article_json
            else: 
                cached = True 
            
    collection = init_mongo(dbs="Articles", collection=collection_name) 

    # Fetch article data
    article_data = collection.find_one({"_id": article_id})
    title = article_data['clean_title']
    link = article_data.get('link', '')

    if not article_data:
        return {"title": title, "body": body, "link": link}
    
    # Scrape article content
    if cached == False: 
        title, body = retrieve_body(link)
    
    # Prepare results
    result = {
        "title": title,
        "body": body,
        "link": link
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


