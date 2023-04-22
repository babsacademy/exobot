
import sqlite3
import requests
import json

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
    link TEXT
)
""")

urls = ["https://wiwsport.com/wp-json/wp/v2/posts?embed", "https://senego.com/wp-json/wp/v2/posts?embed","https://www.senenews.com/wp-json/wp/v2/posts?embed"]

for url in urls:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        data = response.json()

        new_articles = []

        for article in data:
            cursor = conn.execute("SELECT * FROM articles WHERE slug=?", (article["slug"],))
            existing_article = cursor.fetchone()
            if existing_article is None:
                if "_embedded" in article and "wp:featuredmedia" in article["_embedded"]:

                    photo_url = article["_embedded"]["wp:featuredmedia"][0]["source_url"]
                else:

                    photo_url = None

                article_data = {
                    "title": article["title"]["rendered"],
                    "content": article["content"]["rendered"],
                    "slug": article["slug"],
                    "photo": photo_url,
                    "date": article["date"],
                    "link": article["link"]
                }
                new_articles.append(article_data)


                conn.execute("""
                INSERT INTO articles (title, content, slug, photo, date, link)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (article_data["title"], article_data["content"], article_data["slug"], article_data["photo"], article_data["date"], article_data["link"]))
        conn.commit()

        print(f"{len(new_articles)} nouveaux articles ajoutés.")
    else:
        print("Erreur de requête HTTP : le code de statut est {}".format(response.status_code))

conn.close()