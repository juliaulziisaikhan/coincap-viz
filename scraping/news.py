import requests
from bs4 import BeautifulSoup
import logging
import argparse
from datetime import datetime
import pandas as pd

#python scrape_crypto.py --stop_at_article_count 100

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_article_links(url, scraped_urls):
    logger.info(f"Fetching page: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to retrieve page. Status code: {response.status_code}")
        return []
    
    logger.info("Parsing page HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    article_data_list = []
    for item in soup.find_all('div', class_='row news-item start-xs'):
        data_id = item.get('data-id')
        
        if data_id and data_id not in scraped_urls:
            article_data = {
                'url': 'https://cryptonews.net' + data_id  # construct full article URL
            }
            article_data_list.append(article_data)
            scraped_urls.add(data_id)
    
    logger.info(f"Found {len(article_data_list)} articles on this page.")
    return article_data_list

def scrape_article(url):
    logger.info(f"Scraping article: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to retrieve article. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # title
    title_tag = soup.find('h1', class_='article-title')
    title = title_tag.get_text() if title_tag else 'No title found'
    
    # publish date (from meta tags)
    date_published_tag = soup.find('meta', property='article:published_time')
    date_published = date_published_tag['content'] if date_published_tag else 'No date found'
    
    # author (adjust selector if necessary)
    author_tag = soup.find('span', class_='author-name')
    author = author_tag.get_text() if author_tag else 'No author found'
    
    # coins mentioned (adjust the selector based on actual page structure)
    coins = [coin.get_text() for coin in soup.find_all('span', class_='coin-name')]  # Adjust class
    
    # content (adjust based on actual class)
    content_tag = soup.find('div', class_='article-content')
    content = content_tag.get_text() if content_tag else 'No content found'
    
    article_data = {
        'title': title,
        'date_published': date_published,
        'author': author,
        'coins': coins,
        'content': content
    }
    
    return article_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--stop_at_page', type=int, help='Stop after this page number')
    parser.add_argument('--stop_at_article_count', type=int, help='Stop after scraping this number of articles')
    args = parser.parse_args()

    base_url = 'https://cryptonews.net/'
    scraped_urls = set()
    article_data_list_full = []
    page_number = 1
    total_articles_scraped = 0

    while True:
        page_url = f"{base_url}?page={page_number}" if page_number > 1 else base_url
        
        logger.info(f"Scraping page {page_number} at {page_url}")
        
        article_data_list = get_article_links(page_url, scraped_urls)
        
        if not article_data_list:
            logger.info("No new articles found. Exiting.")
            break

        for article_data in article_data_list:
            article_url = article_data['url']
            article_data_detail = scrape_article(article_url)
            
            if article_data_detail:
                article_data.update(article_data_detail) 
                article_data_list_full.append(article_data)
                total_articles_scraped += 1
                logger.info(f"Successfully scraped: {article_url}")
            
            if args.stop_at_article_count and total_articles_scraped >= args.stop_at_article_count:
                logger.info(f"Reached the article limit of {args.stop_at_article_count}. Exiting.")
                break
        
        if args.stop_at_page and page_number >= args.stop_at_page:
            logger.info(f"Reached the page limit of {args.stop_at_page}. Exiting.")
            break
        
        if args.stop_at_article_count and total_articles_scraped >= args.stop_at_article_count:
            break
        
        page_number += 1
    
    if article_data_list_full:
        # create df
        df = pd.DataFrame(article_data_list_full)
        
        # save to CSV
        timestamp = datetime.now().strftime("%Y%m%d")
        save_path = f'/Users/juliaulzii/coincap/crypto_data/raw/cryptonews_net_{timestamp}.csv'
        
        df.to_csv(save_path, index=False)
        logger.info(f"Data saved to {save_path}")
    else:
        logger.error("No data to save.")
