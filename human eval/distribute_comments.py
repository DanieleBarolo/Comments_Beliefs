import pandas as pd
import numpy as np

# Function to create distribution assignments
def create_annotation_distribution(data_files, output_file):
    """
    Creates annotation assignments for 4 annotators based on the given data files.
    Each comment will be assigned to exactly 2 annotators.
    
    Parameters:
    data_files (list): List of CSV file paths containing comments data
    output_file (str): Path to save the output assignments
    """
    # Define the provider mapping dictionary according to existing convention
    PROVIDER_DICT = {
        "motherjones": "4",
        "thehill": "2",
        "breitbart": "1"
    }
    
    # Load all data files
    dfs = []
    for file in data_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    # Combine all data
    all_comments = pd.concat(dfs, ignore_index=True)
    
    # Define annotator pairs - these are all possible combinations of 4 annotators
    annotator_pairs = [
        (1, 2), (1, 3), (1, 4),
        (2, 3), (2, 4),
        (3, 4)
    ]
    
    # Assign comments to pairs
    all_comments['annotator_pair'] = np.nan
    
    # Keep track of provider-specific counts
    pair_provider_counts = {pair: {provider: 0 for provider in PROVIDER_DICT.keys()} 
                            for pair in annotator_pairs}
    
    # Create a column to identify the provider
    # Map providers to their numeric IDs according to predefined mapping
    PROVIDER_DICT = {
        "motherjones": "4",
        "thehill": "2",
        "breitbart": "1"
    }
    
    # Track which provider each comment came from based on original files
    all_comments['provider_name'] = ""
    start_idx = 0
    for i, df in enumerate(dfs):
        end_idx = start_idx + len(df)
        provider_name = data_files[i].replace("sampled_comments_", "").replace(".csv", "")
        all_comments.loc[start_idx:end_idx-1, 'provider_name'] = provider_name
        start_idx = end_idx
    
    # Map to numeric provider ID using the predefined dictionary
    all_comments['provider'] = all_comments['provider_name'].apply(
        lambda x: PROVIDER_DICT.get(x, "0")
    )
    
    # For each provider
    for provider_name in PROVIDER_DICT.keys():
        provider_comments = all_comments[all_comments['provider_name'] == provider_name]
        
        # For each article within the provider (assuming 6 articles per provider)
        article_ids = provider_comments['article_id'].unique()
        
        for i, article_id in enumerate(article_ids):
            article_comments = provider_comments[provider_comments['article_id'] == article_id]
            
            # Each article (with 23 comments) gets assigned to one annotator pair
            # This ensures balanced distribution across providers and articles
            pair_index = i % len(annotator_pairs)
            pair = annotator_pairs[pair_index]
            
            # Update the main dataframe
            all_comments.loc[article_comments.index, 'annotator_pair'] = str(pair)
            
            # Update counts
            pair_provider_counts[pair][provider_name] += len(article_comments)
    
    # Create the final assignment dataframe
    assignments = pd.DataFrame({
        'article_id': all_comments['article_id'],
        'comment_id': all_comments['comment_id'],
        'user_id': all_comments['user_id'],
        'provider': all_comments['provider'],
        'provider_name': all_comments['provider_name'],
        'annotator_pair': all_comments['annotator_pair']
    })
    
    # Expand annotator pairs to individual annotator columns
    assignments['annotator_1'] = assignments['annotator_pair'].apply(lambda x: eval(x)[0] if pd.notna(x) else np.nan)
    assignments['annotator_2'] = assignments['annotator_pair'].apply(lambda x: eval(x)[1] if pd.notna(x) else np.nan)
    
    # Create separate files for each annotator
    for annotator in range(1, 5):
        annotator_comments = assignments[
            (assignments['annotator_1'] == annotator) | 
            (assignments['annotator_2'] == annotator)
        ].copy()
        
        annotator_comments.to_csv(f"annotator_{annotator}_assignments.csv", index=False)
    
    # Save the master assignment file
    assignments.to_csv(output_file, index=False)
    
    # Print distribution statistics
    print("\nAssignment Statistics:")
    print("-" * 50)
    print(f"Total comments: {len(all_comments)}")
    
    # Count comments per annotator
    for annotator in range(1, 5):
        count = len(assignments[(assignments['annotator_1'] == annotator) | 
                               (assignments['annotator_2'] == annotator)])
        print(f"Annotator {annotator}: {count} comments")
    
    # Count comments per pair
    for pair in annotator_pairs:
        pair_str = str(pair)
        count = len(assignments[assignments['annotator_pair'] == pair_str])
        print(f"Pair {pair}: {count} comments total")
        
        # Break down by provider
        provider_names = list(PROVIDER_DICT.keys())
        for provider_name in provider_names:
            provider_count = len(assignments[(assignments['annotator_pair'] == pair_str) & 
                                           (assignments['provider_name'] == provider_name)])
            print(f"  - {provider_name} (ID: {PROVIDER_DICT[provider_name]}): {provider_count} comments")
    
    return assignments

# Example usage:
if __name__ == "__main__":
    # Your actual file paths
    data_files = [
        "sampled_comments_motherjones.csv",
        "sampled_comments_thehill.csv",
        "sampled_comments_breitbart.csv"
    ]
    
    assignments = create_annotation_distribution(data_files, "comment_assignments_master.csv")
    
    print("\nAnnotation distribution complete!")
    print("Files created:")
    print("- comment_assignments_master.csv (all assignments)")
    print("- annotator_1_assignments.csv (Annotator 1's assignments)")
    print("- annotator_2_assignments.csv (Annotator 2's assignments)")
    print("- annotator_3_assignments.csv (Annotator 3's assignments)")
    print("- annotator_4_assignments.csv (Annotator 4's assignments)")