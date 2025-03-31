import pandas as pd 
import json 
import os 
import re 

# setup 
user = '31499533'
suffix = 'new'
path = f'../Batch_calling/data/results/{user}/deepseek-r1-distill-llama-70b/closed_target_{suffix}/'
file = 'batch_size_100_with_body_with_parent.jsonl'
filepath = os.path.join(path, file)

def process_jsonl(json_line): 
    answer = json_line['response']['body']['choices'][0]['message']['content']
    answer = re.split("</think>", answer)[1]
    answer = re.search(r'```json\n(.*?)\n```', answer, re.DOTALL).group(1)
    answer = json.loads(answer)
    return answer 

# load data
data = []
with open(filepath, 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line.strip()))

# take out results 
from json import JSONDecodeError
clean_data = []
for num, ele in enumerate(data): 
    try: 
        clean_line = process_jsonl(ele)
        idx = ele['custom_id'] 
        clean_data.append((clean_line, idx))   
    except (JSONDecodeError, TypeError):
        pass 

# get all of the targets 
topics = []
for num, tuple in enumerate(clean_data): 
    comment, idx = tuple 
    comment = comment['results']
    for topic in comment: 
        print(topic)
        target = topic['target']
        stance = topic['stance']
        explanation = topic['explanation']
        topics.append([idx, target, stance, explanation])

data = pd.DataFrame(topics, columns=['post_idx', 'target', 'stance', 'explanation'])
data = data[data['stance'].isin(['FAVOR', 'AGAINST'])]
data.to_csv(f'data/targets_closed_{user}_{suffix}.csv', index=False)

# things to add: 
# 1. the original comment. 
# 2. whether there was a body + whether there was a comment above.
# 3. do manual evaluation ourselves.
# 4. make plot that is interactive (maybe). 