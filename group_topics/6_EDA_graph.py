### think about networks now
# 1. triangles
# 2. centrality 
# 3. (other random metrics)
# 4. similarity 

import os 
import networkx as nx 
import pandas as pd 
import re 
from utility import compute_edges, aggregate_nodes, aggregate_edges
from collections import Counter
from itertools import combinations
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 

# overall setup 
breitbart_id = 'data/20250409_CT_DS70B_002' 
mjones_id = 'data/20250411_CT_DS70B_005' 
b5k_id = 'data/20250422_CT_DS70B_002'

def load_data(f):
    df = pd.read_csv(f)
    df_edges = compute_edges(df)
    df_edges_agg = aggregate_edges(df_edges)
    df_nodes_agg = aggregate_nodes(df)
    df_edges_agg['sign'] = np.where(df_edges_agg['average_connection'] > 0, 1, -1)
    return df_nodes_agg, df_edges_agg 

def create_graph(df_edges):
    # graph
    G = nx.Graph()
    for _, row in df_edges.iterrows():
        G.add_edge(
            row['source'], 
            row['target'], 
            closeness=row['average_connection'],
            strength=row['connection_count'],
            sign=row['sign']
        )
    # return 
    return G

def find_triangles(G):
    population_signs = Counter()
    node_dictionary = {}
    for node in G:
        node_signs = Counter()
        neighbors = list(G[node])
        for u, v in combinations(neighbors, 2):
            if G.has_edge(u, v):
                edges = [(node, u), (node, v), (u, v)]
                signs = [G[a][b].get('sign', None) for a, b in edges]
                if None not in signs:
                    num_pos = signs.count(1)
                    pattern = ''.join(sorted('+' * num_pos + '-' * (3 - num_pos), reverse=True))

                    # add 
                    population_signs[pattern] += 1
                    node_signs[pattern] += 1 
        # add 
        node_dictionary[node] = node_signs
    return population_signs, node_dictionary 

triangle_balance = {
    '+++': 1,
    '--+': 1,
    '-++': -1,
    '---': -1
}

# convert to dataframe as well 
def triangles_to_dataframe(triangle_dict):
    
    records = []

    for node, triangle_counts in triangle_dict.items():
        for triangle_type, count in triangle_counts.items():
            records.append({'target': node, 'triangle': triangle_type, 'count': count})

    df_triangles = pd.DataFrame(records)

    # balance and triangle types
    df_triangles['balance'] = df_triangles['triangle'].map(triangle_balance)
    df_triangles['w_balance'] = df_triangles['count'] * df_triangles['balance']
    df_triangles['frequency'] = df_triangles['count'] / df_triangles.groupby('target')['count'].transform('sum')
    df_triangles['n_balance'] = df_triangles['frequency'] * df_triangles['balance']

    return df_triangles

def get_short_id(file_path):
    for run_id in run_id_map:
        if run_id in file_path:
            return run_id_map[run_id]
    return None

## create a test graph ## 
run_id_map = {
    'data/20250422_CT_DS70B_002': 'B5k',
    'data/20250411_CT_DS70B_005': 'MJ',
    'data/20250409_CT_DS70B_002': 'BB'
}
paths = run_id_map.keys()
files = [os.path.join(path, file) for path in paths for file in os.listdir(path)]

node_tri_list = []
pop_tri_list = []
node_agg_list = []

for f in files: 
    # load 
    df_nodes_agg, df_edges_agg = load_data(f)

    # filter
    df_edges_agg[df_edges_agg['connection_count']>=5]

    # triangles
    G = create_graph(df_edges_agg)
    pop_triangles, node_triangles = find_triangles(G)    
    node_tri_df = triangles_to_dataframe(node_triangles)
    node_tri_df['platform'] = get_short_id(f)
    node_tri_df['user'] = f
    
    # collect nodes
    df_nodes_agg['platform'] = get_short_id(f)
    df_nodes_agg['user'] = f

    # append
    pop_tri_list.append(pop_triangles)
    node_tri_list.append(node_tri_df)
    node_agg_list.append(df_nodes_agg)

df_node_tri = pd.concat(node_tri_list)
df_node_agg = pd.concat(node_agg_list)

#### across topics (by user) ####
normalized_counters = []
for c in pop_tri_list:
    total = sum(c.values())
    freq_counter = Counter({k: v / total for k, v in c.items()})
    normalized_counters.append(freq_counter)

triangle_types = triangle_balance.keys()
records = []
for i, counter in enumerate(normalized_counters):
    for t_type in triangle_types: 
        records.append({
            'triangle': t_type,
            'proportion': counter.get(t_type, 0),
            'case': i
        })
df_pop = pd.DataFrame(records)

plt.figure(figsize=(5, 3))
sns.lineplot(
    data=df_pop,
    x='triangle',
    y='proportion',
    hue='case',
    palette='tab10',  # or any other palette
    legend=False      # hide legend if there are many cases
)
plt.title("Triangle Proportions by User")
plt.ylabel("Proportion")
plt.xlabel("Triangle Type")
plt.tight_layout()
plt.savefig('fig/exploratory/triangle_prop.png', dpi=300)

#### within topic + user ####
df_tri_agg = df_node_tri.groupby(['user', 'target', 'balance'])['n_balance'].sum().reset_index(name='proportion')
df_tri_agg = df_tri_agg[df_tri_agg['balance']==1]
df_tri_agg_freq = df_tri_agg.merge(df_node_agg, on = ['user', 'target'], how = 'inner')
df_tri_agg_freq['proportion_c'] = df_tri_agg_freq['count'] / df_tri_agg_freq.groupby('user')['count'].transform('sum')

fig, ax = plt.subplots(figsize=(6, 4))

# Scatter points, colored by user
sns.scatterplot(
    data=df_tri_agg_freq,
    x='proportion_c',
    y='proportion',
    hue='user',
    ax=ax,
    legend=False  # disables legend here
)

sns.regplot(
    data=df_tri_agg_freq,
    x='proportion_c',
    y='proportion',
    scatter=False,
    ax=ax,
    color='black',  # or whatever global fit color
    line_kws={'linewidth': 1, 'linestyle': '--'}
)

# Customize axes
ax.set_xlabel("Concept-level Frequency")
ax.set_ylabel("Proportion of Balanced Triads")
ax.set_title("Triadic Balance by User")

# Save the plot
plt.savefig("fig/exploratory/triadic_lmplot.png", dpi=300, bbox_inches='tight')

#### can we do anything over time? #### 
