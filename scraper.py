"""
Web Scraper for Hacker News
Scrapes article titles, links, and scores from https://news.ycombinator.com/
Saves cleaned data to CSV with logging support.
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import logging
from datetime import datetime


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
    log_file = os.path.join(logs_dir, 'scraper.log')
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
# HELPER FUNCTIONS
# ============================================
def create_directories():
    """Create data and logs directories if they don't exist."""
    base_dir = os.path.dirname(__file__)
    
    data_dir = os.path.join(base_dir, 'data')
    logs_dir = os.path.join(base_dir, 'logs')
    
    for directory in [data_dir, logs_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")


def fetch_page(url, logger):
    """
    Fetch webpage content with timeout and error handling.
    Returns BeautifulSoup object or None if failed.
    """
    try:
        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, timeout=10)
        
        # Validate status code
        if response.status_code != 200:
            logger.error(f"Bad status code: {response.status_code} for URL: {url}")
            return None
        
        logger.info("Page fetched successfully")
        return BeautifulSoup(response.text, 'html.parser')
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while fetching: {url}")
        return None
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching: {url}")
        return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return None


def extract_score(score_text, logger):
    """
    Extract integer score from score text.
    Returns 0 if score cannot be parsed.
    """
    try:
        # Score format is usually "123 points"
        score_str = score_text.strip().split()[0]
        return int(score_str)
    except (ValueError, IndexError, AttributeError):
        logger.warning(f"Could not parse score: {score_text}")
        return 0


def clean_title(title_text):
    """
    Clean and validate article title.
    Returns cleaned title or None if invalid.
    """
    if not title_text:
        return None
    
    # Strip whitespace
    cleaned = title_text.strip()
    
    # Return None for empty titles
    if not cleaned or len(cleaned) == 0:
        return None
    
    return cleaned


def parse_articles(soup, logger):
    """
    Parse article data from BeautifulSoup object.
    Returns list of article dictionaries.
    """
    articles = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Find all article rows (class 'athing')
        article_rows = soup.find_all('tr', class_='athing')
        logger.info(f"Found {len(article_rows)} article rows")
        
        for row in article_rows:
            try:
                # Get article ID for matching with score
                article_id = row.get('id')
                
                # Find title and link
                title_span = row.find('span', class_='titleline')
                if not title_span:
                    logger.warning(f"No title found for article ID: {article_id}")
                    continue
                
                title_link = title_span.find('a')
                if not title_link:
                    logger.warning(f"No link found for article ID: {article_id}")
                    continue
                
                # Extract and clean title
                raw_title = title_link.get_text()
                title = clean_title(raw_title)
                
                if not title:
                    logger.warning(f"Empty title for article ID: {article_id}")
                    continue
                
                # Extract link
                link = title_link.get('href', '')
                
                # Handle relative links
                if link.startswith('item?'):
                    link = 'https://news.ycombinator.com/' + link
                
                # Find score (in the next sibling row)
                score = 0
                next_row = row.find_next_sibling('tr')
                if next_row:
                    score_span = next_row.find('span', class_='score')
                    if score_span:
                        score = extract_score(score_span.get_text(), logger)
                
                # Create article dictionary
                article = {
                    'title': title,
                    'link': link,
                    'score': score,
                    'timestamp': timestamp
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error parsing article: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(articles)} articles")
        
    except Exception as e:
        logger.error(f"Error during parsing: {str(e)}")
    
    return articles


def save_to_csv(articles, filepath, logger):
    """
    Save articles list to CSV file.
    """
    try:
        # Define CSV columns
        fieldnames = ['title', 'link', 'score', 'timestamp']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(articles)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return True
        
    except IOError as e:
        logger.error(f"Error saving CSV file: {str(e)}")
        return False


# ============================================
# MAIN FUNCTION
# ============================================
def main():
    """Main function to run the scraper."""
    # Setup
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Starting Hacker News Scraper")
    logger.info("=" * 50)
    
    # Create necessary directories
    create_directories()
    
    # Target URL
    url = "https://news.ycombinator.com/"
    
    # Fetch page
    soup = fetch_page(url, logger)
    if not soup:
        logger.error("Failed to fetch page. Exiting.")
        return
    
    # Parse articles
    articles = parse_articles(soup, logger)
    if not articles:
        logger.error("No articles found. Exiting.")
        return
    
    # Save to CSV
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'data', 'scraped_data.csv')
    
    if save_to_csv(articles, csv_path, logger):
        print(f"\n[OK] Successfully scraped {len(articles)} articles!")
        print(f"[OK] Data saved to: {csv_path}")
    else:
        print("\n[ERROR] Failed to save data")
    
    logger.info("Scraper finished")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
