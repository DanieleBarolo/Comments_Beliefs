import pandas as pd 
import os 
import re
from utility import aggregate_nodes
import seaborn as sns 
import matplotlib.pyplot as plt 
from statsmodels.distributions.empirical_distribution import ECDF
pd.options.mode.chained_assignment = None  # default='warn'

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

### 1. plot distribution (N comments) ### 
breitbart_id = '20250409_CT_DS70B_002' 
mjones_id = '20250411_CT_DS70B_005' 

breitbart_nodes = agg_nodes_run(breitbart_id)
mjones_nodes = agg_nodes_run(mjones_id)

breitbart_nodes['platform'] = 'breitbart'
mjones_nodes['platform'] = 'mjones'

df_nodes_agg = pd.concat([breitbart_nodes, mjones_nodes])

# maybe do something with the 5K nodes
b5k_id = '20250422_CT_DS70B_002'
b5k_nodes = agg_nodes_run(b5k_id)
b5k_nodes['platform'] = '5K'

platform_palette = {
    'breitbart': 'tab:blue',
    'mjones': 'tab:orange',
    '5K': 'tab:green'
}

### plot ECDF ### 
def plot_ECDF(df_nodes, outname, title, legend=False):

    plt.figure(figsize=(6, 4))
    seen_platforms = set()

    for _, row in df_nodes.groupby('user_id'):
        platform = row['platform'].iloc[0]
        color = platform_palette.get(platform, 'gray')
        
        # Only add label the first time we see this platform
        label = platform if platform not in seen_platforms else None
        seen_platforms.add(platform)
        
        ecdf = ECDF(row['count'])
        plt.plot(ecdf.x, ecdf.y, color=color, alpha=0.7, label=label)

    plt.title(title)
    plt.xlabel('Count (N stances on topic)')
    plt.ylabel('(Empirical) Cumulative Probability')
    
    if legend: 
        plt.legend(title='Platform')
    
    plt.tight_layout()
    plt.savefig(f'fig/exploratory/{outname}.png', dpi=300)
    plt.close()

# plot across platforms 
plot_ECDF(
    df_nodes = df_nodes_agg, 
    outname = 'ECDF',
    title = 'ECDF by user (n~500 across platform)',
    legend=True)

# plot 5K users 
plot_ECDF(
    df_nodes = b5k_nodes, 
    outname = 'ECDF_5K',
    title = 'ECDF by user (n~5K Breitbart)',
    legend=False)

### plot topics over time ### 
def plot_topics_time(df, n_topics, outname, show_errorbars=False, n_days=365):

    # curate
    df['value'] = df['stance'].map({"AGAINST": -1, "FAVOR": 1})
    df['time_slice'] = pd.to_datetime(df['time_slice'])

    # select top n targets & group/average
    top_targets = df['target'].value_counts().nlargest(n_topics).index 
    subset = df[df['target'].isin(top_targets)]
    #subset['time_slice'] = subset['comment_date'].dt.to_period(period).dt.to_timestamp()

    # plot (top 10 topics for one user).
    plt.figure(figsize=(8, 5))
    sns.lineplot(
        data=subset,
        x='time_slice', 
        y='value', 
        hue='target', 
        #marker='o', 
        errorbar=('ci', 95) if show_errorbars else None
        )
    plt.title(f'Top {n_topics} targets, {n_days} day window')
    plt.xlabel('Time')
    plt.ylabel('Average Value')
    plt.xticks(rotation=45)
    plt.legend(title='Target', bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend
    plt.tight_layout()
    plt.savefig(f'fig/exploratory/{outname}.png', dpi=300)
    plt.close()

### plot for all users ###
from utility import create_time_windows

path = os.path.join('data', breitbart_id)
files = os.listdir(path)    

for f in files: 
    
    user_id = re.match(r'\d+', f)[0]
    df = pd.read_csv(os.path.join(path, f))
    time_slices = create_time_windows(
        df=df,
        window_size_days=365,
        move_size_days=25,
        return_df = True
    )
    plot_topics_time(
        df = time_slices,
        n_topics=10,
        outname=f'time_BB_{user_id}',
        show_errorbars=True
    )

## one from mother jones
path = os.path.join('data', mjones_id)
files = os.listdir(path)    

for f in files: 
    
    user_id = re.match(r'\d+', f)[0]
    df = pd.read_csv(os.path.join(path, f))
    time_slices = create_time_windows(
        df=df,
        window_size_days=365,
        move_size_days=25,
        return_df = True
    )
    plot_topics_time(
        df = time_slices,
        n_topics=10,
        outname=f'time_MJ_{user_id}',
        show_errorbars=True
    )
    
## big batches
path = os.path.join('data', b5k_id)
files = os.listdir(path)

for f in files: 
    
    user_id = re.match(r'\d+', f)[0]
    df = pd.read_csv(os.path.join(path, f))
    time_slices = create_time_windows(
        df=df,
        window_size_days=365,
        move_size_days=25,
        return_df = True
    )
    plot_topics_time(
        df = time_slices,
        n_topics=10,
        outname=f'time_BB5K_{user_id}',
        show_errorbars=True
    )

## one from large breitbart 
