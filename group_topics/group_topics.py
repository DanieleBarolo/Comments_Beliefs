import numpy as np 
import pandas as pd 
import json 
import os 
import re 

# setup 
path = '../Batch_calling/data/results/'
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
clean_data = []
for ele in data: 
    clean_line = process_jsonl(ele) 
    clean_data.append(clean_line)   

# get all of the targets 
topics = []
for num, comment in enumerate(clean_data): 
    comment = comment['results']
    for topic in comment: 
        print(topic)
        target = topic['target']
        stance = topic['stance']
        topics.append([num, target, stance])
        
data = pd.DataFrame(topics, columns=['post_idx', 'target', 'stance'])
data.to_csv('targets.csv', index=False)

target_list = data['target'].tolist()

### create a prompt for this ### 
def topic_prompt(): 
    '''
    
    
    '''

### do it the other way (i.e., from topic model) ### 