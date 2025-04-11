import pandas as pd
from pymongo import MongoClient
import os

def get_mongo_connection():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['reddit']  # Replace with your database name
    return db

def fetch_usernames(user_ids):
    db = get_mongo_connection()
    users_collection = db['users']  # Replace with your collection name
    
    results = []
    for user_id in user_ids:
        user = users_collection.find_one({'id': user_id})
        if user:
            results.append({
                'user_id': user_id,
                'user_name': user.get('name', '')
            })
        else:
            results.append({
                'user_id': user_id,
                'user_name': ''
            })
    return results

def main():
    # Read the input CSV file
    input_file = '/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/Batch_calling/data/selected_users/motherjones.csv'
    output_file = '/Users/barolo/Desktop/PhD/Code/Comments_Beliefs/Batch_calling/data/selected_users/motherjones_with_usernames.csv'
    
    # Read user IDs from CSV
    df = pd.read_csv(input_file)
    user_ids = df['user_id'].tolist()
    
    # Fetch usernames from MongoDB
    results = fetch_usernames(user_ids)
    
    # Create DataFrame and save to CSV
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
