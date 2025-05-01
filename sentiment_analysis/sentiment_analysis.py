import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

def analyse_review(review):
    """Breaks down reviews into sentences, analyses sentiment of each review"""
    analyser = SentimentIntensityAnalyzer()
    sentences = nltk.sent_tokenize(review)
    sentiment_results = []

    for sentence in sentences:
        sentiment = analyser.polarity_scores(sentence)
        sentiment_results.append({
            'sentence': sentence,
            'sentiment': sentiment
        })

    SS = np.mean([s['sentiment']['compound'] for s in sentiment_results])
    return SS

