from pymongo import MongoClient
import random

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update connection string if needed
db = client["Articles"]  # Database name

# Get all collections in the Articles database
collections = db.list_collection_names()

# Sample 10 random articles from each collection
sampled_articles = {}

for collection_name in collections:

    collection = db[collection_name]
    
    sample = list(collection.aggregate([{ "$sample": { "size": 10 } }]))
        
    sampled_articles[collection_name] = sample

# Print and save results
with open("sampled_articles.txt", "w") as file:
    for collection, articles in sampled_articles.items():
        result = f"Collection: {collection} - Sampled {len(articles)} articles\n"
        print(result)
        file.write(result)
        for article in articles:
            print(article)
            file.write(str(article) + "\n")
        separator = "\n" + "-"*50 + "\n"
        print(separator)
        file.write(separator)
