import numpy as np 
import pandas as pd 
from itertools import combinations

# open or closed targets
df = pd.read_csv('targets_closed.csv')

# just take a first look
df['direction'] = df["stance"].map({"FAVOR": 1, "AGAINST": -1})
df.groupby('target')['direction'].sum().sort_values()

def get_connections(df, idx):

    pairs = list(combinations(df.index, 2))

    # Create edges list
    edges = []

    for idx1, idx2 in pairs:
        target1, stance1 = df.loc[idx1, ['target', 'stance']]
        target2, stance2 = df.loc[idx2, ['target', 'stance']]

        connection = 1 if stance1 == stance2 else -1

        edges.append({
            'source': target1,
            'target': target2,
            'connection': connection,
            'idx': idx
        })

    return edges

unique_idx = df['post_idx'].unique().tolist()
super_edges = []
for idx in unique_idx: 
    df_sub = df[df['post_idx']==idx]
    edges_sub = get_connections(df_sub, idx)
    super_edges.extend(edges_sub)

df = pd.DataFrame(super_edges)

# let us absolutely plot this # 
df.head(10)
