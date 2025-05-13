import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_interannotator_agreement():
    """
    Streamlined analysis of inter-annotator agreement focusing on three essential metrics:
    1. Topic Selection Agreement (Jaccard Score)
    2. Total Agreement Rate
    3. Stance Direction Agreement (pooled)
    """
    print("Analyzing inter-annotator agreement...")
    
    # Create output directory
    output_dir = "agreement_analysis_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create plots directory
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Load master assignments
    master_df = pd.read_csv("comment_assignments_master.csv")
    print(f"Loaded master assignments: {len(master_df)} comments")
    
    # Load results from all annotators
    results = {}
    for i in range(1, 5):
        path = "test_gold_data"
        results[i] = pd.read_excel(f"{path}/insert_data_annotator_{i}.xlsx")
        print(f"Loaded data from annotator {i}: {len(results[i])} rows")
    
    # Define annotator pairs
    annotator_pairs = [
        (1, 2), (1, 3), (1, 4), 
        (2, 3), (2, 4), 
        (3, 4)
    ]
    
    # Create results storage
    agreement_results = []
    
    # Create matrices for the heatmaps
    topic_selection_matrix = np.zeros((4, 4))
    total_agreement_matrix = np.zeros((4, 4))
    stance_direction_matrix = np.zeros((4, 4))
    
    # Process each annotator pair
    for annotator1, annotator2 in annotator_pairs:
        print(f"\nAnalyzing annotator pair: {annotator1} and {annotator2}")
        
        # Get comments assigned to this pair
        pair_rows = master_df[
            ((master_df['annotator_1'] == annotator1) & (master_df['annotator_2'] == annotator2)) |
            ((master_df['annotator_1'] == annotator2) & (master_df['annotator_2'] == annotator1))
        ]
        
        # Skip if no comments assigned to this pair
        if len(pair_rows) == 0:
            print(f"No comments assigned to annotators {annotator1} and {annotator2}")
            continue
        
        # Get the results from both annotators
        df1 = results[annotator1]
        df2 = results[annotator2]
        
        # Initialize counters
        total_comments = 0
        total_possible_topics = 0
        total_both_annotated = 0
        total_directional_matches = 0
        
        # Per-comment metrics storage
        jaccard_values = []
        total_agreement_values = []
        
        # Lists for detailed analysis
        all_comment_data = []
        
        # Skip administrative columns
        skip_columns = ['comment_id', 'article_id', 'user_id', 'provider_name', 'COMPLETED', 'Notes']
        
        # Process each comment assigned to this pair
        for _, row in pair_rows.iterrows():
            comment_id = row['comment_id']
            provider_name = row.get('provider_name', 'unknown')
            article_id = row.get('article_id', 'unknown')
            
            # Find this comment in both annotators' results
            comment1 = df1[df1['comment_id'] == comment_id]
            comment2 = df2[df2['comment_id'] == comment_id]
            
            # Skip if either annotator doesn't have this comment
            if comment1.empty or comment2.empty:
                continue
            
            # Extract the first matching row
            comment1 = comment1.iloc[0]
            comment2 = comment2.iloc[0]
            
            # Find topic columns (excluding administrative columns)
            topic_columns = [col for col in df1.columns if col not in skip_columns]
            
            total_comments += 1
            total_possible_topics += len(topic_columns)
            
            # Topic count tracking
            topics_marked1 = set()
            topics_marked2 = set()
            topics_both_marked = set()
            topics_both_nan = set()
            directional_matches = 0
            
            # Per-comment data for detailed analysis
            comment_data = {
                'comment_id': comment_id,
                'provider_name': provider_name,
                'article_id': article_id,
                'total_topics': len(topic_columns),
                'annotator1_topics': 0,
                'annotator2_topics': 0,
                'union_topics': 0,
                'intersection_topics': 0,
                'directional_matches': 0
            }
            
            # Process each topic column
            for topic in topic_columns:
                val1 = comment1[topic]
                val2 = comment2[topic]
                
                # Track topics marked by each annotator
                if not pd.isna(val1):
                    topics_marked1.add(topic)
                    comment_data['annotator1_topics'] += 1
                if not pd.isna(val2):
                    topics_marked2.add(topic)
                    comment_data['annotator2_topics'] += 1
                
                # Track topics both marked or both left as NaN
                if not pd.isna(val1) and not pd.isna(val2):
                    topics_both_marked.add(topic)
                    total_both_annotated += 1
                    comment_data['intersection_topics'] += 1
                    
                    # Check directional agreement
                    if directional_agreement(val1, val2):
                        directional_matches += 1
                        total_directional_matches += 1
                        comment_data['directional_matches'] += 1
                elif pd.isna(val1) and pd.isna(val2):
                    topics_both_nan.add(topic)
            
            # Calculate union
            union_topics = topics_marked1.union(topics_marked2)
            comment_data['union_topics'] = len(union_topics)
            
            # Calculate per-comment metrics
            
            # 1. Topic Selection Agreement (Jaccard Score)
            if len(union_topics) > 0:
                jaccard_score = len(topics_both_marked) / len(union_topics)
            elif len(topics_marked1) == 0 and len(topics_marked2) == 0:
                # Both annotators marked nothing - perfect agreement
                jaccard_score = 1.0
            else:
                jaccard_score = 0.0
                
            jaccard_values.append(jaccard_score)
            comment_data['topic_selection_agreement'] = jaccard_score
            
            # 2. Total Agreement Rate (previously "Modified Jaccard")
            agreement_count = len(topics_both_marked) + len(topics_both_nan)
            total_agreement = agreement_count / len(topic_columns) if len(topic_columns) > 0 else 0
            total_agreement_values.append(total_agreement)
            comment_data['total_agreement_rate'] = total_agreement
            
            all_comment_data.append(comment_data)
        
        # Skip if no comments were processed
        if total_comments == 0:
            continue
            
        # Calculate aggregated metrics
        
        # 3. Stance Direction Agreement (pooled)
        stance_direction_agreement = total_directional_matches / total_both_annotated if total_both_annotated > 0 else 0
        
        # Per-comment averaged metrics (with std)
        avg_topic_selection = np.mean(jaccard_values)
        std_topic_selection = np.std(jaccard_values)
        
        avg_total_agreement = np.mean(total_agreement_values)
        std_total_agreement = np.std(total_agreement_values)
        
        # Store results in the matrices (0-indexed, so subtract 1)
        topic_selection_matrix[annotator1-1, annotator2-1] = avg_topic_selection * 100
        topic_selection_matrix[annotator2-1, annotator1-1] = avg_topic_selection * 100  # Mirror values
        
        total_agreement_matrix[annotator1-1, annotator2-1] = avg_total_agreement * 100
        total_agreement_matrix[annotator2-1, annotator1-1] = avg_total_agreement * 100  # Mirror values
        
        stance_direction_matrix[annotator1-1, annotator2-1] = stance_direction_agreement * 100
        stance_direction_matrix[annotator2-1, annotator1-1] = stance_direction_agreement * 100  # Mirror values
        
        # Create detailed comment data CSV
        comment_df = pd.DataFrame(all_comment_data)
        comment_file = os.path.join(output_dir, f"pair_{annotator1}_{annotator2}_details.csv")
        comment_df.to_csv(comment_file, index=False)
        
        # Store results for this pair
        pair_result = {
            'annotator_pair': f"{annotator1}-{annotator2}",
            'total_comments': total_comments,
            'topic_selection_agreement': avg_topic_selection * 100,
            'topic_selection_agreement_std': std_topic_selection * 100,
            'total_agreement_rate': avg_total_agreement * 100,
            'total_agreement_rate_std': std_total_agreement * 100,
            'stance_direction_agreement': stance_direction_agreement * 100
        }
        
        agreement_results.append(pair_result)
        
        # Print results for this pair
        print(f"Annotators {annotator1}-{annotator2} results:")
        print(f"  - Total comments: {total_comments}")
        print(f"  - Topic Selection Agreement (Jaccard): {avg_topic_selection:.2%} ± {std_topic_selection:.2%}")
        print(f"  - Total Agreement Rate: {avg_total_agreement:.2%} ± {std_total_agreement:.2%}")
        print(f"  - Stance Direction Agreement: {stance_direction_agreement:.2%}")
    
    # Create overall summary
    if agreement_results:
        # Convert to DataFrame for easier analysis
        results_df = pd.DataFrame(agreement_results)
        
        # Calculate overall averages and standard deviations
        avg_metrics = {
            'topic_selection_agreement': {
                'mean': results_df['topic_selection_agreement'].mean(),
                'std': results_df['topic_selection_agreement_std'].mean()
            },
            'total_agreement_rate': {
                'mean': results_df['total_agreement_rate'].mean(),
                'std': results_df['total_agreement_rate_std'].mean()
            },
            'stance_direction_agreement': {
                'mean': results_df['stance_direction_agreement'].mean(),
                'std': results_df['stance_direction_agreement'].std()
            }
        }
        
        # Create overall metrics bar plot
        create_overall_metrics_plot(avg_metrics, plots_dir)
        
        # Create annotator agreement matrices
        create_agreement_matrices(
            topic_selection_matrix, 
            total_agreement_matrix, 
            stance_direction_matrix, 
            plots_dir
        )
        
        print("\nOverall Agreement Summary:")
        print("-" * 30)
        for metric, values in avg_metrics.items():
            if metric == 'stance_direction_agreement':
                print(f"{metric}: {values['mean']:.2f}% ± {values['std']:.2f}%")
            else:
                print(f"{metric}: {values['mean']:.2f}% ± {values['std']:.2f}%")
        
        # Save results to CSV
        results_file = os.path.join(output_dir, "interannotator_agreement_results.csv")
        results_df.to_csv(results_file, index=False)
        print(f"Results saved to: {results_file}")
        
        # Create a focused report
        report_file = os.path.join(output_dir, "interannotator_agreement_report.txt")
        with open(report_file, "w") as f:
            f.write("INTER-ANNOTATOR AGREEMENT ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("OVERALL METRICS\n")
            f.write("-" * 30 + "\n")
            for metric, values in avg_metrics.items():
                if metric == 'stance_direction_agreement':
                    f.write(f"{metric}: {values['mean']:.2f}% ± {values['std']:.2f}%\n")
                else:
                    f.write(f"{metric}: {values['mean']:.2f}% ± {values['std']:.2f}%\n")
            f.write("\n")
            
            f.write("EXPLANATION OF METRICS\n")
            f.write("-" * 30 + "\n")
            
            f.write("1. Topic Selection Agreement (Jaccard Score):\n")
            f.write("   - Measures how much annotators agree on WHICH topics to annotate\n")
            f.write("   - Calculated as: intersection / union of topics annotated by either annotator\n")
            f.write("   - Higher values indicate better agreement on topic selection\n\n")
            
            f.write("2. Total Agreement Rate:\n")
            f.write("   - Accounts for both mutual annotations AND mutual omissions\n")
            f.write("   - Calculated as: (shared annotations + shared omissions) / total topics\n")
            f.write("   - Useful when most topics are left blank by both annotators\n\n")
            
            f.write("3. Stance Direction Agreement:\n")
            f.write("   - Measures agreement on HOW topics were annotated (positive/negative stance)\n")
            f.write("   - Calculated as: total directional matches / total shared annotations\n")
            f.write("   - Treats E+/I+ as the same direction, E-/I- as the same direction\n\n")
            
            f.write("RESULTS BY ANNOTATOR PAIR\n")
            f.write("-" * 30 + "\n")
            
            # Create a table format in the specified order
            f.write(f"{'Pair':10} | {'TopicSel':15} | {'TotalAgree':15} | {'StanceDir':10} |\n")
            f.write(f"{'-'*10}-+-{'-'*15}-+-{'-'*15}-+-{'-'*10}-|\n")
            
            for _, row in results_df.iterrows():
                pair = row['annotator_pair']
                f.write(f"{pair:10} | ")
                f.write(f"{row['topic_selection_agreement']:6.2f}% ± {row['topic_selection_agreement_std']:5.2f}% | ")
                f.write(f"{row['total_agreement_rate']:6.2f}% ± {row['total_agreement_rate_std']:5.2f}% | ")
                f.write(f"{row['stance_direction_agreement']:8.2f}% |\n")
            
            f.write("\nVisualization files created in the 'plots' directory:\n")
            f.write("1. overall_metrics.png/pdf - Bar chart showing all three metrics\n")
            f.write("2. agreement_matrices.png/pdf - Heatmaps showing agreement between all annotator pairs\n")
        
        print(f"Detailed report saved to: {report_file}")
        print(f"Plots saved to: {plots_dir}")
    
    return agreement_results

def create_overall_metrics_plot(avg_metrics, plots_dir):
    """
    Create a bar plot of the overall metrics with error bars,
    with improved styling and both PNG and PDF outputs
    """
    plt.figure(figsize=(10, 6))
    
    # Extract data
    metrics = list(avg_metrics.keys())
    means = [avg_metrics[m]['mean'] for m in metrics]
    stds = [avg_metrics[m]['std'] for m in metrics]
    
    # Define nice labels and colors
    labels = [
        "Topic Selection\nAgreement",
        "Total Agreement\nRate",
        "Stance Direction\nAgreement"
    ]
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    
    # Create the bar plot
    bars = plt.bar(labels, means, yerr=stds, capsize=10, color=colors, width=0.5)
    
    # Add value labels on top of each bar
    for bar, mean, std in zip(bars, means, stds):
        plt.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + std + 2,
            f"{mean:.1f}%",
            ha='center', va='bottom',
            fontweight='bold'
        )
    
    # Customize the plot
    plt.ylim(0, 110)  # Increase the y-limit to accommodate the labels and error bars
    plt.ylabel('Agreement (%)', fontsize=12)
    plt.title('Inter-Annotator Agreement Metrics', fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add a light gray background
    plt.gca().set_facecolor('#f8f9fa')
    
    # Customize the spine visibility and add a border
    for spine in plt.gca().spines.values():
        spine.set_visible(True)
        spine.set_color('#cccccc')
    
    plt.tight_layout()
    
    # Save the plot in PNG format
    output_path_png = os.path.join(plots_dir, "overall_metrics.png")
    plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
    
    # Save the plot in PDF format
    output_path_pdf = os.path.join(plots_dir, "overall_metrics.pdf")
    plt.savefig(output_path_pdf, format='pdf', bbox_inches='tight')
    
    plt.close()

def create_agreement_matrices(topic_selection, total_agreement, stance_direction, plots_dir):
    """
    Create heatmaps for each agreement metric between annotators,
    showing only the lower triangle of each matrix
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Define annotator labels
    annotators = [f"A{i+1}" for i in range(4)]
    
    # Set colormap options
    cmap = "YlGnBu"
    vmin = 0
    vmax = 100
    
    # Mask for the upper triangle (including the diagonal)
    mask = np.triu(np.ones_like(topic_selection, dtype=bool))
    
    # Topic Selection Agreement Matrix
    sns.heatmap(
        topic_selection, 
        annot=True, 
        fmt=".1f", 
        cmap=cmap,
        vmin=vmin, 
        vmax=vmax,
        cbar=True, 
        square=True,
        xticklabels=annotators,
        yticklabels=annotators,
        mask=mask,
        ax=axes[0]
    )
    axes[0].set_title("Topic Selection Agreement", fontweight='bold')
    
    # Total Agreement Matrix
    sns.heatmap(
        total_agreement, 
        annot=True, 
        fmt=".1f", 
        cmap=cmap,
        vmin=vmin, 
        vmax=vmax,
        cbar=True, 
        square=True,
        xticklabels=annotators,
        yticklabels=annotators,
        mask=mask,
        ax=axes[1]
    )
    axes[1].set_title("Total Agreement Rate", fontweight='bold')
    
    # Stance Direction Matrix
    sns.heatmap(
        stance_direction, 
        annot=True, 
        fmt=".1f", 
        cmap=cmap,
        vmin=vmin, 
        vmax=vmax,
        cbar=True, 
        square=True,
        xticklabels=annotators,
        yticklabels=annotators,
        mask=mask,
        ax=axes[2]
    )
    axes[2].set_title("Stance Direction Agreement", fontweight='bold')
    
    # Add a title for the entire figure
    plt.suptitle("Inter-Annotator Agreement Matrices", fontsize=16, fontweight='bold', y=1.05)
    
    # Tight layout
    plt.tight_layout()
    
    # Save the figure in PNG format
    output_path_png = os.path.join(plots_dir, "agreement_matrices.png")
    plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
    
    # Save the figure in PDF format
    output_path_pdf = os.path.join(plots_dir, "agreement_matrices.pdf")
    plt.savefig(output_path_pdf, format='pdf', bbox_inches='tight')
    
    plt.close()

def directional_agreement(value1, value2):
    """
    Check if two annotation values agree directionally:
    - Both are negative (E- or I-)
    - Both are positive (E+ or I+)
    - Both are zero (0)
    """
    # Convert to strings for comparison
    val1 = str(value1).strip() if not pd.isna(value1) else ""
    val2 = str(value2).strip() if not pd.isna(value2) else ""
    
    # Check for exact match
    if val1 == val2:
        return True
    
    # Check for directional agreement
    negative_values = ["E-", "E -", "I-", "I -"]
    positive_values = ["E+", "E +", "I+", "I +"]
    
    # Both negative
    if val1 in negative_values and val2 in negative_values:
        return True
    
    # Both positive
    if val1 in positive_values and val2 in positive_values:
        return True
    
    # Otherwise, no directional agreement
    return False

if __name__ == "__main__":
    analyze_interannotator_agreement()