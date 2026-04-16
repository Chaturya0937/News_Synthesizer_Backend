import requests
from dotenv import load_dotenv
import os
load_dotenv()
Api_key = os.getenv("NEWSAPI")

def get_news_from_NewsApi(Topic):
    response=requests.get(f'https://newsapi.org/v2/everything?q={Topic}&apiKey={Api_key}&pagesize=10')
    data=response.json()
    return data["articles"]
