# Web Scraper + Analyzer

A simple Python project I built to scrape articles from Hacker News and analyze the data. It extracts article titles, links, and scores, then performs some basic analysis like finding top keywords and generating charts.

## What This Project Does

- Scrapes the front page of Hacker News
- Saves article data (title, link, score, timestamp) to a CSV file
- Analyzes the data to find patterns
- Shows top keywords from article titles
- Creates visualizations using matplotlib

## Tech Stack

- **requests** - for making HTTP requests
- **BeautifulSoup** - for parsing HTML
- **pandas** - for data manipulation
- **matplotlib** - for creating charts

## Project Structure

```
web_scraper_analyzer/
├── scraper.py          # main scraping script
├── analyzer.py         # analysis and visualization
├── requirements.txt
├── README.md
├── data/               # output files go here
│   ├── scraped_data.csv
│   ├── score_distribution.png
│   └── keyword_frequency.png
└── logs/               # log files
    ├── scraper.log
    └── analyzer.log
```

## How to Run

1. Clone the repo and navigate to the folder

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scraper first:
```bash
python scraper.py
```

4. Then run the analyzer:
```bash
python analyzer.py
```

## What You Get

After running both scripts, you'll find:

- `data/scraped_data.csv` - all the scraped articles in CSV format
- `data/score_distribution.png` - histogram showing how scores are distributed
- `data/keyword_frequency.png` - bar chart of most common words in titles

The analyzer also prints out some stats in the terminal like total articles, average score, and top 5 highest-scored articles.

## Features I Added

- Error handling for network issues
- Logging to track what's happening (check the logs folder)
- Data cleaning to remove duplicates and handle missing values
- Stopword filtering for keyword analysis (removes common words like "the", "and", etc.)

## Notes

- The scraper only gets articles from the first page of HN (about 30 articles)
- Run the scraper at different times to get different data since HN updates frequently
- Charts are generated fresh each time based on whatever data is in the CSV

---

Feel free to fork this or suggest improvements!