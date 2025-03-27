# 1. Normalize the pairs so source-target and target-source are treated the same
df['pair'] = df.apply(lambda row: tuple(sorted([row['source'], row['target']])), axis=1)

# 2. Group by the normalized pair and aggregate
aggregated = df.groupby('pair').agg(
    average_connection=('connection', 'mean'),
    connection_count=('connection', 'count')
).reset_index()

# 3. Optionally split the 'pair' back into two columns
aggregated[['source', 'target']] = pd.DataFrame(aggregated['pair'].tolist(), index=aggregated.index)
aggregated = aggregated.drop(columns='pair')