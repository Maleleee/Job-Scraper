# PH Job Scraper

A Flask web application that aggregates job listings from Philippine job websites:
- HireMe.ph (Local Jobs)
- WorkAbroad.ph (Overseas Jobs)

## Features
- Search jobs by keyword and location
- Filter by local or overseas positions
- Select job specializations
- Real-time job scraping
- Responsive web interface

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open `http://localhost:5000` in your browser

3. Use the search form to:
   - Enter job keywords
   - Select specialization
   - Choose location type (Local/Overseas)
   - Specify location

## Disclaimer

This application is for educational purposes only. Please respect the terms of service of the websites being scraped.

## Project Structure

```
Job-Scraper/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── scrapers/             # Scraper modules
│   ├── base_scraper.py   # Base scraper class
│   ├── hireme_scraper.py # HireMe.ph scraper
│   └── workabroad_scraper.py # WorkAbroad.ph scraper
└── templates/            # HTML templates
    └── index.html       # Main page template
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
 
