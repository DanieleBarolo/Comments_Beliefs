import pandas as pd 
from itertools import combinations 

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
            'comment_id': idx
        })

    return edges

def compute_edges(df):
    unique_comments = df['comment_id'].unique().tolist()
    super_edges = []
    for idx in unique_comments: 
        df_sub = df[df['comment_id']==idx]
        edges_sub = get_connections(df_sub, idx)
        super_edges.extend(edges_sub)

    df_edges = pd.DataFrame(super_edges)
    return df_edges

def aggregate_edges(df):
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

def aggregate_nodes(df):
    df['direction'] = df['stance'].map({'FAVOR': 1, 'AGAINST': -1})
    aggregated_nodes = df.groupby('target').agg(
        average_direction=('direction', 'mean'),
        count=('direction', 'count')
    ).reset_index()
    return aggregated_nodes