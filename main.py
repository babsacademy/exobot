import sqlite3
import requests
import json
import re
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
}

conn = sqlite3.connect("articles.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    slug TEXT,
    photo TEXT,
    date TEXT,
    link TEXT,
    site_name TEXT
)
""")

urls = ["https://wiwsport.com/wp-json/wp/v2/posts?embed", "https://senego.com/wp-json/wp/v2/posts?embed", "https://www.senenews.com/wp-json/wp/v2/posts?embed"]

for url in urls:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        data = response.json()

        new_articles = []

        for article in data:
            cursor = conn.execute("SELECT * FROM articles WHERE slug=? AND site_name=?", (article["slug"], url,))
            existing_article = cursor.fetchone()
            if existing_article is None:
                if "_embedded" in article and "wp:featuredmedia" in article["_embedded"]:

                    photo_url = article["_embedded"]["wp:featuredmedia"][0]["source_url"]
                else:

                    photo_url = None

                # Formatting the date
                article_date = datetime.strptime(article["date"], '%Y-%m-%dT%H:%M:%S')
                formatted_date = article_date.strftime('%d/%m/%Y %H:%M')

                # Encoding the title and removing "&#8230" from the title
                encoded_title = article["title"]["rendered"].encode('ascii', 'ignore').decode()
                clean_title = re.sub(r'&#8230;', '', encoded_title)

                article_data = {
                    "title": clean_title,
                    "content": re.sub(r'<video.*?>.*?</video>', '', article["content"]["rendered"], flags=re.DOTALL),
                    "slug": article["slug"],
                    "photo": photo_url,
                    "date": formatted_date,
                    "link": article["link"],
                    "site_name": url
                }
                new_articles.append(article_data)

                conn.execute("""
                INSERT INTO articles (title, content, slug, photo, date, link, site_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (article_data["title"], article_data["content"], article_data["slug"], article_data["photo"], article_data["date"], article_data["link"], article_data["site_name"]))
        conn.commit()

        print(f"{len(new_articles)} nouveaux articles ajoutés pour le site {url}.")
    else:
        print("Erreur de requête HTTP : le code de statut est {}".format(response.status_code))

conn.close()
