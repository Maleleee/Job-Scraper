from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import logging
import requests
import urllib.parse

logger = logging.getLogger(__name__)

def scrape_workabroad(keyword=None, specialization=None, location=None):
    """
    Scrape jobs from WorkAbroad.ph with search functionality
    
    Args:
        keyword (str, optional): Search keyword to filter jobs
        specialization (str, optional): Job specialization to filter jobs
        location (str, optional): Location to filter jobs (can be country or city)
    """
    scraper = BaseScraper()
    jobs = []
    base_url = "https://www.workabroad.ph/search-jobs/b/landbased"
    
    try:
        # Create a session to handle cookies and redirects
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
        # First visit the homepage to get cookies
        logger.info("Visiting WorkAbroad.ph homepage...")
        session.get("https://www.workabroad.ph")
        
        # Construct search parameters
        params = {}
        if keyword:
            params['keywords'] = keyword
        if specialization:
            params['specialization'] = specialization
        if location:
            # For WorkAbroad.ph, we'll use the location as a keyword since it's an overseas job site
            params['keywords'] = f"{keyword} {location}".strip() if keyword else location
            
        # Build the search URL
        search_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        logger.info(f"Scraping WorkAbroad.ph with URL: {search_url}")
        
        # Get the search results page
        response = session.get(search_url)
        logger.info(f"WorkAbroad.ph response status: {response.status_code}")
        logger.info(f"WorkAbroad.ph response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            logger.error(f"Failed to get search results from WorkAbroad.ph: {response.status_code}")
            return jobs
            
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        logger.info("Successfully parsed WorkAbroad.ph HTML")
        
        # Find all job listings - try different possible selectors
        job_listings = soup.find_all('div', class_='job-listing') or \
                      soup.find_all('div', class_='job-item') or \
                      soup.find_all('article', class_='job-listing')
        
        logger.info(f"Found {len(job_listings)} job listings on WorkAbroad.ph")
        
        if not job_listings:
            logger.warning("No job listings found. HTML content preview:")
            logger.warning(html[:500])  # Log first 500 chars of HTML for debugging
        
        for job in job_listings:
            try:
                # Try different possible selectors for each element
                title_elem = job.find('h2', class_='job-title') or \
                           job.find('h3', class_='job-title') or \
                           job.find('h2', class_='entry-title')
                
                company_elem = job.find('div', class_='company-name') or \
                             job.find('div', class_='company')
                
                location_elem = job.find('div', class_='location') or \
                              job.find('div', class_='job-location')
                
                link_elem = job.find('a', class_='job-link') or \
                          job.find('a', class_='job-title-link') or \
                          job.find('a')
                
                if not all([title_elem, company_elem, location_elem, link_elem]):
                    logger.warning("Missing required elements in WorkAbroad.ph job listing")
                    logger.warning(f"Job HTML: {job.prettify()[:200]}")  # Log job HTML for debugging
                    continue
                
                job_location = scraper.clean_text(location_elem.text)
                logger.info(f"Found job location: {job_location}")
                
                # Filter by location if specified
                if location:
                    # For overseas jobs, we'll check if the location is mentioned in the title or location
                    location_match = (
                        location.lower() in job_location.lower() or
                        location.lower() in scraper.clean_text(title_elem.text).lower()
                    )
                    if not location_match:
                        logger.info(f"Skipping job - location mismatch: {job_location} (searching for: {location})")
                        continue
                
                # Extract additional details
                experience_elem = job.find('div', class_='experience') or \
                                job.find('div', class_='job-experience')
                vacancies_elem = job.find('div', class_='vacancies') or \
                               job.find('div', class_='job-vacancies')
                
                job_data = {
                    'title': scraper.clean_text(title_elem.text),
                    'company': scraper.clean_text(company_elem.text),
                    'location': job_location,
                    'url': link_elem['href'],
                    'source': 'WorkAbroad.ph',
                    'date_posted': scraper.parse_date(''),  # WorkAbroad.ph doesn't show posting dates
                    'experience': scraper.clean_text(experience_elem.text) if experience_elem else '',
                    'vacancies': scraper.clean_text(vacancies_elem.text) if vacancies_elem else ''
                }
                
                # Filter by keyword if specified (excluding location from keyword)
                if keyword and keyword.lower() not in job_data['title'].lower():
                    logger.info(f"Skipping job - keyword mismatch: {job_data['title']} (searching for: {keyword})")
                    continue
                
                jobs.append(job_data)
                logger.info(f"Successfully parsed WorkAbroad.ph job: {job_data['title']} in {job_data['location']}")
                
            except Exception as e:
                logger.error(f"Error parsing WorkAbroad.ph job: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping WorkAbroad.ph: {str(e)}")
    
    logger.info(f"Total jobs scraped from WorkAbroad.ph: {len(jobs)}")
    return jobs 