import numpy as np 
import pandas as pd 
import json 
import re

# load network 
suffix = 'new'
user_id = '31499533'
filepath = f'../Batch_calling/data/batch_files/{user_id}/deepseek-r1-distill-llama-70b/closed_target_{suffix}/batch_size_100_with_body_with_parent.jsonl'

def process_jsonl(json_line): 
    text = json_line['body']['messages'][1]['content']
    match = re.search(r'COMMENT UNDER ANALYSIS(.*?)END COMMENT', text, re.DOTALL)
    clean = match.group(1).strip()
    return text, clean 

# load data
data = []
with open(filepath, 'r', encoding='utf-8') as f:
    for line in f:
        line = json.loads(line.strip())
        text, comment = process_jsonl(line)
        idx = line['custom_id']
        data.append([idx, text, comment])

# Create the DataFrame
df = pd.DataFrame({
    'post_idx': [int(x) for x, y, z in data],
    'prompt': [y for x, y, z in data],
    'response': [z for x, y, z in data]
}) 

# this we need to bind with the node data 
filepath = f'data/targets_closed_{user_id}_{suffix}.csv'
df_nodes = pd.read_csv(filepath)

# merge 
df_merge = df.merge(df_nodes, on = 'post_idx', how = 'inner')
pd.set_option('display.max_colwidth', None)

# now we can find guys 

df_merge[df_merge['target']=='Google']
df_merge.dtypes