from db.mysql_integration import connect_to_db
from db.mysql_integration import get_or_create_show_id
from db.mysql_integration import get_or_create_source_id
from db.mysql_integration import insert_review_if_not_exists
from sentiment_analysis.sentiment_analysis import analyse_review
import pandas as pd

def insert_reviews(df):
    conn = connect_to_db()
    cursor = conn.cursor()
    reviews_added = 0

    for index, row in df.iterrows():
        show_id = get_or_create_show_id(cursor, row['Show Name'], row['Venue'])
        source_id = get_or_create_source_id(cursor, row['Source'])
        inserted = insert_review_if_not_exists(cursor, show_id, source_id, row['Date'], row['Rating'], row['Sentiment Score'])
        if inserted:
            reviews_added += 1

    conn.commit()
    cursor.close()
    conn.close()

    if reviews_added > 0:
        print(f"{reviews_added} review(s) added.")
    else:
        print("No reviews added.")

    return reviews_added
def process_reviews(urls, scraper):
    data = []
    total = len(urls)

    for i, url in enumerate(urls, start=1):
        review = scraper(url)
        if review is None:
            print(f"Skipping URL due to scrape failure")
            continue
        ss = analyse_review(review['Review'])
        data.append({
            'Show Name': review['Show Name'],
            'Venue': review['Venue'],
            'Date': review['Date'],
            'Rating': review['Rating'],
            'Sentiment Score': ss,
            'Source': review['Source']
        })
        print(f"Processed {i} of {total}")

    df = pd.DataFrame(data)
    df = df.dropna(subset=['Show Name', 'Venue', 'Date', 'Rating', 'Source'])
    return df
def pipeline(reviews_csv, scraper):
    # Read
    df = pd.read_csv(reviews_csv)
    review_urls = df['Review URL'].tolist()

    # Process
    processed_reviews = process_reviews(review_urls, scraper)

    # Insert
    inserted_reviews = insert_reviews(processed_reviews)

    return inserted_reviews