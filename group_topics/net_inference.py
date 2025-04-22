import numpy as np
import graph_tool.all as gt 
import os 
import re 
import pandas as pd 
from utility import compute_edges, aggregate_edges, aggregate_nodes

# open or closed targets
run_id = '20250411_CT_DS70B_005'
path = f'data/{run_id}'
files = os.listdir(path) 
f = files[1]
user_id = re.match(r'\d+', f).group()
df = pd.read_csv(os.path.join(path, f))
df['direction'] = df['stance'].map(
    {
    "AGAINST": -1,
    "FAVOR": 1
})

#### try 1: wide format matrix #### 
df_wide = df.pivot_table(
    index='target', 
    columns='comment_id', 
    values='direction', 
    fill_value=0
    )
s = df_wide.to_numpy()
#s = np.ones_like(s)
#s[1, :] = -1
#s[2, :] = -1
active = s.copy()
active = np.abs(active)

# try other s fun
# Example shape
shape = (50, 358)  # Change this to your desired shape

# Create array with -1 and +1
#s = np.random.choice([-1, 1], size=shape)
#s[1, :] = s[2, :]

# MDL 
# assumes drawn from same distribution
# not a markov chain
# has_zero = True (Daniele point).
state = gt.PseudoIsingBlockState(
    s = s, 
    has_zero = False, # change
    active = active,
    directed=False, 
    self_loops=False,
    theta_range=[(0, 0)],
    # theta_range = [(-inf, inf)]: fields
    # x_range = (-inf, inf): couplings
    )

# range(10) and niter=100 is equal to niter=1K
# run for longer
g = None 
entropy_list = []
g_list = []
edgenum_list = []

# first inf (burn-in)
for i in range(10):
    delta, *_ = state.mcmc_sweep(beta=np.inf, niter=20)
    # entropy 

# now we do sample with beta=1
for i in range(20):
    delta, *_ = state.mcmc_sweep(beta=1, niter=20)
    print(delta)
    entropy = state.entropy()
    entropy_list.append(entropy)
    g = state.collect_marginal(g)
    g_list.append(g)
    edge_num = state.bstate.g.num_edges()
    edgenum_list.append(edge_num)

gt.graph_draw(g)
# state 
state.x.a # would have been weights for edges
# state.g
state.bstate.g
state.theta[5] # theta: local/external fields
state.bstate.b.a # group
g.ep.eprob.a # 3 edges.. (one appears in all samples--i.e., the good one...)
# eprob: how often do they appear.. 
import matplotlib.pyplot as plt 
#import seaborn as sns 
plt.hist(g.ep.eprob.a,
         100)
np.unique(s, return_counts=True)


'''
first do the inf to stabilize.
then do beta=1 
'''

'''
Key thing is that we have basically too many parameters.
Everything can just be explained by nodes. 

If there is change though we would expect couplings. 

Bigger data (n=5K e.g.,)
'''

# similarity 
u = state.get_graph()      # reconstructed network
w_r = state.get_x()        # reconstructed weights
t_r = state.get_theta()    # reconstructed thetas

'''
Tentatively does not work.
I get *no* edges here.
'''

#### try the pre-aggregated #### 
df_edges = compute_edges(df)
df_edges_agg = aggregate_edges(df_edges)
df_nodes_agg = aggregate_nodes(df)

# try something new here 
df_nodes_agg['power'] = df_nodes_agg['average_direction'] * df_nodes_agg['count']
df_edges_agg['power'] = df_edges_agg['average_connection'] * df_edges_agg['connection_count']

# Initialize an undirected graph
g = gt.Graph(directed=False)

# Create property maps
vprop_name = g.new_vertex_property("string")
vprop_avg_dir = g.new_vertex_property("double")
vprop_count = g.new_vertex_property("int")
vprop_pwr = g.new_vertex_property("double")

eprop_avg_conn = g.new_edge_property("double")
eprop_conn_count = g.new_edge_property("int")
eprop_pwr = g.new_edge_property("double")

# Map node identifiers to vertex objects
node_map = {}

# Add vertices
for idx, row in df_nodes_agg.iterrows():
    v = g.add_vertex()
    vprop_name[v] = str(row['target'])
    vprop_avg_dir[v] = row['average_direction']
    vprop_count[v] = row['count']
    vprop_pwr[v] = row['power']
    node_map[row['target']] = v

# Add edges
for idx, row in df_edges_agg.iterrows():
    src = node_map.get(row['source'])
    tgt = node_map.get(row['target'])
    if src is not None and tgt is not None:
        e = g.add_edge(src, tgt)
        eprop_avg_conn[e] = row['average_connection']
        eprop_conn_count[e] = row['connection_count']
        eprop_pwr[e] = row['power']

# Assign property maps to the graph
g.vertex_properties["name"] = vprop_name
g.vertex_properties["avg_direction"] = vprop_avg_dir
g.vertex_properties["count"] = vprop_count
g.vertex_properties['power'] = vprop_pwr

g.edge_properties["avg_connection"] = eprop_avg_conn
g.edge_properties["connection_count"] = eprop_conn_count
g.edge_properties['power'] = eprop_pwr

# Nested block model on this? 
state = gt.inference.minimize_nested_blockmodel_dl(
    g,
    state_args=dict(
        #eweight=g.ep.
        recs=[g.ep.power],
        rec_types=["real-exponential"],
        deg_corr=True
    )
)

# Draw the inferred nested block model
# Can we draw this with labels? 
pos = gt.draw.sfdp_layout(g)
state.draw(
    pos=pos,
    vertex_font_size=12,
    ink_scale=0.2,
    vertex_text=g.vertex_properties["name"],
    output="reconstruction/test.png")

### second try with aggregation ### 
