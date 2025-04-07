from pymongo import MongoClient

collection = 'Breitbart'
client = MongoClient("mongodb://localhost:27017/")
comment_db = client["Comments"]
comment_collection = comment_db[collection]
comment_collection.index
comment_id = "1452368501"
comment = comment_collection.find_one({"_id": comment_id})
comment
art_id = str(int(comment['art_id']))
art_id
article_filter = {'art_id': art_id}

# ## Create compound indexes
# comment_collection.create_index([('art_id', 1), ('createdAt', 1)]) 
# comment_collection.create_index([('art_id', 1), ('likes', -1)])

oldest_comment = comment_collection.find_one(
        {'art_id': art_id},
        sort=[('createdAt', 1)]
    )
oldest_comment

most_liked_comment = comment_collection.find_one(
    {'art_id': art_id},
    sort=[('likes', -1)]
)
