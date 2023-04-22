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
    link TEXT,
    site TEXT
)
""")

urls = ["https://wiwsport.com/wp-json/wp/v2/posts?embed", "https://senego.com/wp-json/wp/v2/posts?embed","https://www.senenews.com/wp-json/wp/v2/posts?embed"]

for url in urls:
    site = url.split('/')[2]
    r = requests.get(url, headers=headers)
    data = json.loads(r.text)
    
    for post in data:
        title = post['title']['rendered']
        content = post['content']['rendered']
        slug = post['slug']
        
        if '_embedded' in post and 'wp:featuredmedia' in post['_embedded']:
            photo = post['_embedded']['wp:featuredmedia'][0]['source_url']
        else:
            photo = 'https://via.placeholder.com/150'
            
        date = post['date']
        link = post['link']
        
        conn.execute("INSERT INTO articles (title, content, slug, photo, date, link, site) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, content, slug, photo, date, link, site))
        conn.commit()
    
    print(f"Les données du site {site} ont été insérées dans la base de données avec succès.")

conn.close()
