from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup
import random
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import os

# Define the paths for your CSV files (main project directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # Current directory of the script
DATA_DIR = os.path.join(BASE_DIR, 'data')  # The 'data' directory in the main folder

WOS_REVIEW_URLS_PATH = os.path.join(DATA_DIR, 'wos_review_urls.csv')
WOS_REVIEW_URLS_ARCHIVE_PATH = os.path.join(DATA_DIR, 'wos_review_urls_archive.csv')

TS_REVIEW_URLS_PATH = os.path.join(DATA_DIR, 'TS_review_urls.csv')
TS_REVIEW_URLS_ARCHIVE_PATH = os.path.join(DATA_DIR, 'TS_review_urls_archive.csv')

LT1_REVIEW_URLS_PATH = os.path.join(DATA_DIR, 'lt1_review_urls.csv')
LT1_REVIEW_URLS_ARCHIVE_PATH = os.path.join(DATA_DIR, 'lt1_review_urls_archive.csv')

def load_url_archive_csv(csv_file):
    """Convenience function that allows loading of ALL previous reviews"""
    try:
        df = pd.read_csv(csv_file)
        return set(df['Review URL'].dropna().str.strip())
    except FileNotFoundError:
        return set()
def get_review_links_WOS(max_clicks=1):
    """Loads first and second pages of new reviews on WhatsOnStage, and collects the urls to pass to the scraper"""
    archived_urls = load_url_archive_csv(WOS_REVIEW_URLS_ARCHIVE_PATH)

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get('https://www.whatsonstage.com/news/?categories=reviews')

    new_urls = set()

    for i in range(max_clicks):
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.startswith("https://www.whatsonstage.com/news/") and "-review" in href:
                if href not in archived_urls:
                    new_urls.add(href)

        try:
            load_more = driver.find_element(By.ID, 'load-more-news')
            driver.execute_script('arguments[0].click();', load_more)
            time.sleep(random.uniform(3, 5))
        except NoSuchElementException:
            print(f"Stopped after {i + 1} clicks — no more button found.")
            break

    driver.quit()

    # Save the new URLs to the working file
    if new_urls:
        df_new = pd.DataFrame(new_urls, columns=['Review URL'])
        df_new.to_csv(WOS_REVIEW_URLS_PATH, index=False)
        print(f"Saved {len(new_urls)} new URLs to working file (wos_review_urls.csv).")

        # Update archive (only if there were new ones)
        combined_urls = archived_urls.union(new_urls)
        df_archive = pd.DataFrame(combined_urls, columns=['Review URL'])
        df_archive.to_csv(WOS_REVIEW_URLS_ARCHIVE_PATH, index=False)
        print(f"Updated archive (wos_review_urls_archive.csv) with total {len(combined_urls)} URLs.")

    else:
        print("No new 'WhatsOnStage' URLs found. Working file and archive left unchanged.")

    return list(new_urls)
def get_review_links_TS(max_clicks=1):
    """As above but for TheStage"""
    archived_urls = load_url_archive_csv(TS_REVIEW_URLS_ARCHIVE_PATH)

    options = Options()
    options.add_argument('--headless')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://www.thestage.co.uk/reviews')

    try:
        accept_btn = driver.find_element(By.XPATH, "//button[normalize-space(text())='Accept All Cookies']")
        driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)
        time.sleep(1)
        accept_btn.click()
    except NoSuchElementException:
        print("No cookie popup found.")

    new_urls = set()

    for i in range(max_clicks):
        try:
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and '/review' in href and 'https://www.thestage.co.uk/' in href:
                        if href not in archived_urls:
                            new_urls.add(href)
                except StaleElementReferenceException:
                    continue

        except Exception as e:
            print(f"Unexpected error while processing links: {e}")
            continue

        try:
            load_more = driver.find_element(By.CLASS_NAME, 'aos-LoadMoreDE')
            driver.execute_script('arguments[0].click();', load_more)
            time.sleep(random.uniform(3, 5))
        except NoSuchElementException:
            print(f"Stopped after {i + 1} clicks — no more button found.")
            break

    driver.quit()

    # Save the *new* URLs to the working file
    if new_urls:
        df_new = pd.DataFrame(new_urls, columns=['Review URL'])
        df_new.to_csv(TS_REVIEW_URLS_PATH, index=False)
        print(f"Saved {len(new_urls)} new URLs to working file (TS_review_urls.csv).")

        # Update archive
        combined_urls = archived_urls.union(new_urls)
        df_archive = pd.DataFrame(combined_urls, columns=['Review URL'])
        df_archive.to_csv(TS_REVIEW_URLS_ARCHIVE_PATH, index=False)
        print(f"Updated archive (TS_review_urls_archive.csv) with total {len(combined_urls)} URLs.")
    else:
        print("No new 'The Stage' URLs found. Working file and archive left unchanged.")
    return list(new_urls)
def get_review_links_lt1(max_pages=1):
    """As above but for LondonTheatre1"""
    base_url = "https://www.londontheatre1.com/reviews/page/"

    df_archive = pd.read_csv(LT1_REVIEW_URLS_ARCHIVE_PATH)
    archived_urls = set(df_archive['Review URL'].tolist())
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    new_urls = set()

    for page_num in range(1, max_pages + 1):
        url = f'{base_url}{page_num}/'
        driver.get(url)
        time.sleep(3)
        page_content = driver.page_source

        soup = BeautifulSoup(page_content, 'html.parser')
        review_links = soup.find_all("a", href=True, rel="bookmark")
        print(f"Scraping page {page_num}... Found {len(new_urls)} URLs so far.")

        for link in review_links:
            review_url = link["href"]
            if review_url not in archived_urls:
                new_urls.add(review_url)
    driver.quit()

    # Save new URLs to the working file (CSV)
    if new_urls:
        df_new = pd.DataFrame(list(new_urls), columns=['Review URL'])
        df_new.to_csv(LT1_REVIEW_URLS_PATH, index=False)
        print(f"Saved {len(new_urls)} new URLs to {LT1_REVIEW_URLS_PATH}.")

        # Update archive with new URLs
        all_urls = archived_urls.union(new_urls)
        df_archive = pd.DataFrame(list(all_urls), columns=['Review URL'])
        df_archive.to_csv(LT1_REVIEW_URLS_ARCHIVE_PATH, index=False)
        print(f"Updated archive with total {len(all_urls)} URLs.")
    else:
        print("No new URLs found. Working file and archive left unchanged.")

    return list(new_urls)