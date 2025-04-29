import os
import pandas as pd
from pymongo import MongoClient
import shutil

# MongoDB connection
def init_mongo(dbs: str, collection: str):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

def get_comment_thread(comment_collection, comment_id):
    """Retrieve the full parent thread for a comment"""
    thread = []
    current_id = comment_id
    
    while current_id:
        comment = comment_collection.find_one({'_id': str(current_id)})
        if not comment:
            break
            
        thread.append(comment)
        current_id = comment.get('parent')
    
    # Thread is now in reverse order (from target to root)
    # Reverse it to get chronological order (from root to target)
    thread.reverse()
    
    return thread

def format_comment_file(comment_obj, parent_comment_obj, oldest_comment_obj, liked_comment_obj, thread, article_title, article_url):
    """Format the content of the annotation file in a minimal, easy-to-read format with updated order"""
    content = []
    
    # Article Information
    content.append("=" * 70)
    content.append(f"ARTICLE TITLE: {article_title}")
    content.append(f"ARTICLE ID: {comment_obj.get('art_id')}")
    content.append(f"ARTICLE URL: {article_url}")
    content.append("=" * 70)
    content.append("")
    
    # Target Comment
    content.append(">" * 25 + " TARGET COMMENT " + "<" * 25)
    content.append(f"Date: {comment_obj.get('createdAt', 'Unknown date')}")
    content.append("")
    content.append(comment_obj.get('raw_message', 'No message available'))
    content.append("=" * 70)
    content.append("")
    
    # Context section
    content.append(">" * 25 + " CONTEXT " + "<" * 25)
    
    # 1. Oldest Comment
    content.append("OLDEST COMMENT:")
    content.append(f"Date: {oldest_comment_obj.get('createdAt', 'Unknown date')}")
    content.append("")
    content.append(oldest_comment_obj.get('raw_message', 'No message available'))
    content.append("-" * 70)
    content.append("")
    
    # 2. Most Liked Comment
    content.append("MOST LIKED COMMENT:")
    content.append(f"Likes: {liked_comment_obj.get('likes', 0)}")
    content.append("")
    content.append(liked_comment_obj.get('raw_message', 'No message available'))
    content.append("-" * 70)
    content.append("")
    
    # 3. Parent Comment (if exists)
    content.append("PARENT COMMENT:")
    if parent_comment_obj:
        content.append(parent_comment_obj.get('raw_message', 'No message available'))
    else:
        content.append("TARGET COMMENT IS A PARENT COMMENT (no parent exists)")
    content.append("-" * 70)
    content.append("")
    
    # 4. Full Comment Thread
    content.append("FULL COMMENT THREAD:")
    if thread and len(thread) > 1:  # Only show if there's actually a thread (more than just the target comment)
        for i, comment in enumerate(thread):
            if i > 0:  # Add separator between comments
                content.append("- - - - - - - - - - - - - - - - - - - -")
            indent = "  " * i  # Indent to show nesting level
            content.append(f"{indent}Comment {i+1}:")
            content.append(f"{indent}Date: {comment.get('createdAt', 'Unknown date')}")
            content.append("")
            content.append(f"{indent}{comment.get('raw_message', 'No message available')}")
            content.append("")
    else:
        content.append("No thread available (single comment)")
    
    content.append("=" * 70)
    
    return "\n".join(content)

def create_annotation_files(master_csv_path):
    """Generate annotation files based on the master CSV file with minimal format"""
    # Read the master CSV
    df = pd.read_csv(master_csv_path)
    
    # Create base output directory
    base_dir = "annotation_files"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    # Create directories for each annotator
    for annotator_id in range(1, 5):  # 1 through 4
        annotator_dir = os.path.join(base_dir, f"annotator_{annotator_id}")
        os.makedirs(annotator_dir)
        
        # Create directories for just the three news sources we need
        for news_source in ["motherjones", "thehill", "breitbart"]:
            news_dir = os.path.join(annotator_dir, news_source)
            os.makedirs(news_dir)
    
    # Process each row in the master CSV
    for index, row in df.iterrows():
        article_id = row['article_id']
        comment_id = row['comment_id']
        
        # Get the provider_name directly from the CSV
        if 'provider_name' in row:
            provider_name = row['provider_name'].lower()  # Use lowercase for folders
            collection_name = provider_name.capitalize()  # Capitalize first letter for collection
        else:
            # Default if not found
            print(f"Warning: provider_name not found for comment {comment_id}. Using default.")
            provider_name = "thehill"
            collection_name = "Thehill"
        
        # Only process if the provider is one of the three we're looking for
        if provider_name not in ["motherjones", "thehill", "breitbart"]:
            print(f"Skipping comment {comment_id} - provider {provider_name} not in target list")
            continue
        
        # Get annotator assignments from the CSV
        annotator_1 = row.get('annotator_1', 1)
        annotator_2 = row.get('annotator_2', 2)
        annotator_ids = [annotator_1, annotator_2]
        
        # Initialize MongoDB connections
        comment_collection = init_mongo(dbs="Comments", collection=collection_name)
        article_collection = init_mongo(dbs="Articles", collection=collection_name)
        
        # Retrieve comment
        comment = comment_collection.find_one({'_id': str(comment_id)})
        if not comment:
            print(f"Comment {comment_id} not found in {collection_name}. Skipping.")
            continue
            
        # Get article ID from comment
        art_id = comment.get('art_id')
        
        # Get article title and URL
        article_obj = article_collection.find_one({'_id': str(art_id)})
        if not article_obj:
            article_title = "Article not found"
            article_url = "URL not available"
        else:
            article_title = article_obj.get('clean_title', article_obj.get('title', 'No title available'))
            article_url = article_obj.get('link', article_obj.get('url', 'No URL available'))
        
        # Get parent comment if exists
        parent_comment_id = comment.get('parent')
        parent_comment_obj = comment_collection.find_one({'_id': str(parent_comment_id)}) if parent_comment_id else None
        
        # Get oldest comment
        oldest_comment_obj = comment_collection.find_one(
            {'art_id': art_id},
            sort=[('createdAt', 1)]
        )
        
        # Get most liked comment
        liked_comment_obj = comment_collection.find_one(
            {'art_id': art_id},
            sort=[('likes', -1)]
        )
        
        # Get the full comment thread
        comment_thread = get_comment_thread(comment_collection, comment_id)
        
        # Format the content with minimal information
        content = format_comment_file(
            comment, 
            parent_comment_obj, 
            oldest_comment_obj, 
            liked_comment_obj,
            comment_thread,
            article_title, 
            article_url
        )
        
        # Create article directory and write file for assigned annotators only
        for annotator_id in annotator_ids:
            # Create article directory if it doesn't exist
            article_dir = os.path.join(base_dir, f"annotator_{annotator_id}", provider_name, str(article_id))
            os.makedirs(article_dir, exist_ok=True)
            
            # Write the file
            file_path = os.path.join(article_dir, f"{comment_id}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Processed comment {comment_id} for article {article_id}")

if __name__ == "__main__":
    # Path to your master CSV file
    master_csv_path = "comment_assignments_master.csv"
    create_annotation_files(master_csv_path)
    print("Annotation files generated successfully!")