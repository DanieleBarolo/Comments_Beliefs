from pymongo import MongoClient
import random
import json
import pandas as pd
import numpy as np


client = MongoClient("mongodb://localhost:27017/")
db = client["Articles"]
collection = db["Breitbart"]

# Sample 10 random articles from each collection
    
sampled_articles = list(collection.aggregate([{ "$sample": { "size": 1000 } }]))



#to dataframe
sampled_articles_df = pd.DataFrame(sampled_articles)
sampled_articles_df.columns
sampled_articles_df[sampled_articles_df['isClosed'].isna()]


# Print and save results
with open("sampled_1k_articles.jsonl", "w") as file:
    result = f"Collection: {collection.name} - Sampled {len(sampled_articles)} articles\n"
    print(result)
    for article in sampled_articles:
        # Extract only the '_id' and 'link' fields
        filtered_article = {"_id": article["_id"], "link": article["link"]}
        # Write the filtered article as a JSON line
        file.write(json.dumps(filtered_article) + "\n")
    separator = "\n" + "-"*50 + "\n"
    print(separator)

#query mongo db with all ids in missing_articles['ids']

# Load missing articles
missing_articles = pd.read_csv("/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/scrape_articles/article_body/breitbart_missing.csv")

# Query MongoDB with all IDs in missing_articles['ids']
missing_article_ids = missing_articles['_id'].tolist()
missing_articles_query = {"_id": {"$in": missing_article_ids}}
missing_articles_cursor = collection.find(missing_articles_query)

# Convert the cursor to a DataFrame
missing_articles_df = pd.DataFrame(list(missing_articles_cursor))

# Display the missing articles DataFrame
missing_articles_df





