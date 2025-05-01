This project automates the extraction of theatre show reviews from websites like WhatsOnStage and LondonTheatre1. It performs sentiment analysis using VADER and stores the cleaned data in a relational MySQL database, enabling structured querying, sentiment tracking, and future insights (like ranking shows by sentiment over time).


In the DB file, the local credentials are removed (obvs), but the rest of the code is designed to work anywhere with a viable MySQL connection setup

As of 01/05/25, this project is a WIP - plans are to scale up with more review sites and little fixes here and there

Tech Stack: 
- BeautifulSoup4
- requests
- vaderSentiment
- nltk
- mysql-connector-python
- pandas
- PyCharm/Jupyter
- venv

Example Output:

| Show           | Source       | Review Excerpt                    | Sentiment | Rating |
|----------------|--------------|-----------------------------------|-----------|-----|
| Hamlet         | WhatsOnStage | "A gripping, emotionally raw..." | 0.76      | 4   |
| Six the Musical| TheStage     | "Fun, feminist, and fresh"       | 0.91      | 5   |