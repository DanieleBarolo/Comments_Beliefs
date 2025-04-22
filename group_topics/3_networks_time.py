import pandas as pd 
import networkx as nx 
import os 
import re
from utility import compute_edges, aggregate_edges, aggregate_nodes, plot_network, create_time_windows
import shutil

def recreate_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)  # Deletes directory and all its contents
    os.makedirs(directory_path) 

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
    edge_scale=0.05,
    node_scale=1,
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
run_id = '20250422_CT_DS70B_002'
path = f'data/{run_id}'
files = os.listdir(path) 

# make directory 
outdir = os.path.join('fig', 'temporal', run_id)
if not os.path.exists(outdir): 
    os.makedirs(outdir)

for f in files: 
    # get basic data out 
    user_id = re.match(r'\d+', f).group()
    df = pd.read_csv(os.path.join(path, f))

    # create time slices
    time_slices = create_time_windows(
        df=df,
        window_size_days=500, 
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