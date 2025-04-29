import os
import pandas as pd
from pymongo import MongoClient
import sys

# Try to import the get_article_text function from utils
try:
    from utils import get_article_text
    utils_imported = True
except ImportError:
    print("Warning: Could not import get_article_text from utils. Article bodies will be empty.")
    utils_imported = False

# MongoDB connection
def init_mongo(dbs: str, collection: str):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[dbs]
    collection = db[collection]
    return collection

def create_article_context_files(master_csv_path):
    """Generate article context files based on the master CSV file"""
    # Read the master CSV
    df = pd.read_csv(master_csv_path)
    
    # Keep track of articles we've already processed
    processed_articles = set()
    
    # Process each row in the master CSV
    for index, row in df.iterrows():
        article_id = row['article_id']
        
        # Skip if we've already processed this article
        if article_id in processed_articles:
            continue
        
        # Get the provider_name directly from the CSV
        if 'provider_name' in row:
            provider_name = row['provider_name'].lower()  # Use lowercase for folders
            collection_name = provider_name.capitalize()  # Capitalize first letter for collection
        else:
            # Default if not found
            print(f"Warning: provider_name not found for article {article_id}. Using default.")
            provider_name = "thehill"
            collection_name = "Thehill"
        
        # Only process if the provider is one of the three we're looking for
        if provider_name not in ["motherjones", "thehill", "breitbart"]:
            print(f"Skipping article {article_id} - provider {provider_name} not in target list")
            continue
        
        # Initialize MongoDB connection
        article_collection = init_mongo(dbs="Articles", collection=collection_name)
        
        # Get article data
        article_obj = article_collection.find_one({'_id': str(article_id)})
        if not article_obj:
            print(f"Article {article_id} not found in {collection_name}. Skipping.")
            continue
        
        # Get article info
        article_title = article_obj.get('clean_title', article_obj.get('title', 'No title available'))
        article_url = article_obj.get('link', 'No URL available')
        article_date = article_obj.get('createdAt', 'No date available')
        
        # Try to get article body using the utility function
        article_body = ""
        if utils_imported:
            try:
                article_data = get_article_text(str(article_id), collection_name)
                article_body = article_data.get('body', '')
                if not article_body:
                    print(f"Warning: No article body found for article {article_id} in {collection_name}")
            except Exception as e:
                print(f"Error getting article body for {article_id} in {collection_name}: {str(e)}")
        
        # Format article context
        content = []
        content.append("=" * 70)
        content.append(f"ARTICLE TITLE: {article_title}")
        content.append(f"ARTICLE ID: {article_id}")
        content.append(f"ARTICLE URL: {article_url}")
        content.append(f"ARTICLE DATE: {article_date}")
        content.append("=" * 70)
        content.append("")
        content.append("ARTICLE BODY:")
        content.append("")
        content.append(article_body if article_body else "Article body not available")
        content.append("=" * 70)
        
        # For each annotator, create the article context file
        for annotator_id in range(1, 5):  # 1 through 4
            # Path to article directory
            article_dir = os.path.join("annotation_files", f"annotator_{annotator_id}", provider_name, str(article_id))
            
            # Skip if directory doesn't exist (no comments from this article for this annotator)
            if not os.path.exists(article_dir):
                continue
            
            # Write the article context file
            file_path = os.path.join(article_dir, f"{article_id}_context.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            
            print(f"Created article context file for article {article_id} in {file_path}")
        
        # Mark as processed
        processed_articles.add(article_id)

if __name__ == "__main__":
    # Path to your master CSV file
    master_csv_path = "comment_assignments_master.csv"
    create_article_context_files(master_csv_path)
    print("Article context files generated successfully!")