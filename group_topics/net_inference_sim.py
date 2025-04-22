import numpy as np
import graph_tool.all as gt 
import os 
import re 
import pandas as pd 
from utility import compute_edges, aggregate_edges, aggregate_nodes
from ising_fun import * 
import json
from tqdm import tqdm

# basic setup  
inpath = 'sim'
n_nodes = 10
n_couplings = n_nodes * (n_nodes - 1) // 2
n_obs = 1000

# load the normal data and wrange a bit 
ising_normal = pd.read_csv(os.path.join(
    inpath,
    f'nodes_{n_nodes}_obs_{n_obs}_normal.csv'
))
s = ising_normal.to_numpy()
s = s.T
s[s == 0] = -1

# now try to fit their thing
state = gt.PseudoIsingBlockState(
    s = s, 
    has_zero = False, 
    # active = active # 
    directed=False, 
    self_loops=False,
    # theta_range=[(0, 0)],
    # theta_range = [(-inf, inf)]: fields
    # x_range = (-inf, inf): couplings
    )

# first fitting / burn-in
convergence_metrics = {}
for i in tqdm(range(10)):
    delta, *_ = state.mcmc_sweep(beta=np.inf, niter=20)
    entropy = state.entropy()
    convergence_metrics[i] = {
        'delta': delta, 
        'entropy': entropy}

# we can save convergence statistics here
# but overall it looks good.

'''
Looks good for this one.
'''

# now we actually sample 
# although; not 100% sure how we basically "throw away" burn-in.
g = None 
sampling_metrics = {}
for i in tqdm(range(20)):
    delta, *_ = state.mcmc_sweep( # metropolis hastings.
        beta=1, # inverse temperature 
        niter=20) # number of sweeps 
    entropy = state.entropy()
    g = state.collect_marginal(g)
    num_edges = state.bstate.g.num_edges()
    sampling_metrics[i] = {
        'entropy': entropy, 
        'delta': delta, 
        'g': g, 
        'num_edges': num_edges
    }

# check what we have 
len(state.x.a) # edge weights (but length ~n=25)
state.bstate.g # graph overview (n edges = 20)
state.bstate.b.a # group assignment (all same)

# check how good the inference is 
# - edges are 
# - nodes are 
# compared to true Ising 
with open(os.path.join(
    inpath,
    f"nodes_{n_nodes}_obs_{n_obs}_normal.json"
), 'r') as f: 
    ising_dict = json.load(f)

p_true = ising_dict['probabilities'] # n=1024
h_true = ising_dict['local_fields'] # n=10
J_true = ising_dict['pairwise_couplings'] # n=45

# getting the spins out (not working)
node_indices = [v for v in g.vertices()]
node_ids = [int(v) for v in g.vertices()]
spins = state.s
node_spins = [spins[int(v)] for v in g.vertices()]

# getting the edges/couplings (does not work)
edges = [{
    'source': int(e.source()),
    'target': int(e.target())
} for e in g.edges()]
df_edges = pd.DataFrame(edges)
df_edges = df_edges.sort_values(['source', 'target'], ascending=True)

'''
But — graph-tool doesn't directly give you the coupling constants 
(i.e. interaction strengths like Jij) the way a traditional 
Ising model would. Instead, the inferred structure in state.get_graph() 
is a sparse, binary encoding of the dependency structure — i.e., 
edges are inferred if there is a dependency, not how strong it is.

Is this also true for the spins? 

Then we cannot get to the "landscape" model, really. 
I basically thought that this was a cool implementation of the Ising/Potts.

And actually it is not clear to me how this *would* infer an Ising model
in any strong sense. Like, how would the likelihood function work to 
"ignore" all of the missing data (we struggled with much less missing data..)
'''
