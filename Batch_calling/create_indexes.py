from pymongo import MongoClient, ASCENDING, DESCENDING

def init_mongo(dbs: str, collection: str): 
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

def create_indexes_for_collection(collection_name: str, present_indexes: list):
    """
    Creates all necessary indexes for a given collection.
    
    Args:
        collection_name (str): Name of the collection to create indexes for
        present_indexes (list): List of present indexes for the collection
    """
    collection = init_mongo(dbs="Comments", collection=collection_name)

    # print which indexes are going to be generated 
    needed_index = ['art_id_1', 'user_id_1', 'likes_1', 'createdAt_-1', 'art_id_1_createdAt_1', 'art_id_1_likes_-1']
    index_to_create = [index for index in needed_index if index not in present_indexes]
    print(f"Indexes going to be generated for collection {collection_name}: {index_to_create}")

    # Create single field indexes
    if 'art_id_1' not in present_indexes:
        collection.create_index([("art_id", ASCENDING)])
    if 'user_id_1' not in present_indexes:
        collection.create_index([("user_id", ASCENDING)])
    if 'likes_1' not in present_indexes:
        collection.create_index([("likes", ASCENDING)])
    if 'createdAt_-1' not in present_indexes:
        collection.create_index([("createdAt", DESCENDING)])
    
    # Create compound indexes
    if 'art_id_1_createdAt_1' not in present_indexes:
        collection.create_index([("art_id", ASCENDING), ("createdAt", ASCENDING)])
    if 'art_id_1_likes_-1' not in present_indexes:
        collection.create_index([("art_id", ASCENDING), ("likes", DESCENDING)])
    
    print(f"Successfully created indexes for collection: {collection_name}")

# Example usage:
# create_indexes_for_collection("Motherjones")

collection_lists = ["Atlantic", "Breitbart", "Gatewaypundit", "Motherjones", "Thehill"]
for collection_name in collection_lists:
    print(f"Creating indexes for collection: {collection_name}")
    collection = init_mongo(dbs = "Comments", collection = collection_name)
    indexes = collection.list_indexes()
    present_indexes = [index['name'] for index in indexes]
    print(f"Indexes present for collection {collection_name}: {present_indexes}")
    create_indexes_for_collection(collection_name, present_indexes)

# # sanity check 
# motherjones = init_mongo(dbs = "Comments", collection = "Motherjones")
# user_id = "27844421"
# comments = motherjones.find({"user_id": user_id})
# # transform to list
# comments = list(comments)

# print(len(comments))
