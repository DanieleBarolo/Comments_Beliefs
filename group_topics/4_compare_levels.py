import numpy as np 
import pandas as pd 
import os 
import re
from utility import aggregate_nodes
import seaborn as sns 

# actually get distributions first will be interesting
run_id = '20250409_CT_DS70B_002' 
path = os.path.join('data', run_id)
files = os.listdir(path)

nodes_list = []
for f in files: 
    user_id = re.search(r'\d+', f)[0]
    df = pd.read_csv(os.path.join(path, f))
    df_nodes = aggregate_nodes(df)
    df_nodes['user_id'] = user_id
    nodes_list.append(df_nodes)

df_nodes_agg = pd.concat(nodes_list)

# what is the relevant metric here? 
# not quite power-law maybe; but something like that...?
sns.displot(
    data=df_nodes_agg, 
    x="count", 
    hue="user_id", 
    kind="kde")