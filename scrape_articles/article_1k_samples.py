from pymongo import MongoClient
import random
import json


client = MongoClient("mongodb://localhost:27017/")
db = client["Articles"]
collection = db["Breitbart"]

# Sample 10 random articles from each collection
    
sampled_articles = list(collection.aggregate([{ "$sample": { "size": 1000 } }]))

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