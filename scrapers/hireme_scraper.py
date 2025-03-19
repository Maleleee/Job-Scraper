from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import logging
import time

logger = logging.getLogger(__name__)

def scrape_hireme(keyword=None, location=None, max_pages=3):
    """
    Scrape jobs from HireMe.ph with pagination support
    
    Args:
        keyword (str, optional): Search keyword to filter jobs
        location (str, optional): Location to filter jobs
        max_pages (int): Maximum number of pages to scrape (default: 3)
    """
    scraper = BaseScraper()
    jobs = []
    base_url = "https://hireme.ph"
    
    for page in range(1, max_pages + 1):
        try:
            # Construct URL with page parameter
            url = f"{base_url}/page/{page}/" if page > 1 else base_url
            logger.info(f"Scraping HireMe.ph page {page}: {url}")
            
            html = scraper.get_page(url)
            if not html:
                logger.error(f"Failed to get HTML content from HireMe.ph page {page}")
                continue
            
            soup = BeautifulSoup(html, 'lxml')
            logger.info(f"Successfully parsed HireMe.ph page {page}")
            
            # Find all job listings - try different possible selectors
            job_listings = soup.find_all('article', class_='job-listing') or \
                          soup.find_all('div', class_='job-listing') or \
                          soup.find_all('div', class_='job-item')
            
            logger.info(f"Found {len(job_listings)} job listings on HireMe.ph page {page}")
            
            if not job_listings:
                logger.warning("No job listings found. HTML content preview:")
                logger.warning(html[:500])  # Log first 500 chars of HTML for debugging
            
            for job in job_listings:
                try:
                    # Try different possible selectors for each element
                    title_elem = job.find('h2', class_='entry-title') or \
                               job.find('h2', class_='job-title') or \
                               job.find('h3', class_='job-title')
                    
                    company_elem = job.find('div', class_='company') or \
                                 job.find('div', class_='company-name')
                    
                    location_elem = job.find('div', class_='location') or \
                                  job.find('div', class_='job-location')
                    
                    link_elem = job.find('a', class_='job-link') or \
                              job.find('a', class_='job-title-link') or \
                              job.find('a')
                    
                    # Extract additional details if available
                    salary_elem = job.find('div', class_='salary') or \
                                job.find('div', class_='job-salary')
                    date_elem = job.find('div', class_='date') or \
                              job.find('div', class_='job-date')
                    
                    if not all([title_elem, company_elem, location_elem, link_elem]):
                        logger.warning("Missing required elements in HireMe.ph job listing")
                        logger.warning(f"Job HTML: {job.prettify()[:200]}")  # Log job HTML for debugging
                        continue
                    
                    job_location = scraper.clean_text(location_elem.text)
                    logger.info(f"Found job location: {job_location}")
                    
                    # Filter by location if specified
                    if location and location.lower() not in job_location.lower():
                        logger.info(f"Skipping job - location mismatch: {job_location} (searching for: {location})")
                        continue
                    
                    job_data = {
                        'title': scraper.clean_text(title_elem.text),
                        'company': scraper.clean_text(company_elem.text),
                        'location': job_location,
                        'url': link_elem['href'],
                        'source': 'HireMe.ph',
                        'date_posted': scraper.parse_date(date_elem.text) if date_elem else scraper.parse_date(''),
                        'salary': scraper.clean_text(salary_elem.text) if salary_elem else ''
                    }
                    
                    # Filter by keyword if specified
                    if keyword and keyword.lower() not in job_data['title'].lower():
                        logger.info(f"Skipping job - keyword mismatch: {job_data['title']} (searching for: {keyword})")
                        continue
                    
                    jobs.append(job_data)
                    logger.info(f"Successfully parsed HireMe.ph job: {job_data['title']} in {job_data['location']}")
                    
                except Exception as e:
                    logger.error(f"Error parsing HireMe.ph job: {str(e)}")
                    continue
            
            # Check if there's a next page
            next_page = soup.find('a', class_='next')
            if not next_page:
                logger.info("No more pages to scrape on HireMe.ph")
                break
                
            # Add a delay between pages
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error scraping HireMe.ph page {page}: {str(e)}")
            continue
    
    logger.info(f"Total jobs scraped from HireMe.ph: {len(jobs)}")
    return jobs 