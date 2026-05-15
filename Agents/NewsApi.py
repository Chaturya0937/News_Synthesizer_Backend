import requests
from dotenv import load_dotenv
import os

load_dotenv()
Api_key = os.getenv("NEWSAPI")

def get_news_from_NewsApi(Topic):
    # Using python f-string correctly to inject the generated query topic
    url = f'https://newsapi.org/v2/everything?q={Topic}&apiKey={Api_key}&pageSize=10'
    response = requests.get(url)
    data = response.json()
    
    if "articles" in data:
        return data["articles"]
    return []
