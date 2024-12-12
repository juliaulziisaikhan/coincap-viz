import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import pandas as pd
import argparse
import re

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# convert article time published "21m" to timedelta
def parse_time_ago(time_string):
    """Parses a string like '21 m' to a timedelta object"""
    match = re.match(r'(\d+)\s*(m|h|d)', time_string.strip())
    if not match:
        return None
    
    number, unit = match.groups()
    number = int(number)
    
    if unit == 'm':
        return timedelta(minutes=number)
    elif unit == 'h':
        return timedelta(hours=number)
    elif unit == 'd':
        return timedelta(days=number)

# scrape a single article's detailed content
def scrape_article(url, data_id):
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to retrieve article. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # title
    title_tag = soup.find('h1', class_='article_title')
    title = title_tag.get_text() if title_tag else None
    
    # content
    content_tag = soup.find('div', class_='cn-content') 
    content = content_tag.get_text(separator="\n", strip=True) if content_tag else None
    
    # source link
    source_link_tag = soup.find('a', class_='source-host')
    source_link = source_link_tag.get('href') if source_link_tag else None
    
    # time ago (e.g., '21 m' for 21 minutes ago)
    time_tag = soup.find('span', class_='datetime flex middle-xs')
    time_ago = time_tag.get_text(strip=True) if time_tag else '0 m'
    
    # convert time ago to datetime
    time_delta = parse_time_ago(time_ago)
    if time_delta:
        datetime_published = datetime.utcnow() - time_delta
    else:
        datetime_published = datetime.utcnow()
    
    # image url
    image_tag = soup.find('div', class_='news-item detail content_text')
    image_url = image_tag.get('data-image') if image_tag else None
    
    article_data = {
        'data_id': data_id, 
        'title': title,
        'content': content,
        'source_link': source_link,
        'datetime_published': datetime_published,
        'image_url': image_url,
    }
    
    missing_fields = [field for field, value in article_data.items() if value is None]
    
    if missing_fields:
        if title and content:  
            logger.info(f"Partially scraped: data-id {data_id} missing fields: {', '.join(missing_fields)}")
            article_data['status'] = 'Partially Scraped'
        else:  
            logger.info(f"Unsuccessfully scraped, skipping: data-id {data_id}")
            article_data['status'] = 'Skipped'
            return None  
    else:
        logger.info(f"Successfully scraped: data-id {data_id}")
        article_data['status'] = 'Successfully Scraped'
    
    return article_data

if __name__ == "__main__":
    # command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file', help='Path to the input CSV file containing article URLs')
    parser.add_argument('--stop_at_article_count', type=int, help='Stop after scraping this number of articles')
    args = parser.parse_args()

    # log input file URL
    logger.info(f"Input CSV file: {args.csv_file}")
    
    # read the input CSV with URLs
    df = pd.read_csv(args.csv_file)
    article_urls = df['url'].tolist()

    article_data_list_full = []
    total_articles_scraped = 0

    for article_url in article_urls:
        # assuming the data-id is the last part of the URL path, like /news/finance/30203892/
        data_id = '/'.join(article_url.split('/')[3:])  # The portion of the URL you want as data-id
        article_data_detail = scrape_article(article_url, data_id)
        
        if article_data_detail:
            article_data_list_full.append(article_data_detail)
            total_articles_scraped += 1
        
        if args.stop_at_article_count and total_articles_scraped >= args.stop_at_article_count:
            logger.info(f"Reached the article limit of {args.stop_at_article_count}. Exiting.")
            break

    if article_data_list_full:
        # create df
        df_articles = pd.DataFrame(article_data_list_full)
        
        # save to csv
        timestamp = datetime.now().strftime("%Y%m%d")
        save_path = f'cryptonews_net_articles_{timestamp}.csv'
        
        df_articles.to_csv(save_path, index=False)
        logger.info(f"Data saved to {save_path}")
    else:
        logger.error("No data to save.")
