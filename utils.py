import pandas as pd
import os
import gzip
import json
from pathlib import Path
import matplotlib.pyplot as plt

# Function to load comments for a specific user from compressed JSONL (.jsonl.gz)
def load_comments_from_jsonl_gz(user_name):
    """
    Load all comments for a specific user from a compressed JSONL file (.jsonl.gz).
    """
    script_dir = Path(__file__).parent
    base_dir = script_dir / "selected_users_data" / "selected_users_comments_compressed"
    user_path = base_dir / f"{user_name}.jsonl.gz"
    if not user_path.exists():
        raise FileNotFoundError(f"File not found: {user_path}\nCheck the file name and directory!")

    comments_list = []

    # Open the compressed file with gzip
    with gzip.open(user_path, "rt", encoding="utf-8") as file:
        for line in file:
            comment = json.loads(line)
            comments_list.append(comment)

    comments_df = pd.DataFrame(comments_list)
    # Ensure 'createdAt' exists and is in datetime format
    if "createdAt" in comments_df.columns:
        comments_df["createdAt"] = pd.to_datetime(comments_df["createdAt"], errors="coerce")

    return comments_df


def plot_top_users_activity(cv_dataframe, num_users=10, min_comments=100):
    """
    Plots the commenting activity over time for the top users based on low Coefficient of Variation 
    and high comment count.
    
    Parameters:
    - cv_dataframe: DataFrame containing 'Coefficient of Variation' and 'count' columns.
    - num_users: Number of top users to plot.
    - min_comments: Minimum comment count threshold.
    """

    # Filter and sort users
    filtered_df = cv_dataframe[cv_dataframe['count'] >= min_comments]
    filtered_df = filtered_df.sort_values(by=['cv', 'count'], ascending=[True, False])

    # Select top users
    top_users = filtered_df.index[:num_users]

    plt.figure(figsize=(12, 6))

    for example_user in top_users:
        user_file = f"longevity_users_comments_breitbart/{example_user}.jsonl"

        # Load comments from JSONL file
        comments = []
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                for line in f:
                    comment = json.loads(line)
                    comments.append(comment)

            # Convert to DataFrame and process dates
            user_df = pd.DataFrame(comments)
            user_df['createdAt'] = pd.to_datetime(user_df['createdAt'])
            user_df['year_month'] = user_df['createdAt'].dt.to_period('M')
            comment_counts = user_df.groupby('year_month').size()

            # Plot the series
            plt.plot(comment_counts.index.to_timestamp(), comment_counts.values, marker="o", label=example_user)

        except FileNotFoundError:
            print(f"Warning: File not found for user {example_user}")

    plt.title(f"Commenting Activity Over Time for Top {num_users} Users")
    plt.xlabel("Time (Year-Month)")
    plt.ylabel("Number of Comments")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend()  # Add legend so each line is labeled
    plt.show()