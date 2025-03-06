import pymongo
import time
from pprint import pprint

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Comments"]
collection = db["Breitbart"]

# Peek at one document
doc = collection.find_one()
pprint(doc)

# # Add indexes to speed up queries

# '''Indexes in MongoDB are like shortcuts for searching data. 
# Without indexes, MongoDB has to scan every single document to find the relevant ones.
# This is slow when dealing with 400M+ comments.
# '''

for index in collection.list_indexes():
    print(index)

# add if condition before creating the index

# collection.create_indexes([
#     pymongo.IndexModel("user_id"),
#     pymongo.IndexModel("article_id")
# ])


# # Check document with missing user_id
# docs = collection.find({"user_id": None}).limit(10)
# for doc in docs:
#     print('-'*50)
#     pprint(doc)


## Create the Users Database

# Source Database (where comments are stored)
source_db = client["Comments"]
source_collection = source_db["Breitbart"]  # Working only on Breitbart for now

# Target Database (where users' aggregated data will be stored)
target_db = client["Users"]
target_collection = target_db["Breitbart"]  # This should match the source collection


pipeline = [
    # 1️ Projection: Select only needed fields
    {
        "$project": {
            "user_id": 1,
            "user_name": 1,
            "user_about": 1,
            "user_avatar": 1,
            "user_disable3rdPartyTrackers": 1,
            "user_isAnonymous": 1,
            "user_isPowerContributor": 1,
            "user_isPrimary": 1,
            "user_isPrivate": 1,
            "user_joinedAt": 1,
            "user_location": 1,
            "user_profileURL": 1,
            "likes": 1,
            "article_id": 1,
            "comment_id": 1,
            "createdAt": 1,
            "parent": 1  # Keeping this if useful for context
        }
    },

    # 2️ Group by user_id
    {
        "$group": {
            "_id": {
                "$switch": {
                    "branches": [
                        {"case": {"$and": [{"$eq": ["$user_id", None]}, {"$eq": ["$user_isAnonymous", True]}]}, "then": "anonymous_user"},
                        {"case": {"$and": [{"$eq": ["$user_id", None]}, {"$eq": ["$user_isAnonymous", False]}]}, "then": "unknown_user"}  # Changed from "deleted_user"
                    ],
                    "default": "$user_id"  # Keep normal user IDs as-is
                }
            },
        "user_names": {"$addToSet": "$user_name"},  # Users can change names, so we store all
        "user_about": {"$first": "$user_about"},
        "user_disable3rdPartyTrackers": {"$first": "$user_disable3rdPartyTrackers"},
        "user_isAnonymous": {"$first": "$user_isAnonymous"},
        "user_isPowerContributor": {"$first": "$user_isPowerContributor"},
        "user_isPrimary": {"$first": "$user_isPrimary"},
        "user_isPrivate": {"$first": "$user_isPrivate"},
        "user_joinedAt": {"$first": "$user_joinedAt"},
        "user_location": {"$first": "$user_location"},
        "user_profileURL": {"$first": "$user_profileURL"},

        # Aggregated Stats
        "user_names": {"$addToSet": "$user_name"},
        "comments_count": {"$sum": 1},
        "likes_count": {"$sum": "$likes"},
        "dislikes_count" : {"$sum": "$dislikes"},
        # "article_ids": {"$addToSet": "$art_id"}, too long arrays, keep away for now
        # "comment_ids": {"$addToSet": "$_id"},
        "first_comment": {"$min": "$createdAt"},
        "last_comment": {"$max": "$createdAt"}

}
    },

    # 3 Save results in Users.Breitbart
    {
        "$merge": {
            "into": {"db": "Users", "coll": "Breitbart"},  # Writes to Users.Breitbart
            "on": "_id",  # user_id is the unique key
            "whenMatched": "merge",  # If the user exists, replace their data
            "whenNotMatched": "insert"  # If new user, insert
        }
    }
]

# Run the pipeline
explain_result = source_db.command("aggregate", "Breitbart", pipeline=pipeline, explain=True)
print(explain_result)


start_time = time.time()
result = list(source_collection.aggregate(pipeline, allowDiskUse=True))
end_time = time.time()
print(f"Execution Time: {((end_time - start_time) / 60):.2f} minutes")



# #try new database 

# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["Users"]
# collection = db["Breitbart"]

# # Query one specific document by _id
# doc = collection.find_one({"_id": "65893635"})
# pprint(doc)

# doc = collection.find({"_id":"219959063"})
# pprint(doc)
# for doc in docs:
#     print('-'*50)
    

#####################################################################
# ### Sanity Check

# import pandas as pd
# import pymongo
# from pprint import pprint
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db_users = client["Users"]
# collection_users = db_users["Breitbart"]

# # Peek at one document
# doc = collection_users.find_one()
# pprint(doc)

# # Estimated count of users
# estimated_count_users = collection_users.estimated_document_count()
# print(f"Estimated count of users: {estimated_count_users}")

# # Query to fetch only necessary fields
# query = {}
# projection = {
#     "_id": 1,  # user_id
#     "comments_count": 1,
#     "first_comment": 1,
#     "last_comment": 1,
# }

# # Fetch data
# cursor = collection_users.find(query, projection)

# # Convert to DataFrame
# df = pd.DataFrame(list(cursor))
# df.rename(columns={"_id": "user_id"}, inplace=True)
# df["years_active"] = (df["last_comment"] - df["first_comment"]).dt.total_seconds() / (3600 * 24 * 365)


# # Sum of all comments_count
# total_comments_count = df["comments_count"].sum()
# print(f"Total comments count from Users.Breitbart: {total_comments_count}")

# # Estimated count of comments in Comments.Breitbart
db_comments = client["Comments"]
collection_comments = db_comments["Breitbart"]
estimated_count_comments = collection_comments.estimated_document_count()
print(f"Estimated count of comments in Comments.Breitbart: {estimated_count_comments}")

# # Check if the sums are equal
# if total_comments_count == estimated_count_comments:
#     print("The sum of all comments_count is equal to the estimated number of elements in Comments.Breitbart.")
# else:
#     print("The sum of all comments_count is NOT equal to the estimated number of elements in Comments.Breitbart.")


38585087 / 251375537