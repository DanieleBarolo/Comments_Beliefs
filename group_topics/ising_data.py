# generate basic mpf data 
import os 
import json
from ising_fun import *

# setup  
output_folder = 'sim'
n_nodes = 10
n_couplings = n_nodes * (n_nodes - 1) // 2 
n_obs = 1000
states = bin_states(n_nodes)

# generate params
normal_h, normal_J = normal_params(n_nodes)
ising_h, ising_J = ising_params(n_nodes)

# generate data 
normal_p = p_dist(normal_h, normal_J)
ising_p = p_dist(ising_h, ising_J)

normal_obs = generate_obs(states, n_obs, normal_p)
ising_obs = generate_obs(states, n_obs, ising_p)

# save data 
overall_path = f'nodes_{n_nodes}_obs_{n_obs}'
normal_obs.to_csv(os.path.join(output_folder, f'{overall_path}_normal.csv'), index=False)
ising_obs.to_csv(os.path.join(output_folder, f'{overall_path}_ising.csv'), index=False)

# save parameters & true p
data = {
    'probabilities': normal_p.tolist(),
    'local_fields': normal_h.tolist(),
    'pairwise_couplings': normal_J.tolist()
}
save_path = os.path.join(output_folder, f'{overall_path}_normal.json')
with open(save_path, 'w') as f: 
    json.dump(data, f)
    
data = {
    'probabilities': ising_p.tolist(),
    'local_fields': ising_h.tolist(),
    'pairwise_couplings': ising_J.tolist()
}
save_path = os.path.join(output_folder, f'{overall_path}_ising.json')
with open(save_path, 'w') as f: 
    json.dump(data, f)
