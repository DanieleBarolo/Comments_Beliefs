import numpy as np 
import pandas as pd 
import os 
import re
from utility import aggregate_nodes
import seaborn as sns 
import matplotlib.pyplot as plt 

# actually get distributions first will be interesting
def agg_nodes_run(run_id):

    path = os.path.join('data', run_id)
    files = os.listdir(path)    

    nodes_list = []
    for f in files: 
        user_id = re.search(r'\d+', f)[0]
        df = pd.read_csv(os.path.join(path, f))
        df_nodes = aggregate_nodes(df)
        df_nodes['user_id'] = user_id
        nodes_list.append(df_nodes)

    df_nodes_agg = pd.concat(nodes_list)

    return df_nodes_agg

breitbart_id = '20250409_CT_DS70B_002' 
mjones_id = '20250411_CT_DS70B_005' 
breitbart_nodes = agg_nodes_run(breitbart_id)
mjones_nodes = agg_nodes_run(mjones_id)

# put together
breitbart_nodes['platform'] = 'breitbart'
mjones_nodes['platform'] = 'mjones'
df_nodes_agg = pd.concat([breitbart_nodes, mjones_nodes])

platform_palette = {
    'breitbart': 'tab:blue',
    'mjones': 'tab:orange'
}

plt.figure(figsize=(6, 4))

# Loop over each user
for _, row in df_nodes_agg.groupby('user_id'):
    platform = row['platform'].iloc[0]
    sns.kdeplot(
        row['count'], 
        color=platform_palette.get(platform, 'gray'), 
        linewidth=1, 
        alpha=0.7,
        label=platform if platform not in plt.gca().get_legend_handles_labels()[1] else None
    )

plt.title('KDE per User, Colored by Platform')
plt.xlabel('Count')
plt.ylabel('Density')
plt.legend(title='Platform')
plt.tight_layout()
plt.show()

# actually this is basically all we need to know
# it is extremely sparse because we have n=60 topics
# and we have n=500 posts and we classify on average around n=2 topics
# so very few of these topics have more than around n=20 observations
# this makes it *very* difficult for us to say something I'm afraid.
sns.histplot(df_nodes_agg, x='count')

### topics over time ### 
# just look at one individual 
path = os.path.join('data', breitbart_id)
files = os.listdir(path)    
f = files[0]
df = pd.read_csv(os.path.join(path, f))

# curate
df['value'] = df['stance'].map({"AGAINST": -1, "FAVOR": 1})
df['comment_date'] = pd.to_datetime(df['comment_date'])

# select top n targets & group/average
n = 10
top_targets = df['target'].value_counts().nlargest(n).index 
subset = df[df['target'].isin(top_targets)]
subset['time_slice'] = subset['comment_date'].dt.to_period('Y').dt.to_timestamp()
#grouped = subset.groupby(['time_slice', 'target'])['value'].mean().reset_index()

# plot (top 10 topics for one user).
plt.figure(figsize=(8, 5))
sns.lineplot(data=subset, x='time_slice', y='value', hue='target', marker='o', ci='sd')
plt.title(f'Average Value Over Time for Top {n} Targets')
plt.xlabel('Time')
plt.ylabel('Average Value')
plt.xticks(rotation=45)
plt.legend(title='Target', bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend
plt.tight_layout()
plt.show()