import pandas as pd 
import os 
import re
from utility import aggregate_nodes, compute_edges, aggregate_edges
import seaborn as sns 
import matplotlib.pyplot as plt 
from statsmodels.distributions.empirical_distribution import ECDF
from itertools import combinations
import numpy as np 
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

    # plot (top 10 topics for one user).
    plt.figure(figsize=(8, 5))
    sns.lineplot(
        data=subset,
        x='time_slice', 
        y='value', 
        hue='target', 
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

## breitbart
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

## mother jones
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
    
## breitbart 5k 
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

'''CORRELATIONS'''
def compute_pairwise_correlations(df_edges):
    # Group by (source, target)
    grouped = df_edges.groupby(['source', 'target'])

    # Compute correlation for each group
    correlation_data = []
    for (source, target), group in grouped:
        if len(group) > 1:
            corr = group['source_spin'].corr(group['target_spin'])
        else:
            corr = None  # Not enough data to compute correlation

        correlation_data.append({
            'source': source,
            'target': target,
            'correlation': corr,
            'count': len(group)  # Optional: to know how many times this pair occurred
        })

    df_corr = pd.DataFrame(correlation_data)
    return df_corr

def compute_pairwise_correlations_platform(df_edges):
    # Group by (source, target)
    grouped = df_edges.groupby(['source', 'target', 'platform'])

    # Compute correlation for each group
    correlation_data = []
    for (source, target, platform), group in grouped:
        if len(group) > 1:
            corr = group['source_spin'].corr(group['target_spin'])
        else:
            corr = None  # Not enough data to compute correlation

        correlation_data.append({
            'source': source,
            'target': target,
            'platform': platform,
            'correlation': corr,
            'count': len(group)  # Optional: to know how many times this pair occurred
        })

    df_corr = pd.DataFrame(correlation_data)
    return df_corr

# this needs to take the list of topics
def create_full_pairwise_matrix(df_edges):
    # Step 1: Get all unique targets
    unique_targets = pd.concat([df_edges['source'], df_edges['target']]).unique()

    # Step 2: Generate all unordered target pairs
    all_pairs = list(combinations(sorted(unique_targets), 2))
    df_all_pairs = pd.DataFrame(all_pairs, columns=['source', 'target'])

    # Step 3: Compute observed correlations
    df_corr_observed = compute_pairwise_correlations(df_edges)

    # Step 4: Merge with full list of pairs
    df_corr_full = pd.merge(df_all_pairs, df_corr_observed, on=['source', 'target'], how='left')

    # Step 5: Fill missing counts with 0 (leave correlation as NaN to indicate no data)
    df_corr_full['count'] = df_corr_full['count'].fillna(0).astype(int)

    return df_corr_full

def get_short_id(file_path):
    for run_id in run_id_map:
        if run_id in file_path:
            return run_id_map[run_id]
    return None

# setup 
run_id_map = {
    '20250422_CT_DS70B_002': 'B5k',
    '20250411_CT_DS70B_005': 'MJ',
    '20250409_CT_DS70B_002': 'BB'
}
paths = [f'data/{run_id}' for run_id in run_id_map.keys()]
files = [os.path.join(path, file) for path in paths for file in os.listdir(path)]

corr_list = []
data_list = []
for f in files: 

    df = pd.read_csv(f)
    df_edges = compute_edges(df) 
    corr_edges = create_full_pairwise_matrix(df_edges)

    # take out actual correlations # 
    corr_edges_notna = corr_edges.dropna()
    corr_edges_notna['platform'] = get_short_id(f)
    data_list.append(corr_edges_notna)

# plot correlations 
df_corr = pd.concat(data_list)
fig, ax = plt.subplots(figsize=(4, 3))
sns.kdeplot(
    data = df_corr,
    x = 'correlation',
    hue = 'platform',
    clip=(-1, 1)
)
plt.tight_layout()
plt.savefig('fig/exploratory/corr_kde.png', dpi=300)

### population-level correlations ###
data_list = []
for f in files: 
    df = pd.read_csv(f)
    df_edges = compute_edges(df)
    df_edges['platform'] = get_short_id(f)
    data_list.append(df_edges)
df_corr_pop = pd.concat(data_list)
df_corr = compute_pairwise_correlations_platform(df_corr_pop)
df_corr = df_corr.dropna()
fig, ax = plt.subplots(figsize=(4, 3))
sns.kdeplot(
    data = df_corr,
    x = 'correlation',
    hue = 'platform',
    clip=(-1, 1)
)
plt.tight_layout()
plt.savefig('fig/exploratory/corr_kde_pop.png', dpi=300)

### straight up co-occurence ###
counts = (
    df_corr_pop.groupby('platform')[['source_spin', 'target_spin']]
    .value_counts()
    .unstack(fill_value=0)
)
counts_reset = counts.reset_index()

platforms = counts_reset['platform'].unique()
fig, axes = plt.subplots(1, len(platforms), figsize=(6, 3), sharey=True)

for ax, platform in zip(axes, platforms):
    sub_df = counts_reset[counts_reset['platform'] == platform]
    pivot = sub_df.set_index('source_spin')[[ -1, 1 ]]  # Select target_spin columns explicitly
    sns.heatmap(pivot, annot=True, fmt='g', cmap='Blues', ax=ax, cbar=False)
    ax.set_title(f'Platform: {platform}')
    ax.set_ylabel('source_spin')
    ax.set_xlabel('target_spin')

plt.tight_layout()
plt.savefig('fig/exploratory/cooccurence.png', dpi=300)

'''SEMANTICS'''
def normalize_freq(df):
    user_total_counts = df.groupby('user_id')['count'].transform('sum')
    df['normalized_frequency'] = df['count'] / user_total_counts
    return df 

def avg_frequency(df):
    df_avg = df.groupby('target')['normalized_frequency'].mean().reset_index()
    df_avg = df_avg.sort_values(by='normalized_frequency', ascending=False)
    return df_avg 

def plot_dumbbell(df, outname=False, mj_col='mj_freq', bb_col='bb_freq', label_col='target', xlabel='Normalized Frequency'):
    # Sort by one column to have a clean y-axis
    df_sorted = df.sort_values(by=mj_col)

    y_positions = range(len(df_sorted))

    plt.figure(figsize=(6, len(df_sorted) * 0.3))  # Adjust height based on number of targets

    # Plot lines between points
    for i, row in enumerate(df_sorted.itertuples()):
        plt.plot(
            [getattr(row, mj_col), getattr(row, bb_col)],
            [i, i],
            color='gray',
            linewidth=1,
            alpha=0.6
        )

    # Plot points
    plt.scatter(df_sorted[mj_col], y_positions, color='tab:blue', label='mj')
    plt.scatter(df_sorted[bb_col], y_positions, color='tab:orange', label='bb')

    # Set y-ticks and labels
    plt.yticks(y_positions, df_sorted[label_col])
    plt.xlabel(xlabel)
    plt.title('Comparison of Target Frequencies: mj vs bb')
    plt.legend()
    plt.tight_layout()
    if outname: 
        plt.savefig(f'fig/exploratory/{outname}.png', dpi=300)
        plt.close()
    else: 
        plt.show()    

## 1. what are users talk about ## 
breitbart_normalized = normalize_freq(breitbart_nodes)
breitbart_avg = avg_frequency(breitbart_normalized)

mjones_normalized = normalize_freq(mjones_nodes)
mjones_avg = avg_frequency(mjones_normalized)

b5k_normalized = normalize_freq(b5k_nodes)
b5k_avg = avg_frequency(b5k_normalized)

# compare breitbart to mother jones
# not doing b5k here
breitbart_avg = breitbart_avg.rename(columns={
    'normalized_frequency': 'bb_freq',
})
mjones_avg = mjones_avg.rename(columns={
    'normalized_frequency': 'mj_freq'
})
node_freq = mjones_avg.merge(
    breitbart_avg,
    on = 'target')
node_freq['delta'] = node_freq['mj_freq']-node_freq['bb_freq']

# find the targets where they differ most
node_freq['delta_abs'] = node_freq['delta'].abs()
node_freq = node_freq.sort_values('delta_abs', ascending=False)
node_freq_delta = node_freq.head(15)
node_freq_delta = node_freq_delta.sort_values('bb_freq')

plot_dumbbell(
    node_freq_delta,
    'dumbbell_frequency'
    )

## 2. where do users disagree ##
bb_spins = breitbart_nodes.groupby('target')['average_direction'].mean().reset_index(name='spin_bb')
mj_spins = mjones_nodes.groupby('target')['average_direction'].mean().reset_index(name='spin_mj')
df_spins = bb_spins.merge(mj_spins, on = 'target')
df_spins['delta'] = df_spins['spin_mj'] - df_spins['spin_bb']
df_spins['delta_abs'] = df_spins['delta'].abs()

# merge with node freq because we have some that are very rare
node_freq_subset = node_freq[['target', 'mj_freq', 'bb_freq']]
df_spins = df_spins.merge(node_freq_subset, on = 'target', how = 'inner')

# only take spins that are relatively common 
median_mj = df_spins['mj_freq'].median()
median_bb = df_spins['bb_freq'].median()

df_spins_subset = df_spins[
    (df_spins['mj_freq'] > median_mj) &
    (df_spins['bb_freq'] > median_bb)
]
len(df_spins_subset) # n=23 out of n=60
df_spins_subset = df_spins_subset.sort_values('spin_mj')

plot_dumbbell(
    df_spins_subset,
    'dumbbell_spin',
    mj_col='spin_mj',
    bb_col='spin_bb',
    xlabel = 'Average Spin'
)

### overall negativity bias? ###

## correlation between frequency and sentiment (by user) ## 
bb_nodes_five = breitbart_normalized[breitbart_normalized['count'] >= 5]
mj_nodes_five = mjones_normalized[mjones_normalized['count'] >= 5]
b5k_nodes_five = b5k_normalized[b5k_normalized['count'] >= 5]

nodes_five_total = pd.concat([bb_nodes_five, mj_nodes_five, b5k_nodes_five])
nodes_five_total = nodes_five_total[['target', 'platform', 'average_direction', 'normalized_frequency']]

sns.lmplot(
    data=nodes_five_total,
    x='average_direction',
    y='normalized_frequency',
    hue='platform',
    height=5,      # controls vertical size
    aspect=1,    # width / height = 5 / 3 (same as figsize=(5,3))
    scatter_kws={'s': 40, 'alpha': 0.7},
    line_kws={'linewidth': 2}
)

plt.xlabel('Average Direction (spin)')
plt.ylabel('Normalized Frequency')
plt.title('User-level negativity bias')
plt.tight_layout()
plt.savefig('fig/exploratory/negativity.png', dpi=300)

### negativity/positive distributions ###
# some deprecation warnings here.
def clean_raincloud(data, outname=False, x='platform', y='average_direction'):
    plt.figure(figsize=(6, 4))

    # Violin (density)
    sns.violinplot(
        data=data,
        x=x,
        y=y,
        inner=None,        # no inner box in violin
        linewidth=1,
        cut=0,
        scale='width',
        bw=0.2,
        palette='pastel'
    )

    # Boxplot
    sns.boxplot(
        data=data,
        x=x,
        y=y,
        width=0.15,
        showcaps=True,
        boxprops={'facecolor':'white', 'edgecolor':'black'},
        whiskerprops={'color':'black'},
        medianprops={'color':'black'},
        flierprops={'marker': 'o', 'markersize': 3}
    )

    # Stripplot (jittered points)
    sns.stripplot(
        data=data,
        x=x,
        y=y,
        color='black',
        size=2,
        jitter=0.2,
        alpha=0.3
    )

    plt.title("Distribution of Average Direction by Platform")
    plt.ylabel("Average Direction (Spin)")
    plt.xlabel("Platform")
    plt.tight_layout()
    if outname: 
        plt.savefig(f'fig/exploratory/{outname}.png', dpi=300)
        plt.close()
    else: 
        plt.show()

clean_raincloud(
    nodes_five_total,
    'violin_sentiment')