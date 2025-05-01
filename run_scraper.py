from utils.utils import log_schedule
from scrapers import url_getter as urls
from scrapers.wos_scraper import wos_scraper
from scrapers.ts_scraper import ts_scraper
from scrapers.lt1_scraper import lt1_scraper
from pipeline.pipeline import pipeline

def main():
    try:
        urls.get_review_links_WOS()
        urls.get_review_links_TS()
        urls.get_review_links_lt1()
        new1 = pipeline('data/wos_review_urls.csv', wos_scraper)
        new2 = pipeline('data/TS_review_urls.csv', ts_scraper)
        new3 = pipeline('data/lt1_review_urls.csv', lt1_scraper)
        reviews_added = new1 + new2 + new3
        log_schedule(f'Scraper run successfully - {reviews_added} review(s) added.')
    except Exception as e:
        log_schedule(f'Script failed with error: {e}')
        raise

if __name__ == '__main__':
    main()