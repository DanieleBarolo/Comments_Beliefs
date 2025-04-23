import pandas as pd 
import matplotlib.pyplot as plt 
import networkx as nx 
from itertools import combinations 

# this is not super effective
def get_connections(df, idx):

    df['direction'] = df['stance'].map({'FAVOR': 1, 'AGAINST': -1})
    pairs = list(combinations(df.index, 2))

    # Create edges list
    edges = []

    for idx1, idx2 in pairs:
        target1, stance1 = df.loc[idx1, ['target', 'direction']]
        target2, stance2 = df.loc[idx2, ['target', 'direction']]

        connection = 1 if stance1 == stance2 else -1

        edges.append({
            'source': target1,
            'target': target2,
            'source_spin': stance1, 
            'target_spin': stance2,
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

# just for basic plotting 
def plot_network(df_edges_agg, df_nodes_agg, edge_scale, node_scale,
                 edge_n_threshold=1, k=1, pos=None, fixed_xlim=None, fixed_ylim=None,
                 savefig=False):
    
    cmap = plt.cm.RdYlGn

    # Create graph
    G = nx.Graph()
    for _, row in df_edges_agg.iterrows():
        G.add_edge(
            row['source'], 
            row['target'], 
            closeness=row['average_connection'],
            strength=row['connection_count']
        )

    # Use provided fixed positions directly
    if pos is None: 
        pos = nx.spring_layout(G, k=k, weight='closeness', seed=42)

    # Edge attributes
    edge_colors = [(data['closeness'] + 1)/2 for _, _, data in G.edges(data=True)]
    edge_widths = [data['strength']*edge_scale if data['strength']>edge_n_threshold else 0 for _, _, data in G.edges(data=True)]

    # Node attributes
    attr_dict = df_nodes_agg.set_index('target').to_dict(orient='index')
    nx.set_node_attributes(G, attr_dict)

    node_colors = [(G.nodes[n].get('average_direction',0)+1)/2 for n in G.nodes()]
    node_sizes = [G.nodes[n].get('count',1)*node_scale for n in G.nodes()]

    # Plotting
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=cmap)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.7, edge_cmap=cmap)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

    # Set fixed limits
    if fixed_xlim and fixed_ylim:
        plt.xlim(fixed_xlim)
        plt.ylim(fixed_ylim)

    plt.axis('off')
    plt.tight_layout()

    if savefig: 
        plt.savefig(savefig)
        plt.close()
    else: 
        plt.show()

def flatten_time_windows(windows, time_col_name='time_slice'):
    frames = []
    for w in windows:
        df_slice = w['data'].copy()
        df_slice[time_col_name] = w['start']  # tag each row with the start of its window
        frames.append(df_slice)
    return pd.concat(frames, ignore_index=True)

def create_time_windows(df, window_size_days, move_size_days, date_col='comment_date', return_df=False):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    # Get the range of dates
    start_date = df[date_col].min()
    end_date = df[date_col].max()

    # Initialize slices
    slices = []
    current_start = start_date

    # Generate slices
    while current_start + pd.Timedelta(days=window_size_days) <= end_date:
        current_end = current_start + pd.Timedelta(days=window_size_days)

        slice_df = df[(df[date_col] >= current_start) & (df[date_col] < current_end)]
        slices.append({
            'start': current_start,
            'end': current_end,
            'data': slice_df
        })

        current_start += pd.Timedelta(days=move_size_days)

    if return_df: 
        return flatten_time_windows(slices)

    return slices