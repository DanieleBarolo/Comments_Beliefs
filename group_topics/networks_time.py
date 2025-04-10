import pandas as pd 
import matplotlib.pyplot as plt
import networkx as nx 
import os 
import re
from utility import compute_edges, aggregate_edges, aggregate_nodes
import shutil

def recreate_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)  # Deletes directory and all its contents
    os.makedirs(directory_path) 

### first network ### 
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

# group into time slices, but overlapping # 
def create_time_windows(df, window_size_days, move_size_days, date_col='comment_date'):
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

    return slices

def get_pos(df_edges, k=1):

    G = nx.Graph()
    for _, row in df_edges.iterrows():
        G.add_edge(
            row['source'], 
            row['target'], 
            closeness=row['average_connection'],
            strength=row['connection_count']
            )
    pos = nx.spring_layout(G, k = k, weight='closeness', seed=42)
    return pos 

def get_fixed_pos(pos): 
    # Compute global axis limits based on the positions
    x_vals, y_vals = zip(*pos.values())
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)

    # Add some padding for clarity
    padding = 0.1
    x_range = x_max - x_min
    y_range = y_max - y_min

    global_x_lim = (x_min - padding * x_range, x_max + padding * x_range)
    global_y_lim = (y_min - padding * y_range, y_max + padding * y_range)

    return global_x_lim, global_y_lim


def plot_time_slices(
    time_slices, 
    pos,
    outdir,
    global_x_lim=None,
    global_y_lim=None,
    n_min = 25,
    edge_scale=0.5,
    node_scale=10,
    edge_n_threshold=0,
    k=1
    ):
    
    for i in time_slices:
        start = i['start'].strftime('%Y-%m-%d')
        end = i['end'].strftime('%Y-%m-%d')
        data = i['data']

        if len(data) > n_min: 
            # now aggregate on this 
            df_edges = compute_edges(data)
            df_edges_agg = aggregate_edges(df_edges)
            df_nodes_agg = aggregate_nodes(data)

            # make network 
            plot_network(
                df_edges_agg = df_edges_agg,
                df_nodes_agg = df_nodes_agg, 
                edge_scale = edge_scale, 
                node_scale = node_scale, 
                edge_n_threshold = edge_n_threshold, 
                k = k,
                pos = pos,
                fixed_xlim=global_x_lim,
                fixed_ylim=global_y_lim,
                savefig = os.path.join(outdir, f"start_{start}_end_{end}.png") 
                )

### actually run shit ###
run_id = '20250409_CT_DS70B_002'
path = f'data/{run_id}'
files = os.listdir(path) 
yaml_path = f'../Batch_calling/data/experiments/runs/{run_id}/config.yaml'

import yaml
with open(yaml_path, 'r') as f:
    batch_information = yaml.safe_load(f)
target_list = batch_information['prompts']['targets']

# make directory 
outdir = os.path.join('fig', 'temporal', run_id)
if not os.path.exists(outdir): 
    os.makedirs(outdir)

for f in files: 
    # get basic data out 
    user_id = re.match(r'\d+', f).group()
    df = pd.read_csv(os.path.join(path, f))
    df = df.drop(columns='explanation').drop_duplicates()
    df = df[df['target'].isin(target_list)]

    # create time slices
    time_slices = create_time_windows(
        df=df,
        window_size_days=500, # 1 year
        move_size_days=100
    )
    
    # aggregate position 
    df_edges = compute_edges(df)
    df_edges_agg = aggregate_edges(df_edges)
    aggregate_position = get_pos(df_edges_agg)
    global_x_lim, global_y_lim = get_fixed_pos(aggregate_position)

    # create directory (delete if exists)
    directory_participant = os.path.join(outdir, user_id)
    recreate_directory(directory_participant)
    
    plot_time_slices(
        time_slices = time_slices,
        pos = aggregate_position,
        outdir=directory_participant, # make 
        global_x_lim=global_x_lim,
        global_y_lim=global_y_lim,
    )