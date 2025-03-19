import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
import random

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def get_page(self, url):
        """
        Fetch a webpage with proper headers and error handling
        
        Args:
            url (str): URL to fetch
            
        Returns:
            str: HTML content or None if failed
        """
        try:
            # Add a random delay between 1-3 seconds
            delay = random.uniform(1, 3)
            logger.info(f"Waiting {delay:.1f} seconds before fetching {url}")
            time.sleep(delay)
            
            # Log the headers being used
            logger.info(f"Using headers: {self.headers}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            # Log the content type
            content_type = response.headers.get('content-type', '')
            logger.info(f"Content type: {content_type}")
            
            # Check if we got HTML content
            if 'text/html' not in content_type.lower():
                logger.warning(f"Received non-HTML content: {content_type}")
                return None
            
            # Log the first 500 characters of the response
            logger.info(f"Response preview: {response.text[:500]}")
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            return datetime.now().strftime('%Y-%m-%d')

    def clean_text(self, text):
        if not text:
            return ""
        return ' '.join(text.split()) 