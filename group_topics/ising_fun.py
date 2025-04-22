import numpy as np 
import itertools 
import os 
import pandas as pd

def normal_params(n_nodes, sd=0.5): 
    n_couplings = n_nodes * (n_nodes - 1) // 2
    fields = np.random.normal(0, sd, n_nodes)
    couplings = np.random.normal(0, sd, n_couplings)
    return fields, couplings

# closer to IsingFit 
def ising_params(n_nodes, p_missing=0.5): 
    # first generate couplings (here uniform)
    n_couplings = n_nodes * (n_nodes - 1) // 2
    couplings = np.random.uniform(0.5, 2, n_couplings)
    
    # set some couplings to 0
    mask = np.random.rand(len(couplings)) < p_missing
    couplings[mask] = 0
    
    # now local fields by column (or similarly row) sums
    pairs = list(itertools.combinations(range(1, n_nodes + 1), 2))
    node_sums = {n: 0 for n in range(1, n_nodes + 1)}
    for coupling, (i, j) in zip(couplings, pairs):
        node_sums[i] += coupling
        node_sums[j] += coupling
    fields = np.array([node_sums[node] for node in sorted(node_sums)])
    
    # needs to be negative row sums divided by 2 
    fields = -fields / 2
    return fields, couplings

def write_to_mpf(df, output_folder, output_filename, weights=1.0): 
    columns = df.columns.tolist()
    n_obs = df.shape[0]
    n_nodes = len(columns)
    df['weight'] = weights
    formatted_rows = df.apply(
        lambda row: f"{''.join(map(str, row[columns].astype(int).tolist()))} {row['weight']:.2f}",
        axis=1
    )
    # save 
    output = f"{n_obs}\n{n_nodes}\n" + '\n'.join(formatted_rows)
    with open(os.path.join(output_folder, output_filename), 'w') as f: 
        f.write(output)
        
def load_mpf_params(n_nodes, path): 
    with open(path, 'r') as f:
        mpf_data = f.readline().strip()
    
    n_couplings = n_nodes * (n_nodes - 1) // 2
    mpf_params = np.array(mpf_data.split(), dtype=float)
    mpf_couplings = mpf_params[:n_couplings]
    mpf_fields = mpf_params[n_couplings:]
    return mpf_fields, mpf_couplings

# taken from coniii enumerate
def fast_logsumexp(X, coeffs=None):
    """correlation calculation in Ising equation

    Args:
        X (np.Array): terms inside logs
        coeffs (np.Array, optional): factors in front of exponential. Defaults to None.

    Returns:
        float: sum of exponentials
    """
    Xmx = max(X)
    if coeffs is None:
        y = np.exp(X-Xmx).sum()
    else:
        y = np.exp(X-Xmx).dot(coeffs)

    if y<0:
        return np.log(np.abs(y))+Xmx, -1.
    return np.log(y)+Xmx, 1.

# still create J_combinations is slow for large number of nodes
def p_dist(h, J):
    """return probabilities for 2**h states

    Args:
        h (np.Array): local fields
        J (np.Array): pairwise couplings. 

    Returns:
        np.Array: probabilities for all configurations
    """
    n_nodes = len(h)
    hJ = np.concatenate((h, J))
    h_combinations = np.array(list(itertools.product([1, -1], repeat = n_nodes)))
    J_combinations = np.array([list(itertools.combinations(i, 2)) for i in h_combinations])
    J_combinations = np.add.reduce(J_combinations, 2)
    J_combinations[J_combinations != 0] = 1
    J_combinations[J_combinations == 0] = -1
    condition_arr = np.concatenate((h_combinations, J_combinations), axis = 1)
    flipped_arr = hJ * condition_arr
    summed_arr = np.sum(flipped_arr, axis = 1)
    logsumexp_arr = fast_logsumexp(summed_arr)[0]
    Pout = np.exp(summed_arr - logsumexp_arr)
    return Pout[::-1]

def bin_states(n, sym=True):
    """generate 2**n possible configurations

    Args:
        n (int): number of questions (features)
        sym (bool, optional): symmetric system. Defaults to True.

    Returns:
        np.Array: 2**n configurations 
    """
    v = np.array([list(np.binary_repr(i, width=n)) for i in range(2**n)]).astype(int)
    if sym is False:
        return v
    return v*2-1

def generate_obs(states, n_observations, p): 
    observations = np.random.choice(len(p), size=n_observations, p=p)
    mapping = states[observations]
    columns = [f"Q{i+1}" for i in range(states.shape[1])]
    df = pd.DataFrame(mapping, columns=columns)
    df = df.replace(-1, 0)
    return df