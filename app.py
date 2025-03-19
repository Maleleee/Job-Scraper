from flask import Flask, render_template, jsonify, request
from scrapers.hireme_scraper import scrape_hireme
from scrapers.workabroad_scraper import scrape_workabroad
import logging

app = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/jobs')
def get_jobs():
    jobs = []
    
    try:
        # Get search parameters from query string
        keyword = request.args.get('keyword')
        specialization = request.args.get('specialization')
        location = request.args.get('location')
        location_type = request.args.get('locationType')
        
        logger.info(f"Starting job scraping process with keyword: {keyword}, specialization: {specialization}, location: {location}, location_type: {location_type}")
        
        # Scrape from each website based on location type
        if not location_type or location_type == 'local':
            hireme_jobs = scrape_hireme(keyword=keyword, location=location)
            logger.info(f"Scraped {len(hireme_jobs)} jobs from HireMe.ph")
            jobs.extend(hireme_jobs)
        
        if not location_type or location_type == 'overseas':
            workabroad_jobs = scrape_workabroad(keyword=keyword, specialization=specialization, location=location)
            logger.info(f"Scraped {len(workabroad_jobs)} jobs from WorkAbroad.ph")
            jobs.extend(workabroad_jobs)
        
        logger.info(f"Total jobs scraped: {len(jobs)}")
        return jsonify({
            'status': 'success',
            'jobs': jobs
        })
    except Exception as e:
        logger.error(f"Error scraping jobs: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 