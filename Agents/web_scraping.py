import feedparser
import requests
from newspaper import Article
from urllib.parse import quote

query = "TamilNadu Elections"

encoded_query = quote(query)

rss_url = (
    f"https://news.google.com/rss/search?q={encoded_query}"
)

print(rss_url)

feed = feedparser.parse(rss_url)

articles = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

for entry in feed.entries[:10]:

    try:

        # Google redirect URL
        google_url = entry.link

        # Resolve redirect
        response = requests.get(
            google_url,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )

        real_url = response.url

        print("\nREAL URL:")
        print(real_url)

        article = Article(real_url)

        article.download()
        article.parse()

        print("TEXT LENGTH:", len(article.text))

        if len(article.text) > 200:

            articles.append({
                "title": article.title,
                "url": real_url,
                "text": article.text
            })

            print("SUCCESS:", article.title)

    except Exception as e:

        print("FAILED")
        print(e)

print("\nTotal Articles:", len(articles))