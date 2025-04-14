# example case 
# https://graph-tool.skewed.de/static/doc/demos/reconstruction_indirect/reconstruction.html
# just continue from where we left off tomorrow. 
import numpy as np
import graph_tool as gt 
import graph_tool.collection
import graph_tool.dynamics 
import graph_tool.draw 
import graph_tool.inference
import graph_tool.topology 
import matplotlib 

g = gt.collection.data["dolphins"]

E = g.num_edges()
N = g.num_vertices()
w = g.new_ep("double", vals=np.random.normal(N/(2*E), .05, E))  # True edge weights
istate = gt.dynamics.IsingGlauberState(g, w=w)

M = 1000
X = []
for m in range(M):
    istate.iterate_sync()
    X.append(istate.get_state().a.copy())
X = np.array(X).T

state = gt.inference.IsingGlauberBlockState(X, directed=False, self_loops=False)

for i in range(10):
    delta, *_ = state.mcmc_sweep(beta=np.inf, niter=10)
    print(delta)

# similarity 
u = state.get_graph()      # reconstructed network
w_r = state.get_x()        # reconstructed weights
t_r = state.get_theta()    # reconstructed thetas

print(gt.topology.similarity(g, u, w, w_r)) # ~0.9

# DRAW 
cnorm = matplotlib.colors.Normalize(vmin=-abs(w.fa).max(), vmax=abs(w.fa).max())

# Original graph
gt.draw.graph_draw(
    g, 
    g.vp.pos, 
    edge_pen_width=gt.draw.prop_to_size(w.t(abs), 2, 8, power=1), 
    edge_color=w,
    ecmap=matplotlib.cm.coolwarm_r, 
    ecnorm=cnorm, 
    output="net_inference/dolphins-orig.pdf"
    )

# Inferred graph
gt.draw.graph_draw(
    u, 
    g.vp.pos, 
    edge_pen_width=gt.draw.prop_to_size(w_r.t(abs), 2, 8, power=1), 
    edge_color=w_r,
    ecmap=matplotlib.cm.coolwarm_r, 
    ecnorm=cnorm, 
    output="net_inference/dolphins-inf.pdf"
    )

# Inferred graph with SBM partition
state.bstate.draw(
    pos=g.vp.pos, 
    edge_gradient=[],
    edge_pen_width=gt.draw.prop_to_size(w_r.t(abs), 2, 8, power=1),
    edge_color=w_r, ecmap=matplotlib.cm.coolwarm_r, 
    ecnorm=cnorm,
    output="net_inference/dolphins-inf-sbm.pdf"
    )
