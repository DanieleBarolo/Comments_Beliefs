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

from pymongo import MongoClient
from utils import get_article_text

def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

collection_name = "Motherjones" # or "Motherjones", "Thehill"
comment_id = "1866230156"


# initialize collections
comment_collection = init_mongo(dbs = "Comments", collection = collection_name)
comment = comment_collection.find_one({'_id': comment_id})
article_id = comment.get('art_id')
# same logic for parent comment
parent_comment_id = comment.get('parent')
parent_comment_obj = comment_collection.find_one({'_id': str(parent_comment_id)}) if parent_comment_id else None
oldest_comment_obj = comment_collection.find_one(
    {'art_id': article_id},
    sort=[('createdAt', 1)] # is it really 1 here and not 0?
)
liked_comment_obj = comment_collection.find_one(
    {'art_id': article_id},
    sort=[('likes', -1)]
)

# context around comments 
comment_text = comment.get('raw_message')
parent_comment_text = parent_comment_obj.get('raw_message') 
oldest_comment_text = oldest_comment_obj.get('raw_message') 
liked_comment_text = liked_comment_obj.get('raw_message') 



# # comment info 
# target_comment_text = comment.get('raw_message') if target_comment else ''
# target_comment_id = comment.get('_id')
# comment_date = comment.get('createdAt')
