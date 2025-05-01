from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def lt1_scraper(url):
    try:
        # Set up headless Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # Wait until the title is present or timeout
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "entry-title"))
        )

        # Parse the page source after JS has loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        # Extract title
        title_tag = soup.find('h1', class_="entry-title")
        if not title_tag:
            print(f"Title not found on {url}")
            return None
        title = title_tag.get_text(strip=True)

        # Attempt to extract show name and venue
        extracted = pd.Series([title]).str.extract(r'^(.*?)\s+[–-]\s+(.*?)\s+\|\s*Review$', expand=True)
        show_name = extracted[0][0].strip() if pd.notna(extracted[0][0]) else None
        venue = extracted[1][0].strip() if pd.notna(extracted[1][0]) else None

        # Extract publication date
        date_tag = soup.find('span', class_='published', itemprop='datePublished')
        if date_tag:
            try:
                date_str = date_tag.get_text(strip=True)
                date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
            except:
                date = None
        else:
            date = None

        # Remove author bio box if it exists
        author_box = soup.find('div', class_='pp-multiple-authors-boxes-wrapper')
        if author_box:
            author_box.decompose()

        # Extract review content
        body_tag = soup.find('div', class_='entry-content clear')
        paragraphs = []
        if body_tag:
            for p in body_tag.find_all('p'):
                strongs = p.find_all('strong')
                if len(strongs) >= 2 or p.find('br'):
                    continue
                text = p.get_text(strip=True)
                if text:
                    paragraphs.append(text)
            review_text = ' '.join(paragraphs)
        else:
            review_text = None

        # Extract rating from star image alt text
        rating_img = soup.find('img', alt=lambda x: x and 'star' in x.lower())
        if rating_img:
            try:
                rating = int(rating_img['alt'].strip()[0])
            except:
                rating = None
        else:
            rating = None

        return {
            'URL': url,
            'Show Name': show_name,
            'Venue': venue,
            'Date': date,
            'Review': review_text,
            'Rating': rating,
            'Source': 'LondonTheatre1'
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None