import numpy as np 
import pandas as pd 
import json 
import re

# load network 
user_id = '31499533'
filepath = f'../Batch_calling/data/batch_files/{user_id}/deepseek-r1-distill-llama-70b/closed_target/batch_size_100_with_body_with_parent.jsonl'

def process_jsonl(json_line): 
    text = json_line['body']['messages'][1]['content']
    match = re.search(r'COMMENT UNDER ANALYSIS(.*?)END COMMENT', text, re.DOTALL)
    clean = match.group(1).strip()
    return clean 

# load data
data = []
with open(filepath, 'r', encoding='utf-8') as f:
    for line in f:
        line = json.loads(line.strip())
        clean_line = process_jsonl(line)
        data.append(clean_line)

# Create the DataFrame
df = pd.DataFrame({
    'post_idx': range(len(data)),
    'Comment': data
})

# this we need to bind with the node data 
filepath = f'data/targets_closed_{user_id}.csv'
df_nodes = pd.read_csv(filepath)

# merge 
df_merge = df.merge(df_nodes, on = 'post_idx', how = 'inner')
pd.set_option('display.max_colwidth', None)

df_merge.head(5)

''' problems: 

'''