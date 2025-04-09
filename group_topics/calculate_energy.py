import pandas as pd 
from itertools import combinations

# open or closed targets
user_id = '31499533'
body = 'with_body'
model = 'llama-3.3-70b-versatile'# 'deepseek-r1-distill-llama-70b'
date = '2025-03-31'
df = pd.read_csv(f'data/{user_id}_{body}_{model}_{date}.csv')

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

def aggregate_network(df):
    # 1. Normalize the pairs so source-target and target-source are treated the same
    df['pair'] = df.apply(lambda row: tuple(sorted([row['source'], row['target']])), axis=1)

    # 2. Group by the normalized pair and aggregate
    aggregated = df.groupby('pair').agg(
        average_connection=('connection', 'mean'),
        connection_count=('connection', 'count')
    ).reset_index()

    # 3. Optionally split the 'pair' back into two columns
    aggregated[['source', 'target']] = pd.DataFrame(aggregated['pair'].tolist(), index=aggregated.index)
    aggregated = aggregated.drop(columns='pair')
    return aggregated 

unique_idx = df['post_idx'].unique().tolist()
super_edges = []
for idx in unique_idx: 
    df_sub = df[df['post_idx']==idx]
    edges_sub = get_connections(df_sub, idx)
    super_edges.extend(edges_sub)

df_edges = pd.DataFrame(super_edges)
df_edges_agg = aggregate_network(df_edges)

### aggregation of nodes generally ###
df['direction'] = df['stance'].map({'FAVOR': 1, 'AGAINST': -1})
df_nodes = df.groupby('target').agg(
    average_direction=('direction', 'mean'),
    count=('direction', 'count')
).reset_index()

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
df_h_pers = calc_H_pers(df_edges_agg, df_nodes) 

# let us calculate this across all concepts we have # 
all_targets = df_nodes['target'].unique().tolist()
h_flip_list = []
for i in all_targets:
    df_nodes_tmp = df_nodes.copy()
    df_nodes_tmp.loc[df_nodes_tmp['target']==i, 'average_direction'] = 1
    h_flip_pos = calc_H_pers(df_edges_agg, df_nodes_tmp)
    df_nodes_tmp.loc[df_nodes_tmp['target']==i, 'average_direction'] = -1
    h_flip_neg = calc_H_pers(df_edges_agg, df_nodes_tmp)
    h_flip_list.append((i, h_flip_pos, h_flip_neg))

df_h = pd.DataFrame(
    h_flip_list,
    columns=['target', 'h_flip_pos', 'h_flip_neg']
)

df_h['h_true_system'] = df_h_pers
df_h['sensitivity'] = df_h['h_flip_pos'] - df_h['h_flip_neg']

# add back in the opinion to see # 
df_h = df_h.merge(df_nodes, on = 'target', how = 'inner')
df_h.sort_values('sensitivity')

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