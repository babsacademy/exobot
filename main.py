import requests
import json
import re
from datetime import datetime
from database import conn
import html

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
}

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

urls = {
    "wiwsport": "https://wiwsport.com/wp-json/wp/v2/posts?embed",
    "senego": "https://senego.com/wp-json/wp/v2/posts?embed",
    "senenews": "https://www.senenews.com/wp-json/wp/v2/posts?embed",
    "aps": "https://aps.sn/wp-json/wp/v2/posts?embed","xalimasn":"https://www.xalimasn.com/wp-json/wp/v2/posts?embed",
}

for site_name, url in urls.items():
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        data = response.json()

        new_articles = []

        for article in data:
            cursor = conn.execute("SELECT * FROM articles WHERE slug=? AND site_name=?", (article["slug"], site_name,))
            existing_article = cursor.fetchone()
            if existing_article is None:
                photo_url = None
                if "better_featured_image" in article:
                    photo_url = article["better_featured_image"]["source_url"]
                elif "featured_media" in article["_links"]:
                    media_url = article["_links"]["wp:featuredmedia"][0]["href"]
                    media_response = requests.get(media_url, headers=headers)
                    if media_response.status_code == 200:
                        media_data = media_response.json()
                        photo_url = media_data["source_url"]
                
                if not photo_url:
                    # no photo found, use placeholder image
                    photo_url = "https://firebasestorage.googleapis.com/v0/b/dakarois221-94a4b.appspot.com/o/images%2F_2ab23759-756f-424a-a7be-10ddb876370a.jpeg?alt=media&token=1cd4e1c0-0b04-4aa1-9952-43d9cc6efcb7"
                
                # Formatting the date
                article_date = datetime.strptime(article["date"], '%Y-%m-%dT%H:%M:%S')
                formatted_date = article_date.strftime('%d/%m/%Y %H:%M')

                # Encoding the title and removing "&#8230" from the title
                encoded_title = html.unescape(article["title"]["rendered"])

                article_data = {
                    "title": encoded_title,
                    "content": re.sub(r'<video.*?>.*?</video>', '', article["content"]["rendered"], flags=re.DOTALL),
                    "slug": article["slug"],
                    "photo": photo_url,
                    "date": formatted_date,
                    "link": article["link"],
                    "site_name": site_name
                }
                new_articles.append(article_data)

                conn.execute("""
                INSERT INTO articles (title, content, slug, photo, date, link, site_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (article_data["title"], article_data["content"], article_data["slug"], article_data["photo"], article_data["date"], article_data["link"], article_data["site_name"]))
        conn.commit()
        print(f"{len(new_articles)} nouveaux articles ajoutés pour le site {url}.")
