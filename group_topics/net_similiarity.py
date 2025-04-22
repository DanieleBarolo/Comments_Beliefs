'''
Importantly, you can aggregate in 2 ways; either: 
1. first individual --> then collective
2. directly to collective from raw observations

Also importantly--we might have more than n>1
user per comment so we can also think about this
in different ways. 

Actually doing this "by comment" would be consistent
with the typical way to do this. 

'''

import pandas as pd 
import os 
import re
from utility import compute_edges, aggregate_edges, aggregate_nodes, plot_network

# open or closed targets
run_id = '20250411_CT_DS70B_005' # breitbart
path = f'data/{run_id}'
files = os.listdir(path) 

# run for all 
node_list = []
edge_list = []
for f in files: 
    user_id = re.match(r'\d+', f).group()
    
    # read + edges
    df = pd.read_csv(os.path.join(path, f))
    df_edges = compute_edges(df)

    # add user id
    df['user_id'] = user_id 
    df_edges['user_id'] = user_id 

    # append
    node_list.append(df)
    edge_list.append(df_edges)
df_nodes = pd.concat(node_list)
df_edges = pd.concat(edge_list)

# now we can aggregate this 
# but the function might need to be modified
# depending on what we want 
df_nodes_agg = aggregate_nodes(df_nodes)
df_edges_agg = aggregate_edges(df_edges)

# try to plot it 
plot_network(
    df_edges_agg=df_edges_agg,
    df_nodes_agg=df_nodes_agg,
    edge_scale=0.05,
    node_scale=1,
    edge_n_threshold=5,
    k=1,
    savefig=f'fig/population/{run_id}.png'
)

# also need to aggregate at user level 
user_idx = df_nodes['user_id'].unique().tolist()
list_user_nodes = []
list_user_edges = []
for user in user_idx: 
    # take out for users
    df_nodes_user = df_nodes[df_nodes['user_id']==user]
    df_edges_user = df_edges[df_edges['user_id']==user]
    # aggregate
    df_nodes_user_agg = aggregate_nodes(df_nodes_user)
    df_edges_user_agg = aggregate_edges(df_edges_user)
    df_nodes_user_agg['user_id'] = user
    df_edges_user_agg['user_id'] = user 
    # append
    list_user_nodes.append(df_nodes_user_agg)
    list_user_edges.append(df_edges_user_agg)
df_nodes_user = pd.concat(list_user_nodes)
df_edges_user = pd.concat(list_user_edges)

# clearly they do not have all topics
# so this makes it maybe a bit tricky to compare 

# now what would be interesting is: 
# 1. who is dissimilar to aggregate?
# 2. can do this also at landscape level (ofc.)
