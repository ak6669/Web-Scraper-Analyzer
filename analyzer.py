"""
Data Analyzer for Scraped Hacker News Articles
Analyzes article data, performs keyword analysis, and generates visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
from collections import Counter


# ============================================
# SETUP LOGGING
# ============================================
def setup_logging():
    """Create logs directory and configure logging."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    log_file = os.path.join(logs_dir, 'analyzer.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return logging.getLogger(__name__)


# ============================================
# STOPWORDS LIST
# ============================================
# Common English stopwords to filter out from keyword analysis
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
    'used', 'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
    'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'whose', 'where',
    'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 'just', 'about', 'into', 'over',
    'after', 'before', 'between', 'through', 'during', 'above', 'below',
    'up', 'down', 'out', 'off', 'again', 'then', 'once', 'here', 'there',
    'any', 'your', 'my', 'his', 'her', 'our', 'their', 'if', 'because',
    'while', 'although', 'though', 'unless', 'until', 'since', 'now', 'new',
    'show', 'ask', 'get', 'got', 'make', 'vs', 'via', 'using', 'based'
}


# ============================================
# HELPER FUNCTIONS
# ============================================
def load_data(filepath, logger):
    """
    Load CSV data using pandas.
    Returns DataFrame or None if failed.
    """
    try:
        logger.info(f"Loading data from: {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} rows")
        return df
    
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        print(f"\n✗ Error: Data file not found!")
        print("  Please run scraper.py first to generate data.")
        return None
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None


def clean_data(df, logger):
    """
    Clean the DataFrame:
    - Remove duplicates
    - Handle missing values
    - Ensure correct data types
    """
    logger.info("Starting data cleaning")
    
    original_count = len(df)
    
    # Remove duplicates based on title and link
    df = df.drop_duplicates(subset=['title', 'link'])
    duplicates_removed = original_count - len(df)
    logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    # Handle missing values
    # Fill missing scores with 0
    df['score'] = df['score'].fillna(0)
    
    # Drop rows with missing titles
    df = df.dropna(subset=['title'])
    
    # Ensure score is integer
    df['score'] = df['score'].astype(int)
    
    logger.info(f"Data cleaning complete. {len(df)} rows remaining")
    
    return df


def compute_basic_stats(df, logger):
    """
    Compute and display basic statistics:
    - Total article count
    - Average score
    - Top 5 articles by score
    """
    logger.info("Computing basic statistics")
    
    # Total count
    total_articles = len(df)
    
    # Average score
    avg_score = df['score'].mean()
    
    # Top 5 by score
    top_5 = df.nlargest(5, 'score')[['title', 'score']]
    
    # Display results
    print("\n" + "=" * 60)
    print("BASIC STATISTICS")
    print("=" * 60)
    print(f"\n[STAT] Total Articles: {total_articles}")
    print(f"[STAT] Average Score: {avg_score:.2f}")
    
    print("\n[TOP] Top 5 Articles by Score:")
    print("-" * 60)
    for idx, row in top_5.iterrows():
        title = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
        print(f"  [{row['score']:4d}] {title}")
    
    logger.info(f"Total articles: {total_articles}, Average score: {avg_score:.2f}")
    
    return total_articles, avg_score, top_5


def extract_keywords(df, logger):
    """
    Extract keywords from article titles.
    - Convert to lowercase
    - Remove stopwords
    - Count frequency
    """
    logger.info("Starting keyword extraction")
    
    all_words = []
    
    for title in df['title']:
        # Convert to lowercase
        title_lower = str(title).lower()
        
        # Split into words and clean
        words = title_lower.split()
        
        for word in words:
            # Remove punctuation from word
            clean_word = ''.join(char for char in word if char.isalnum())
            
            # Skip empty words, short words, and stopwords
            if clean_word and len(clean_word) > 2 and clean_word not in STOPWORDS:
                all_words.append(clean_word)
    
    # Count word frequency
    word_counts = Counter(all_words)
    
    # Get top 10 keywords
    top_keywords = word_counts.most_common(10)
    
    logger.info(f"Extracted {len(word_counts)} unique keywords")
    
    return top_keywords, word_counts


def display_keywords(top_keywords, logger):
    """Display top keywords in a formatted way."""
    print("\n" + "=" * 60)
    print("KEYWORD ANALYSIS")
    print("=" * 60)
    print("\n[KEYWORDS] Top 10 Keywords in Article Titles:")
    print("-" * 40)
    
    for rank, (keyword, count) in enumerate(top_keywords, 1):
        bar = "#" * min(count, 20)  # Visual bar (max 20 chars)
        print(f"  {rank:2d}. {keyword:15s} | {count:3d} | {bar}")
    
    logger.info("Displayed top 10 keywords")


def plot_score_distribution(df, save_path, logger):
    """
    Create a histogram of score distribution.
    """
    logger.info("Creating score distribution plot")
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    plt.hist(df['score'], bins=20, color='#3498db', edgecolor='white', alpha=0.8)
    
    # Styling
    plt.title('Score Distribution of Hacker News Articles', fontsize=14, fontweight='bold')
    plt.xlabel('Score', fontsize=12)
    plt.ylabel('Number of Articles', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add mean line
    mean_score = df['score'].mean()
    plt.axvline(mean_score, color='#e74c3c', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.1f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    logger.info(f"Score distribution plot saved to: {save_path}")
    print(f"\n[CHART] Score distribution chart saved to: {save_path}")


def plot_keyword_frequency(top_keywords, save_path, logger):
    """
    Create a bar chart of keyword frequency.
    """
    logger.info("Creating keyword frequency plot")
    
    # Prepare data
    keywords = [kw[0] for kw in top_keywords]
    counts = [kw[1] for kw in top_keywords]
    
    # Reverse for horizontal bar chart (highest at top)
    keywords = keywords[::-1]
    counts = counts[::-1]
    
    plt.figure(figsize=(10, 6))
    
    # Create horizontal bar chart
    colors = plt.cm.Blues([0.4 + 0.06 * i for i in range(len(keywords))])
    bars = plt.barh(keywords, counts, color=colors, edgecolor='white')
    
    # Add count labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, 
                 str(count), va='center', fontsize=10)
    
    # Styling
    plt.title('Top 10 Keywords in Article Titles', fontsize=14, fontweight='bold')
    plt.xlabel('Frequency', fontsize=12)
    plt.ylabel('Keyword', fontsize=12)
    plt.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    logger.info(f"Keyword frequency plot saved to: {save_path}")
    print(f"[CHART] Keyword frequency chart saved to: {save_path}")


# ============================================
# MAIN FUNCTION
# ============================================
def main():
    """Main function to run the analyzer."""
    # Setup
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Starting Data Analyzer")
    logger.info("=" * 50)
    
    # File paths
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, 'data', 'scraped_data.csv')
    
    # Load data
    df = load_data(data_path, logger)
    if df is None:
        return
    
    # Clean data
    df = clean_data(df, logger)
    
    # Compute basic statistics
    total, avg, top_5 = compute_basic_stats(df, logger)
    
    # Keyword analysis
    top_keywords, word_counts = extract_keywords(df, logger)
    display_keywords(top_keywords, logger)
    
    # Create plots
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    
    # Score distribution plot
    score_plot_path = os.path.join(base_dir, 'data', 'score_distribution.png')
    plot_score_distribution(df, score_plot_path, logger)
    
    # Keyword frequency plot
    keyword_plot_path = os.path.join(base_dir, 'data', 'keyword_frequency.png')
    plot_keyword_frequency(top_keywords, keyword_plot_path, logger)
    
    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\n[OK] All analysis steps completed successfully!")
    print(f"[OK] Charts saved in: {os.path.join(base_dir, 'data')}")
    
    logger.info("Analyzer finished successfully")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
