import numpy as np 
import pandas as pd 
import os 
import json 
import pandas as pd 

# 
path = '../LLM_extraction/pilot_llm_results/llama-3.3-70b-versatile/2025-03-24'
files = os.listdir(path)

df_list = []
for file in files: 
    
    with open(os.path.join(path, file), "r") as f: 
        dct = json.load(f)

    dataframe = pd.DataFrame(dct['results'])
    dataframe['comment_date'] = dct['comment_date']
    dataframe['comment_id'] = dct['comment_ids']
    dataframe['user_name'] = dct['user_name']

    df_list.append(dataframe)

dct.keys()

df = pd.concat(df_list)
df_pos = df[df['stance'] != 'NOT RELATED']
df_pos = df_pos.sort_values('comment_date')