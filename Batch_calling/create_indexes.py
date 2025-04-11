from pymongo import MongoClient

def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

def create_indexes_for_collection(collection_name: str):
    """
    Creates all necessary indexes for a given collection.
    
    Args:
        collection_name (str): Name of the collection to create indexes for
    """
    collection = init_mongo(dbs="Comments", collection=collection_name)
    
    # Create single field indexes
    collection.create_index("art_id")
    collection.create_index("user_id")
    collection.create_index("likes")
    collection.create_index("createdAt", -1)
    
    # Create compound indexes
    collection.create_index([("art_id", 1), ("createdAt", 1)])
    collection.create_index([("art_id", 1), ("likes", -1)])
    
    print(f"Successfully created indexes for collection: {collection_name}")

# Example usage:
# create_indexes_for_collection("Motherjones")


motherjones = init_mongo(dbs = "Comments", collection = "Motherjones")
user_id = "27844421"
comments = motherjones.find({"user_id": user_id})
# transform to list
comments = list(comments)

print(len(comments))



# given one comment_id, find to which colelction it belongs and give ther right flag

comment_id = "1296188855"
assumed_flag = 1

comment_id = "1766699258"
assumed_flag = 0

comment_id = "1767767286"
assumed_flag = 0

comment_id = "5945168033"
assumed_flag = 4

comment_id = "1766728393"
assumed_flag = 0

comment_id = "636702611"
assumed_flag = 2

collection_lists = ["Atlantic", "Breitbart", "Gatewaypundit", "Motherjones", "Thehill"]


COLLECTION_DICT = {
    "Atlantic": "0",
    "Breitbart": "1",
    "Gatewaypundit": "2",
    "Motherjones": "3",
    "Thehill": "4"
}

for collection_name in collection_lists:
    collection = init_mongo(dbs = "Comments", collection = collection_name)
    comment = collection.find_one({"_id": comment_id})
    if comment:
        print(f"Comment found in {collection} collection")
        print(f"Flag: {COLLECTION_DICT[collection_name]}")
        


CORRECTED_DICT = {
    "Gatewaypundit": "0",
    "Breitbart": "1",
    "Thehill": "2",
    "Atlantic": "3",
    "Motherjones": "4",
}