import requests
from flask import Flask, render_template
from textblob import TextBlob
import logging
import json
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

# Path to cache file
CACHE_FILE = 'news_cache.json'

# Function to check if cache is valid (less than 24 hours old)
def is_cache_valid():
    if os.path.exists(CACHE_FILE):
        mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        return datetime.now() - mod_time < timedelta(days=1)
    return False

# Function to fetch news from NewsAPI
def fetch_news(api_key):
    try:
        NEWSAPI_URL = 'https://newsapi.org/v2/everything'
        query_params = {
            'q': 'politics',  # Keywords or phrases to search for in the article title and body
            'language': 'en',  # Language of the news
            'sortBy': 'publishedAt',  # Sort by the published date
            'apiKey': '6d1d6e73a1134ce59ba497f77e632236'  # Your API key
        }
        response = requests.get(NEWSAPI_URL, params=query_params)
        response.raise_for_status()  # Raise an error for bad responses
        news_data = response.json()
        with open(CACHE_FILE, 'w') as file:
            json.dump(news_data, file)
        return news_data
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return {'articles': []}

# Function to load news from cache
def load_cached_news():
    try:
        with open(CACHE_FILE, 'r') as file:
            news_data = json.load(file)
        return news_data
    except Exception as e:
        logging.error(f"Error loading cached news: {e}")
        return {'articles': []}

# Function to analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    # Classify sentiment as positive, negative, or neutral
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Load news data from cache or fetch new data
if is_cache_valid():
    news_data = load_cached_news()
else:
    API_KEY = '6d1d6e73a1134ce59ba497f77e632236'  # Replace with your NewsAPI key
    news_data = fetch_news(API_KEY)

# Extract articles and analyze sentiment
articles = []
for article in news_data['articles']:
    if article['title']:
        # Analyze sentiment of the article title
        sentiment = analyze_sentiment(article['title'])
        # Add article to list with sentiment
        articles.append({'title': article['title'], 'url': article['url'], 'sentiment': sentiment})

# Function to count sentiments
def count_sentiments(articles):
    mood_data = {'Red': 0, 'Blue': 0, 'Neutral': 0}
    for article in articles:
        if 'cnn' in article['url'].lower():
            if article['sentiment'] == 'Positive':
                mood_data['Blue'] += 1
            elif article['sentiment'] == 'Negative':
                mood_data['Red'] += 1
            else:
                mood_data['Neutral'] += 1
        elif 'fox' in article['url'].lower():
            if article['sentiment'] == 'Positive':
                mood_data['Red'] += 1
            elif article['sentiment'] == 'Negative':
                mood_data['Blue'] += 1
            else:
                mood_data['Neutral'] += 1
    total = sum(mood_data.values())
    if total > 0:
        mood_data = {k: (v / total) * 100 for k, v in mood_data.items()}
    return mood_data

# Calculate sentiment counts
mood_data = count_sentiments(articles)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', mood_data=mood_data, articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
