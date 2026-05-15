import requests
import os
from dotenv import load_dotenv

load_dotenv()
GNEWS_API_KEY = os.getenv("GNEWS")

def get_news_from_GNews(Topic):
    # Fixed static search string to dynamically accept the optimized Topic string
    url = f"https://gnews.io/api/v4/search?q={Topic}&lang=en&max=5&apikey={GNEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "articles" in data:
        return data["articles"]
    return []
