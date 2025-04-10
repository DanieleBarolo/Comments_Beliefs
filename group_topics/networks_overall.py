import pandas as pd 
import matplotlib.pyplot as plt
import networkx as nx 
import os 
import re
from utility import get_connections, compute_edges, aggregate_edges, aggregate_nodes

### first network ### 
def plot_network(df_edges_agg, df_nodes_agg, edge_scale, node_scale, edge_n_threshold=1, k=0.5, savefig=False):
    cmap = plt.cm.RdYlGn

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
    pos = nx.spring_layout(G, k = k, weight='closeness', seed=42)

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
        if count <= edge_n_threshold: 
            edge_widths.append(0)
        else: 
            edge_widths.append(count * edge_scale)

    # for now set edge width to zero if only 1 occurence
    # edge_widths = [x if x > 0.9 else 0 for x in edge_widths]

    # Add node information
    attr_dict = df_nodes_agg.set_index('target').to_dict(orient='index')
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
        node_sizes.append(count * node_scale)

    # Step 4: Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=cmap)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.7, edge_cmap=cmap)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

    # Optional: edge labels showing weight
    #edge_labels = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.2f}" for k, v in edge_labels.items()}, font_size=8)

    plt.axis('off')
    plt.title("")
    plt.tight_layout()
    
    if savefig: 
        plt.savefig(savefig)
        plt.close()
    else: 
        plt.show()

# import yaml file for topics 

# open or closed targets
run_id = '20250409_CT_DS70B_002'
path = f'data/{run_id}'
files = os.listdir(path) 
yaml_path = f'../Batch_calling/data/experiments/runs/{run_id}/config.yaml'

import yaml
with open(yaml_path, 'r') as f:
    batch_information = yaml.safe_load(f)
target_list = batch_information['prompts']['targets']

# make directory 
outdir = os.path.join('fig', 'aggregate', run_id)
if not os.path.exists(outdir): 
    os.makedirs(outdir)

# test on one random guy
for f in files: 
    user_id = re.match(r'\d+', f).group()
    df = pd.read_csv(os.path.join(path, f))
    df = df.drop(columns='explanation').drop_duplicates()
    df = df[df['target'].isin(target_list)]
    df_edges = compute_edges(df)
    df_edges_agg = aggregate_edges(df_edges)
    df_nodes_agg = aggregate_nodes(df)
    # make network 
    plot_network(
        df_edges_agg = df_edges_agg,
        df_nodes_agg = df_nodes_agg, 
        edge_scale = 0.5, 
        node_scale = 10, 
        edge_n_threshold = 5,
        k = 1,
        savefig = os.path.join(outdir, user_id)
        )
