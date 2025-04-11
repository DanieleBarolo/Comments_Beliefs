import pandas as pd 
import os 
import re
import yaml
from utility import compute_edges, aggregate_edges, aggregate_nodes, plot_network


# open or closed targets
run_id = '20250411_CT_DS70B_005'
path = f'data/{run_id}'
files = os.listdir(path) 

# make directory 
outdir = os.path.join('fig', 'aggregate', run_id)
if not os.path.exists(outdir): 
    os.makedirs(outdir)

# test on one random guy
for f in files: 
    user_id = re.match(r'\d+', f).group()
    df = pd.read_csv(os.path.join(path, f))
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
