import pandas as pd 
import json 
import os 
import re 

# setup 
time = '2025-03-31'
user = '31499533'
#model = 'deepseek-r1-distill-llama-70b' 
model = 'llama-3.3-70b-versatile'
path = f'../Batch_calling/data/results/{user}/{model}/closed_target/{time}'
#body = 'with_body' # no_body
body = 'no_body'
file = f'batch_size_100_{body}_with_parent.jsonl'

filepath = os.path.join(path, file)

def process_deepseek(json_line): 
    answer = json_line['response']['body']['choices'][0]['message']['content']
    answer = re.split("</think>", answer)[1]
    answer = re.search(r'```json\n(.*?)\n```', answer, re.DOTALL).group(1)
    answer = json.loads(answer)
    return answer 

def process_llama(json_line): 
    answer = json_line['response']['body']['choices'][0]['message']['content']
    answer = answer.strip('`n').strip()
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
    print(num)
    try: 
        if 'deepseek' in model:
            clean_line = process_deepseek(ele)
        else: 
            clean_line = process_llama(ele)
        idx = ele['custom_id'] 
        clean_data.append((clean_line, idx))   
    except (JSONDecodeError, TypeError, AttributeError, IndexError):
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
        stance_type = topic.get('stance_type', '')
        explanation = topic['explanation']
        topics.append([idx, target, stance, stance_type, explanation])

data = pd.DataFrame(topics, columns=['post_idx', 'target', 'stance', 'stance_type', 'explanation'])
data = data[data['stance'].isin(['FAVOR', 'AGAINST'])]
data.to_csv(f'data/{user}_{body}_{model}_{time}_small.csv', index=False)

# things to add: 
# 1. the original comment. 
# 2. whether there was a body + whether there was a comment above.
# 3. do manual evaluation ourselves.
# 4. make plot that is interactive (maybe). 