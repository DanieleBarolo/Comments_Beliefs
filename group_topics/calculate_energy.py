import pandas as pd 
import os 
from utility import compute_edges, aggregate_edges, aggregate_nodes
import re 

# open or closed targets
run_id = '20250409_CT_DS70B_002'
path = f'data/{run_id}'
files = os.listdir(path) 
f = files[0]
df = pd.read_csv(os.path.join(path, f))

df_edges = compute_edges(df)
df_edges = aggregate_edges(df_edges)
df_nodes = aggregate_nodes(df)

## okay so calculate stuff ##
def calc_H_pers(df_edges, df_nodes, filter=None): 

    if filter is not None: 
        df_edges = df_edges[(df_edges['source']==filter) | (df_edges['target']==filter)]

    ### do the personal dissonance ###
    H_pers = 0
    for num, row in df_edges.iterrows():
            # extract params 
            source = row['source']
            target = row['target']
            wij = row['average_connection'] * row['connection_count']
            
            # nodes 
            xi = df_nodes[df_nodes['target'] == source]['average_direction'].iloc[0]
            bi = df_nodes[df_nodes['target'] == source]['count'].iloc[0]
            xj = df_nodes[df_nodes['target'] == target]['average_direction'].iloc[0]
            bj = df_nodes[df_nodes['target'] == target]['count'].iloc[0]

            # sum 
            H_pers += wij * xi * bi * xj * bj

    # then it should be negative 
    H_pers = -H_pers

    return H_pers

# has to be negative gives consonance, right? 
df_h_pers = calc_H_pers(df_edges, df_nodes) 

# let us calculate this across all concepts we have # 
all_targets = df_nodes['target'].unique().tolist()
h_flip_list = []
for i in all_targets:
    df_nodes_tmp = df_nodes.copy()
    df_nodes_tmp.loc[df_nodes_tmp['target']==i, 'average_direction'] = 1
    h_flip_pos = calc_H_pers(df_edges, df_nodes_tmp)
    df_nodes_tmp.loc[df_nodes_tmp['target']==i, 'average_direction'] = -1
    h_flip_neg = calc_H_pers(df_edges, df_nodes_tmp)
    h_flip_list.append((i, h_flip_pos, h_flip_neg))

df_h = pd.DataFrame(
    h_flip_list,
    columns=['target', 'h_flip_pos', 'h_flip_neg']
)

df_h['h_true_system'] = df_h_pers
df_h['sensitivity'] = df_h['h_flip_pos'] - df_h['h_flip_neg']

# add back in the opinion to see # 
df_h = df_h.merge(df_nodes, on = 'target', how = 'inner')
df_h = df_h[['target', 'h_flip_pos', 'h_flip_neg', 'h_true_system', 'average_direction', 'count', 'sensitivity']]
df_h.sort_values('sensitivity')
df_h

'''
So here we have: 
- mostly consistent (hard to make network better). 
- most things are negative; and should be.
- but looks like Trump *should* be more positive e.g.
--- to be fair I also think that he actually is... 
'''

# question: how do we find the optimal network
# what do we do about the mixed ones (e.g., 0.11 for Trump)

# to make this more effective we need a better implementation
# check our previous code from Simon DeDeo project. 

def check_edges(df_edges, df_nodes, focal):
    df_edges = df_edges[
        (df_edges['target']==focal) |
        (df_edges['source']==focal)
    ]
    df_edges = df_edges.sort_values('average_connection')

    # add nodes as well 
    df_nodes = df_nodes[['target', 'average_direction']]
    df_nodes = df_nodes.rename(columns={'average_direction': 'target_spin'})
    df_edges = df_edges.merge(df_nodes, on = 'target', how = 'inner')
    
    df_nodes = df_nodes.rename(columns={
        'target': 'source',
        'target_spin': 'source_spin'})
    df_edges = df_edges.merge(df_nodes, on = 'source', how = 'inner')
    
    return df_edges 

republicans = check_edges(df_edges_agg, df_nodes, 'Republicans (GOP)')

# yeah okay so we need something to find inconsistency
h_idx = df_nodes['target'].tolist()
h = df_nodes['average_direction'].to_numpy()
wh = df_nodes['count'].to_numpy()

# setup J combinations


def calc_H_numpy(h, J, wh = None, wJ = None):