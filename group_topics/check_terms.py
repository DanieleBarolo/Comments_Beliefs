import numpy as np 
import pandas as pd 
import json 

# load network 
user_id = '31499533'
df = pd.read_csv(f'data/targets_closed_{user_id}.csv')

# 
path = '/Users/poulsen/Comments_Beliefs/Batch_calling/data/batch_files/31499533/deepseek-r1-distill-llama-70b/closed_target/batch_size_100_with_body_with_parent.jsonl'
with open(path, 'r') as f: 
    data = json.loads(f)
        