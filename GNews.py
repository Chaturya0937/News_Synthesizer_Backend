import requests
import os
from dotenv import load_dotenv

load_dotenv()
GNEWS=os.getenv("GNEWS")

def get_news_from_GNews(Topic):
        
    url=f"https://gnews.io/api/v4/search?q=T20WorldCUP&lang=en&max=5&apikey=32a243c637838edf40a22936571762ae"
    response=requests.get(url)
    data = response.json()
    return data["articles"]
