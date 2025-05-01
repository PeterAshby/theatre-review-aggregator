import requests
from bs4 import BeautifulSoup
import pandas as pd

def wos_scraper(url):
    """Web scraper designed to retrieve relevant review information from WhatsOnStage"""
    try:
        # Get HTML
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Extract title
        title = soup.find('h1').get_text(strip=True)

        # Attempt to extract show name and venue
        # Normalize spacing and format
        title = title.replace('at ', ' at ')
        extracted = pd.Series(title).str.extract(r'^(.*?) at (.*?)\s+– review$')

        show_name = extracted[0].values[0] if extracted[0].notna().values[0] else None
        show_name = show_name.replace("Musical", "").replace("musical", "").strip()
        venue = extracted[1].values[0] if extracted[1].notna().values[0] else None

        # Clean venue and show name
        if venue:
            venue = venue.replace('the', 'The').strip()
        if show_name:
            show_name = show_name.replace('"', '').replace('“', '').replace('”', '').strip()

        # Extract date
        date_tag = soup.find('p', id='article-date-tag')
        date = pd.to_datetime(date_tag.get_text(strip=True), errors='coerce').strftime('%Y-%m-%d') if date_tag else None

        # Extract review text
        body_tag = soup.find('div', class_='news-content')
        review_text = body_tag.get_text(strip=True) if body_tag else ''

        # Star rating logic
        stars = soup.find_all('svg', style=True)
        filled_stars = sum(1 for star in stars if 'fill: gray' not in star['style'])
        rating = filled_stars if filled_stars > 0 else None

        return {
            'URL': url,
            'Show Name': show_name,
            'Venue': venue,
            'Date': date,
            'Review': review_text,
            'Rating': rating,
            'Source': 'WhatsOnStage'
        }

    except Exception as e:
        print(f'Error scraping {url}: {e}')
        return None