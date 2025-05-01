import mysql.connector


def connect_to_db():
    """Establish Database connection"""
    return mysql.connector.connect(
        host='Petes',
        user='Peter',
        password='a1-WTPMKG!',
        database='Theatre_Scraper'
    )
def get_or_create_show_id(cursor, show_name, venue):
    """Check if show exists in DB and if not create new ID"""
    cursor.execute('select id from shows where title = %s', (show_name,))
    show = cursor.fetchone()
    if show:
        return show[0]
    else:
        cursor.execute('insert into shows (title, venue) values (%s, %s)', (show_name, venue))
        return cursor.lastrowid
def get_or_create_source_id(cursor, source_name):
    """As above but for source"""
    cursor.execute('select id from sources where source_name = %s', (source_name,))
    source = cursor.fetchone()
    if source:
        return source[0]
    else:
        cursor.execute('insert into sources (source_name) values (%s)', (source_name,))
        return cursor.lastrowid
def insert_review_if_not_exists(cursor, show_id, source_id, date, rating, sentiment_score):
    """Checks DB to make sure no duplicate reviews are inserted and then inserts review"""
    cursor.execute("""
        SELECT id FROM reviews 
        WHERE show_id = %s AND source_id = %s AND date = %s AND rating = %s
    """, (show_id, source_id, date, rating))
    existing_review = cursor.fetchone()

    if not existing_review:
        cursor.execute("""
            INSERT INTO reviews (show_id, source_id, date, rating, sentiment_score)
            VALUES (%s, %s, %s, %s, %s)
        """, (show_id, source_id, date, rating, sentiment_score))
        return True  # Review inserted
    return False  # Review already exists