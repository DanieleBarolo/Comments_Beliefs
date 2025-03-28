import gzip
import json

user = "GGbox" #insert name here
file_name = f"../selected_users_data/selected_users_comments_compressed/{user}.jsonl.gz"


with gzip.open(file_name, 'rt', encoding='utf-8') as file:
    first_line = file.readline()
    data = json.loads(first_line)  # Convert JSON string to dictionary

print(data.get("user_id"))  


# To-Do, rename all the files. 