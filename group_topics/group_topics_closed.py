import pandas as pd 
import json 
import os 
import re 

# setup 
path = '../Batch_calling/data/results/31499533/deepseek-r1-distill-llama-70b/closed_target/'
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
        clean_data.append(clean_line)   
    except JSONDecodeError: 
        pass 

# get all of the targets 
topics = []
for num, comment in enumerate(clean_data): 
    comment = comment['results']
    for topic in comment: 
        print(topic)
        target = topic['target']
        stance = topic['stance']
        explanation = topic['explanation']
        topics.append([num, target, stance, explanation])

data = pd.DataFrame(topics, columns=['post_idx', 'target', 'stance', 'explanation'])
data = data[data['stance'].isin(['FAVOR', 'AGAINST'])]
data.to_csv('targets_closed.csv', index=False)

# things to add: 
# 1. the original comment. 
# 2. whether there was a body + whether there was a comment above.
# 3. do manual evaluation ourselves.
# 4. make plot that is interactive (maybe). 