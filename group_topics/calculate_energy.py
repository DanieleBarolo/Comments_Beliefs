import numpy as np 
import pandas as pd 

# load network 
user_id = '31499533'
df = pd.read_csv(f'data/targets_closed_{user_id}.csv')
df.head(5)
