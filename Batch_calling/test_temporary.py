##############################################################################
import json
import os
import numpy as np
from targets import target_list
from Batch_calling.prompts.prompts_builder import *
from utils import *
from setup import FullStancesCT, FullStancesOT

##############################################################################
# 0. Setup
###############################################################################
collection_name = "Breitbart"

comment_collection = init_mongo(dbs = "Comments", collection = collection_name)

parent_comment = True # Set to False if you want to exclude parent comment in the prompts
all_comments_context = True
if all_comments_context:
    oldest_comment = True # Set to False if you want to exclude oldest comment in the prompts
    most_liked_comment = True # Set to False if you want to exclude most liked comment in the prompts


comment_id = "978198733"
comment = comment_collection.find_one({"_id": comment_id})
article_collection = init_mongo(dbs = "Articles", collection = collection_name)

art_id = comment.get("art_id")
parent_id = comment.get("parent")
parent_comment = comment_collection.find_one({"_id": parent_id})

oldest_comment_full = comment_collection.find_one(
    {'art_id': art_id},
    sort=[('createdAt', 1)]
) 

most_liked_comment_full = comment_collection.find_one(
{'art_id': art_id},
sort=[('likes', -1)]) 

parent_comment_txt  = parent_comment.get("raw_message") if parent_comment else parent_comment
oldest_comment_txt = oldest_comment_full.get("raw_message") if oldest_comment else oldest_comment
most_liked_txt = most_liked_comment_full.get("raw_message") if most_liked_comment else most_liked_comment
