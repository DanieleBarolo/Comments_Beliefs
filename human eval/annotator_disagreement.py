import pandas as pd
import numpy as np
import os

def create_disagreement_documentation(round_number):
    """
    Create documentation for annotator disagreement discussions
    
    Parameters:
    round_number (int): Which round of discussions (1, 2, or 3)
    """
    # Define the annotator pairs for each round
    if round_number == 1:
        pairs = [(1, 2), (3, 4)]
    elif round_number == 2:
        pairs = [(1, 3), (2, 4)]
    elif round_number == 3:
        pairs = [(1, 4), (2, 3)]
    else:
        print("Invalid round number. Please use 1, 2, or 3.")
        return
    
    print(f"Preparing documentation for Round {round_number}")
    print(f"Annotator pairs: {pairs}")
    
    # Step 1: Load the master assignments and results
    master_df = pd.read_csv("comment_assignments_master.csv")
    
    # Load results from all annotators
    results = {}
    for i in range(1, 5):
        path = "test_gold_data"
        results[i] = pd.read_excel(f"{path}/insert_data_annotator_{i}.xlsx")
        print(f"Loaded data from annotator {i}: {len(results[i])} rows")
    
    # Step 2: Create a directory for this round
    round_dir = f"round_{round_number}_disagreements"
    os.makedirs(round_dir, exist_ok=True)
    
    # Also create subdirectories for each pair
    for pair in pairs:
        pair_dir = f"{round_dir}/pair_{pair[0]}_{pair[1]}"
        os.makedirs(pair_dir, exist_ok=True)
    
    # Step 3: Process each pair and collect results for analysis
    pair_results = {}
    for pair in pairs:
        a1, a2 = pair
        pair_results[pair] = process_annotator_pair(a1, a2, master_df, results, round_dir)
    
    # Step 4: Generate an overall analysis for this round
    # At the end of create_disagreement_documentation, add:
    analysis_results = analyze_annotation_agreement(pair_results, round_number, round_dir)
    print(f"\nDocumentation for Round {round_number} completed!")
    print(f"Files created in directory: {round_dir}")

    return analysis_results


def process_annotator_pair(annotator1, annotator2, master_df, results, round_dir):
    """
    Process a pair of annotators and create documentation for their disagreements
    """
    # Get the rows assigned to this pair
    pair_rows = master_df[
        ((master_df['annotator_1'] == annotator1) & (master_df['annotator_2'] == annotator2)) |
        ((master_df['annotator_1'] == annotator2) & (master_df['annotator_2'] == annotator1))
    ]
    
    # Get the results from both annotators
    results1 = results[annotator1]
    results2 = results[annotator2]
    
    # Create a directory for this pair
    pair_dir = f"{round_dir}/pair_{annotator1}_{annotator2}"
    os.makedirs(pair_dir, exist_ok=True)
    
    # Create lists to store comparison data
    comparison_data = []
    
    # Store detailed disagreement information for analysis
    detailed_disagreements = []
    
    # Counter for disagreements
    disagreement_count = 0
    
    # Process each assigned comment
    for _, row in pair_rows.iterrows():
        comment_id = row['comment_id']
        provider_name = row['provider_name']
        article_id = row['article_id']
        
        # Find this comment in both annotators' results
        comment1 = results1[results1['comment_id'] == comment_id]
        comment2 = results2[results2['comment_id'] == comment_id]
        
        # Skip if either annotator doesn't have this comment
        if comment1.empty or comment2.empty:
            continue
        
        # Extract the first (and hopefully only) matching row
        comment1 = comment1.iloc[0]
        comment2 = comment2.iloc[0]
        
        # Identify columns that are different between the two annotators
        # Skip the administrative columns 
        skip_columns = ['comment_id', 'article_id', 'user_id', 'provider_name', 'COMPLETED']
        
        # Find columns that both dataframes have
        common_cols = [col for col in results1.columns if col in results2.columns 
                      and col not in skip_columns]
        
        # Check for disagreements in annotation fields
        disagreements = {}
        has_disagreement = False
        
        # Create a row for this comment
        comparison_row = {
            'comment_id': comment_id,
            'provider_name': provider_name,
            'article_id': article_id
        }
        
        # Add all columns from both annotators
        for col in common_cols:
            # Add original values for both annotators (will be used to create simplified view)
            comparison_row[f'{col}_annotator_{annotator1}'] = comment1[col]
            comparison_row[f'{col}_annotator_{annotator2}'] = comment2[col]
            
            # Check if there's a disagreement
            # Skip if both values are NaN
            if pd.isna(comment1[col]) and pd.isna(comment2[col]):
                continue
                
            # Check if values are different
            if comment1[col] != comment2[col] or (pd.isna(comment1[col]) != pd.isna(comment2[col])):
                disagreements[col] = {
                    f'annotator_{annotator1}': comment1[col],
                    f'annotator_{annotator2}': comment2[col]
                }
                has_disagreement = True
        
        # Add the row to our comparison data
        comparison_data.append(comparison_row)
        
        # If there are disagreements, create a text file and store disagreement info
        if has_disagreement:
            disagreement_count += 1
            
            # Store detailed disagreement info for analysis
            disagreement_info = {
                'comment_id': comment_id,
                'provider_name': provider_name,
                'article_id': article_id,
                'fields': list(disagreements.keys()),
                'values': disagreements
            }
            detailed_disagreements.append(disagreement_info)
            
            # Create a text file for this comment, organized by provider/article
            create_comment_text_file(
                comment_id, 
                provider_name, 
                article_id,
                disagreements,
                annotator1,
                annotator2,
                pair_dir
            )
    
    # Create a disagreement Excel file
    if comparison_data:
        # Convert to DataFrame
        comparison_df = pd.DataFrame(comparison_data)
        
        # Save to Excel with simplified format
        excel_path = f"{pair_dir}/annotations_{annotator1}_{annotator2}.xlsx"
        create_formatted_excel(comparison_df, excel_path, annotator1, annotator2)
        
        print(f"Found {disagreement_count} disagreements between annotators {annotator1} and {annotator2}")
        print(f"Created Excel file: {excel_path}")
    else:
        print(f"No comments found for annotators {annotator1} and {annotator2}")
    
    # Return data about this pair for overall analysis
    return {
        'df': pd.DataFrame(comparison_data) if comparison_data else pd.DataFrame(),
        'disagreements': detailed_disagreements,
        'disagreement_count': disagreement_count
    }

def create_comment_text_file(comment_id, provider_name, article_id, disagreements, 
                            annotator1, annotator2, pair_dir):
    """
    Create a text file containing the comment text and disagreement information,
    organized by provider/article directory structure
    """
    # Create provider and article subdirectories
    provider_dir = os.path.join(pair_dir, provider_name.lower())
    os.makedirs(provider_dir, exist_ok=True)
    
    # Try to find the original comment text
    comment_text = ""
    comment_path = find_comment_file(comment_id, provider_name, article_id)
    
    if comment_path:
        # Read the comment text
        try:
            with open(comment_path, 'r', encoding='utf-8') as f:
                comment_text = f.read()
        except Exception as e:
            comment_text = f"[Error reading comment text: {e}]"
    else:
        comment_text = "[Comment text file not found]"
    
    # Create the output file in the article directory
    output_path = os.path.join(provider_dir, f"{comment_id}.txt")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("DISAGREEMENTS:\n")
        f.write("=" * 50 + "\n")
        
        for field, values in disagreements.items():
            f.write(f"\nField: {field}\n")
            f.write(f"  Annotator {annotator1}: {values[f'annotator_{annotator1}']}\n")
            f.write(f"  Annotator {annotator2}: {values[f'annotator_{annotator2}']}\n")

        f.write("\nCOMMENT TEXT:\n")
        f.write("=" * 50 + "\n")
        f.write(comment_text)
        f.write("\n\n")
    
    print(f"Created disagreement file: {output_path}")

def find_comment_file(comment_id, provider_name, article_id):
    """
    Find the file containing the comment text based on the actual directory structure
    """
    # The comment text files are in annotation_files/annotator_X/provider_name/comment_id.txt
    
    # Try to find the file in any of the annotator folders (prioritizing the current annotators)
    for annotator_num in range(1, 5):
        path = f"annotation_files/annotator_{annotator_num}/{provider_name.lower()}/{article_id}/{comment_id}.txt"
        if os.path.exists(path):
            return path
    
    # Last resort: search for any file with this comment ID
    try:
        for root, dirs, files in os.walk("annotation_files"):
            for file in files:
                # Check if the filename starts with the comment ID (either exactly or with underscore)
                if (file == f"{comment_id}.txt" or 
                    file == f"{comment_id}_context.txt" or
                    file.startswith(f"{comment_id}_")):
                    return os.path.join(root, file)
    except Exception as e:
        print(f"Error searching for comment file: {e}")
    
    return None

def create_formatted_excel(df, output_path, annotator1, annotator2):
    """
    Create a simplified Excel file with a single column per annotation field
    showing agreement or disagreement, sorted by provider name and comment_id
    """
    # Create a new DataFrame for the simplified output
    simplified_df = pd.DataFrame()
    
    # Add only the comment_id and provider_name columns (removing article_id)
    simplified_df['comment_id'] = df['comment_id']
    simplified_df['provider_name'] = df['provider_name']
    
    # Get all the annotation columns (excluding identifiers and disagreement flags)
    annotation_fields_ordered = []
    for col in df.columns:
        if f'_annotator_{annotator1}' in col:
            field_name = col.replace(f'_annotator_{annotator1}', '')
            if field_name not in annotation_fields_ordered and field_name not in ['comment_id', 'provider_name', 'article_id']:
                annotation_fields_ordered.append(field_name)
    
    # Process each annotation field
    for field in annotation_fields_ordered:
        col1 = f'{field}_annotator_{annotator1}'
        col2 = f'{field}_annotator_{annotator2}'
        
        # Create a new column with a simplified name
        simplified_df[field] = None
        
        # For each row, determine if there's agreement or disagreement
        for i, row in df.iterrows():
            value1 = row[col1]
            value2 = row[col2]
            
            # If both values are NaN, use NaN
            if pd.isna(value1) and pd.isna(value2):
                simplified_df.at[i, field] = np.nan
            # If values are equal, use that value
            elif value1 == value2:
                simplified_df.at[i, field] = value1
            # If values are different, mark as DISAGREEMENT
            else:
                simplified_df.at[i, field] = "DISAGREEMENT"
    
    # Create a custom provider order (motherjones first, then thehill, then breitbart)
    provider_order = {
        'motherjones': 0,
        'thehill': 1,
        'breitbart': 2
    }
    
    # Add a temporary column for sorting by provider
    simplified_df['provider_order'] = simplified_df['provider_name'].str.lower().map(provider_order)
    
    # Sort the DataFrame by provider order first, then by comment_id
    simplified_df = simplified_df.sort_values(['provider_order', 'comment_id'])
    
    # Remove the temporary column
    simplified_df = simplified_df.drop('provider_order', axis=1)
    
    # Save to Excel without conditional formatting
    simplified_df.to_excel(output_path, sheet_name='Annotations', index=False)
    
    print(f"Created simplified Excel file: {output_path}")
    return simplified_df

def analyze_annotation_agreement(all_pairs_data, round_number, round_dir):
    """
    Generate an overall analysis of annotation agreement and create a summary report
    
    Parameters:
    all_pairs_data (dict): Dictionary containing data for each annotator pair
    round_number (int): The current round number
    round_dir (str): Directory where the round data is stored
    """
    # Create a report file path
    report_path = os.path.join(round_dir, f"round_{round_number}_agreement_analysis.txt")
    
    # Initialize overall statistics
    total_comments = 0
    total_disagreements = 0
    comments_with_any_disagreement = 0
    
    # Track statistics by provider and annotator
    provider_stats = {}
    annotator_stats = {}
    field_stats = {}
    article_stats = {}
    
    # Process each pair's data
    for pair, pair_data in all_pairs_data.items():
        annotator1, annotator2 = pair
        
        # Initialize annotator stats if not already present
        for annotator in [annotator1, annotator2]:
            if annotator not in annotator_stats:
                annotator_stats[annotator] = {
                    'total_comments': 0,
                    'disagreements': 0,
                    'agreement_rate': 0
                }
        
        # Get the dataframe with all comments for this pair
        df = pair_data['df']
        total_comments += len(df)
        
        # Get the disagreement info
        disagreements = pair_data['disagreements']
        comments_with_disagreements = len(disagreements)
        comments_with_any_disagreement += comments_with_disagreements
        
        # Update annotator stats
        for annotator in [annotator1, annotator2]:
            annotator_stats[annotator]['total_comments'] += len(df)
            annotator_stats[annotator]['disagreements'] += comments_with_disagreements
        
        # Analyze by provider
        for provider, group in df.groupby('provider_name'):
            if provider not in provider_stats:
                provider_stats[provider] = {
                    'total_comments': 0,
                    'comments_with_disagreements': 0,
                    'agreement_rate': 0
                }
            
            # Count comments with any disagreement in this provider group
            provider_disagreements = sum(1 for comment_id in group['comment_id'] 
                                      if comment_id in [d['comment_id'] for d in disagreements])
            
            provider_stats[provider]['total_comments'] += len(group)
            provider_stats[provider]['comments_with_disagreements'] += provider_disagreements
        
        # Analyze by article
        for article_id, group in df.groupby('article_id'):
            article_key = f"{group['provider_name'].iloc[0]}_article_{article_id}"
            
            if article_key not in article_stats:
                article_stats[article_key] = {
                    'total_comments': 0,
                    'comments_with_disagreements': 0,
                    'agreement_rate': 0
                }
            
            # Count comments with any disagreement in this article group
            article_disagreements = sum(1 for comment_id in group['comment_id'] 
                                     if comment_id in [d['comment_id'] for d in disagreements])
            
            article_stats[article_key]['total_comments'] += len(group)
            article_stats[article_key]['comments_with_disagreements'] += article_disagreements
        
        # Analyze by field
        for disagreement in disagreements:
            for field in disagreement['fields']:
                if field not in field_stats:
                    field_stats[field] = {
                        'total_disagreements': 0,
                        'value_pairs': {}
                    }
                
                field_stats[field]['total_disagreements'] += 1
                
                # Track specific disagreements (e.g., "I+" vs "E+")
                value1 = disagreement['values'][field][f'annotator_{annotator1}']
                value2 = disagreement['values'][field][f'annotator_{annotator2}']
                
                if pd.isna(value1):
                    value1 = "NaN"
                if pd.isna(value2):
                    value2 = "NaN"
                
                value_pair = f"{value1} vs {value2}"
                if value_pair not in field_stats[field]['value_pairs']:
                    field_stats[field]['value_pairs'][value_pair] = 0
                
                field_stats[field]['value_pairs'][value_pair] += 1
    
    # Calculate overall agreement rate
    if total_comments > 0:
        overall_agreement_rate = 100 * (1 - comments_with_any_disagreement / total_comments)
    else:
        overall_agreement_rate = 0
    
    # Calculate provider agreement rates
    for provider in provider_stats:
        if provider_stats[provider]['total_comments'] > 0:
            provider_stats[provider]['agreement_rate'] = 100 * (1 - 
                provider_stats[provider]['comments_with_disagreements'] / 
                provider_stats[provider]['total_comments'])
    
    # Calculate annotator agreement rates
    for annotator in annotator_stats:
        if annotator_stats[annotator]['total_comments'] > 0:
            annotator_stats[annotator]['agreement_rate'] = 100 * (1 - 
                annotator_stats[annotator]['disagreements'] / 
                annotator_stats[annotator]['total_comments'])
    
    # Calculate article agreement rates
    for article in article_stats:
        if article_stats[article]['total_comments'] > 0:
            article_stats[article]['agreement_rate'] = 100 * (1 - 
                article_stats[article]['comments_with_disagreements'] / 
                article_stats[article]['total_comments'])
    
    # Generate the report
    with open(report_path, 'w') as f:
        f.write(f"ANNOTATION AGREEMENT ANALYSIS - ROUND {round_number}\n")
        f.write("=" * 50 + "\n\n")
        
        # Overall statistics
        f.write("OVERALL STATISTICS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total comments reviewed: {total_comments}\n")
        f.write(f"Comments with at least one disagreement: {comments_with_any_disagreement}\n")
        f.write(f"Overall agreement rate: {overall_agreement_rate:.2f}%\n\n")
        
        # Provider statistics
        f.write("AGREEMENT BY PROVIDER\n")
        f.write("-" * 30 + "\n")
        for provider, stats in sorted(provider_stats.items(), 
                                     key=lambda x: x[1]['agreement_rate'], reverse=True):
            f.write(f"{provider}:\n")
            f.write(f"  - Total comments: {stats['total_comments']}\n")
            f.write(f"  - Comments with disagreements: {stats['comments_with_disagreements']}\n")
            f.write(f"  - Agreement rate: {stats['agreement_rate']:.2f}%\n\n")
        
        # Annotator statistics
        f.write("ANNOTATOR PERFORMANCE\n")
        f.write("-" * 30 + "\n")
        for annotator, stats in sorted(annotator_stats.items(), 
                                      key=lambda x: x[1]['agreement_rate'], reverse=True):
            f.write(f"Annotator {annotator}:\n")
            f.write(f"  - Total comments annotated: {stats['total_comments']}\n")
            f.write(f"  - Comments with disagreements: {stats['disagreements']}\n")
            f.write(f"  - Agreement rate: {stats['agreement_rate']:.2f}%\n\n")
        
        # Difficult articles
        f.write("MOST DIFFICULT ARTICLES\n")
        f.write("-" * 30 + "\n")
        # Only show articles with enough comments to be statistically relevant
        relevant_articles = {k: v for k, v in article_stats.items() if v['total_comments'] >= 5}
        for article, stats in sorted(relevant_articles.items(), 
                                    key=lambda x: x[1]['agreement_rate'])[:10]:  # Top 10 most difficult
            f.write(f"{article}:\n")
            f.write(f"  - Total comments: {stats['total_comments']}\n")
            f.write(f"  - Comments with disagreements: {stats['comments_with_disagreements']}\n")
            f.write(f"  - Agreement rate: {stats['agreement_rate']:.2f}%\n\n")
        
        # Field disagreement analysis
        f.write("DISAGREEMENT BY FIELD\n")
        f.write("-" * 30 + "\n")
        for field, stats in sorted(field_stats.items(), 
                                  key=lambda x: x[1]['total_disagreements'], reverse=True):
            f.write(f"{field}:\n")
            f.write(f"  - Total disagreements: {stats['total_disagreements']}\n")
            f.write("  - Common disagreement patterns:\n")
            
            # Sort value pairs by frequency
            sorted_pairs = sorted(stats['value_pairs'].items(), 
                                 key=lambda x: x[1], reverse=True)
            
            # Show top 5 most common disagreement types
            for pair, count in sorted_pairs[:5]:
                f.write(f"    * {pair}: {count} occurrences\n")
            
            f.write("\n")
        
        # Add analysis of similar disagreements
        f.write("ANALYSIS OF SIMILAR DISAGREEMENTS\n")
        f.write("-" * 30 + "\n")
        f.write("Common patterns in the disagreements:\n")
        
        # Look for similar disagreements (e.g., I+ vs E+)
        similar_disagreements = {}
        for field, stats in field_stats.items():
            for value_pair, count in stats['value_pairs'].items():
                values = value_pair.split(" vs ")
                # Check if both values contain a common character (like "+")
                if len(values) == 2:
                    v1, v2 = values
                    # Look for similar values (both containing same character)
                    for char in ["+", "-", "I", "E"]:
                        if char in str(v1) and char in str(v2):
                            key = f"Both contain '{char}'"
                            if key not in similar_disagreements:
                                similar_disagreements[key] = {
                                    'count': 0,
                                    'examples': []
                                }
                            similar_disagreements[key]['count'] += count
                            if len(similar_disagreements[key]['examples']) < 3:  # Limit examples
                                similar_disagreements[key]['examples'].append(f"{field}: {value_pair}")
        
        # Report similar disagreements
        for pattern, info in sorted(similar_disagreements.items(), 
                                   key=lambda x: x[1]['count'], reverse=True):
            f.write(f"\n* {pattern}: {info['count']} occurrences\n")
            f.write("  Examples:\n")
            for example in info['examples']:
                f.write(f"    - {example}\n")
    
    print(f"Agreement analysis report created: {report_path}")
    return {
        'overall_agreement_rate': overall_agreement_rate,
        'provider_stats': provider_stats,
        'annotator_stats': annotator_stats,
        'field_stats': field_stats,
        'article_stats': article_stats
    }

def create_unified_report(all_rounds_results):
    """
    Create a unified report using data from all rounds
    """
    # Create a report file
    with open("unified_annotation_analysis.txt", "w") as f:
        f.write("UNIFIED ANNOTATION AGREEMENT ANALYSIS\n")
        f.write("=" * 50 + "\n\n")
        
        # Compare results across rounds
        f.write("AGREEMENT RATES BY ROUND\n")
        f.write("-" * 30 + "\n")
        for round_num, results in sorted(all_rounds_results.items()):
            f.write(f"Round {round_num}: {results['overall_agreement_rate']:.2f}%\n")
        f.write("\n")
        
        # Calculate average agreement rate across all rounds
        avg_agreement = sum(r['overall_agreement_rate'] for r in all_rounds_results.values()) / len(all_rounds_results)
        f.write(f"Average agreement rate across all rounds: {avg_agreement:.2f}%\n\n")
        
        # Provider analysis across rounds
        f.write("PROVIDER AGREEMENT RATES ACROSS ROUNDS\n")
        f.write("-" * 30 + "\n")
        
        # Collect all providers
        all_providers = set()
        for results in all_rounds_results.values():
            all_providers.update(results['provider_stats'].keys())
        
        # Create table header
        f.write(f"{'Provider':<15}")
        for round_num in sorted(all_rounds_results.keys()):
            f.write(f"Round {round_num:<5}")
        f.write("Average\n")
        f.write("-" * 50 + "\n")
        
        # Add provider data
        provider_avg_rates = {}
        for provider in sorted(all_providers):
            f.write(f"{provider:<15}")
            provider_rates = []
            
            for round_num in sorted(all_rounds_results.keys()):
                results = all_rounds_results[round_num]
                if provider in results['provider_stats']:
                    rate = results['provider_stats'][provider]['agreement_rate']
                    provider_rates.append(rate)
                    f.write(f"{rate:8.2f}%")
                else:
                    f.write(f"{'N/A':>8}")
            
            # Calculate average for this provider
            if provider_rates:
                avg_rate = sum(provider_rates) / len(provider_rates)
                provider_avg_rates[provider] = avg_rate
                f.write(f"{avg_rate:8.2f}%\n")
            else:
                f.write(f"{'N/A':>8}\n")
        
        # Rank providers by agreement rate
        f.write("\nPROVIDERS RANKED BY AVERAGE AGREEMENT RATE\n")
        f.write("-" * 30 + "\n")
        for provider, rate in sorted(provider_avg_rates.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{provider:<15}: {rate:.2f}%\n")
        f.write("\n")
        
        # Annotator analysis across rounds
        f.write("ANNOTATOR AGREEMENT RATES ACROSS ROUNDS\n")
        f.write("-" * 30 + "\n")
        
        # Collect all annotators
        all_annotators = set()
        for results in all_rounds_results.values():
            all_annotators.update(results['annotator_stats'].keys())
        
        # Create table header
        f.write(f"{'Annotator':<10}")
        for round_num in sorted(all_rounds_results.keys()):
            f.write(f"Round {round_num:<5}")
        f.write("Average\n")
        f.write("-" * 50 + "\n")
        
        # Add annotator data
        annotator_avg_rates = {}
        for annotator in sorted(all_annotators):
            f.write(f"Annotator {annotator:<2}")
            annotator_rates = []
            
            for round_num in sorted(all_rounds_results.keys()):
                results = all_rounds_results[round_num]
                if annotator in results['annotator_stats']:
                    rate = results['annotator_stats'][annotator]['agreement_rate']
                    annotator_rates.append(rate)
                    f.write(f"{rate:8.2f}%")
                else:
                    f.write(f"{'N/A':>8}")
            
            # Calculate average for this annotator
            if annotator_rates:
                avg_rate = sum(annotator_rates) / len(annotator_rates)
                annotator_avg_rates[annotator] = avg_rate
                f.write(f"{avg_rate:8.2f}%\n")
            else:
                f.write(f"{'N/A':>8}\n")
        
        # Similar disagreement analysis across all rounds
        f.write("ANALYSIS OF SIMILAR DISAGREEMENTS\n")
        f.write("-" * 30 + "\n")
        f.write("Common patterns in the disagreements:\n\n")
        
        # Collect patterns of similar disagreements (e.g., both values contain "+")
        similar_patterns = {}
        for results in all_rounds_results.values():
            for field, stats in results['field_stats'].items():
                # Skip the Notes field
                if field == "Notes":
                    continue
                    
                for value_pair, count in stats['value_pairs'].items():
                    values = value_pair.split(" vs ")
                    if len(values) == 2:
                        v1, v2 = values
                        # Look for similar patterns
                        for char in ["+", "-", "I", "E"]:
                            if char in str(v1) and char in str(v2):
                                key = f"Both contain '{char}'"
                                if key not in similar_patterns:
                                    similar_patterns[key] = {
                                        'count': 0,
                                        'examples': []
                                    }
                                similar_patterns[key]['count'] += count
                                if len(similar_patterns[key]['examples']) < 5:  # Limit examples
                                    example = f"{field}: {value_pair}"
                                    if example not in similar_patterns[key]['examples']:
                                        similar_patterns[key]['examples'].append(example)
        
        # Report similar disagreements
        for pattern, info in sorted(similar_patterns.items(), key=lambda x: x[1]['count'], reverse=True):
            f.write(f"* {pattern}: {info['count']} occurrences\n")
            f.write("  Examples:\n")
            for example in info['examples']:
                f.write(f"    - {example}\n")
            f.write("\n")
        
        # Field analysis across rounds
        f.write("DISAGREEMENT BY FIELD\n")
        f.write("-" * 30 + "\n")
        
        # Collect all fields and count disagreements
        all_fields = {}
        for results in all_rounds_results.values():
            for field, stats in results['field_stats'].items():
                # Skip the Notes field
                if field == "Notes":
                    continue
                    
                if field not in all_fields:
                    all_fields[field] = {
                        'total_disagreements': 0,
                        'rounds_with_disagreements': 0,
                        'common_patterns': {}
                    }
                
                all_fields[field]['total_disagreements'] += stats['total_disagreements']
                all_fields[field]['rounds_with_disagreements'] += 1
                
                # Collect common disagreement patterns
                for pair, count in stats['value_pairs'].items():
                    if pair not in all_fields[field]['common_patterns']:
                        all_fields[field]['common_patterns'][pair] = 0
                    all_fields[field]['common_patterns'][pair] += count
        
        # Sort fields by total disagreements
        for field, stats in sorted(all_fields.items(), key=lambda x: x[1]['total_disagreements'], reverse=True):
            f.write(f"{field}:\n")
            f.write(f"  - Total disagreements across all rounds: {stats['total_disagreements']}\n")
            f.write(f"  - Appeared in {stats['rounds_with_disagreements']} round(s)\n")
            f.write("  - Common disagreement patterns:\n")
            
            # Show top 5 most common patterns
            for pair, count in sorted(stats['common_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
                f.write(f"    * {pair}: {count} occurrences\n")
            
            f.write("\n")
    
    print(f"Unified analysis report created: unified_annotation_analysis.txt")


# Function to run all three rounds
def create_all_rounds():
    """
    Create disagreement documentation for all three rounds and a unified report
    """
    all_rounds_results = {}
    
    for round_num in range(1, 4):
        all_rounds_results[round_num] = create_disagreement_documentation(round_num)
    
    # Create a unified report using data from all rounds
    create_unified_report(all_rounds_results)

# Main function
if __name__ == "__main__":
    create_all_rounds()