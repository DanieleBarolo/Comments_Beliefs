import numpy as np 
import pandas as pd 
from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx 

# open or closed targets
user_id = '46279190'
df = pd.read_csv(f'data/targets_closed_{user_id}.csv')

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
agg_df = df.groupby('target').agg(
    average_direction=('direction', 'mean'),
    count=('direction', 'count')
).reset_index()

### general setup ###
cmap = plt.cm.bwr

### first network ### 

# Step 1: Create the graph
G = nx.Graph()

# Step 2: Add edges with weight = average_connection
for _, row in df_edges_agg.iterrows():
    # Use the average_connection as "closeness" (higher = closer)
    # NetworkX uses 'weight' as a distance metric, so we can optionally invert it for layout
    G.add_edge(
        row['source'], 
        row['target'], 
        closeness=row['average_connection'],
        strength=row['connection_count']
        )

# Step 3: Compute layout based on weights (stronger = closer)
# Invert weights to simulate distance (layout places closer nodes when distance is small)
#inverse_weights = {(u, v): 1 / d['weight'] if d['weight'] != 0 else 1e6 for u, v, d in G.edges(data=True)}
#nx.set_edge_attributes(G, 'strength')

# Use spring layout with "distance" as distance metric
pos = nx.spring_layout(G, k = 1, weight='closeness', seed=42)

# Add edge information
edge_colors = []
edge_widths = []

for u, v, data in G.edges(data=True):
    avg_conn = data.get('closeness', 0)
    count = data.get('strength', 1)
    
    # Normalize color: -1 → 0 (red), 1 → 1 (blue)
    color_val = (avg_conn + 1) / 2
    edge_colors.append(color_val)

    # Scale line width
    edge_widths.append(count * 0.8)

# for now set edge width to zero if only 1 occurence
#edge_widths = [x if x > 0.9 else 0 for x in edge_widths]

# Add node information
attr_dict = agg_df.set_index('target').to_dict(orient='index')
nx.set_node_attributes(G, attr_dict)

# Color map from red (-1) → white (0) → blue (1)
node_colors = []
node_sizes = []

for node in G.nodes():
    data = G.nodes[node]
    avg_dir = data.get('average_direction', 0)
    count = data.get('count', 1)
    
    # Normalize to [0, 1] for colormap: -1 → 0 (red), 0 → 0.5 (white), 1 → 1 (blue)
    color_val = (avg_dir + 1) / 2
    node_colors.append(color_val)
    
    # Scale node size (optional: tweak multiplier for visibility)
    node_sizes.append(300 + count * 50)

# Step 4: Draw the graph
plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=cmap)
nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.7, edge_cmap=cmap)
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

# Optional: edge labels showing weight
#edge_labels = nx.get_edge_attributes(G, 'weight')
#nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.2f}" for k, v in edge_labels.items()}, font_size=8)

plt.axis('off')
plt.title("Undirected Conceptual Similarity Network", fontsize=14)
plt.tight_layout()
plt.savefig(f'fig/closed_unidrected_dir_{user_id}.png', bbox_inches='tight')

'''
Look at self-loop (Christians).
'''