import feedparser
import requests
import time
import json
import os
import re
from datetime import datetime

BALE_TOKEN = "669282757:PCpSAdchCn3PQQYDqFmMrJU7FzIizOVt7as"
CHANNEL_ID = "@atraknews"

RSS_SOURCES = {
    "ایسنا": {"url": "https://www.isna.ir/rss", "icon": "🔵"},
    "مهر": {"url": "https://www.mehrnews.com/rss", "icon": "🔴"},
    "ایرنا": {"url": "https://www.irna.ir/rss", "icon": "🟢"},
    "فارس": {"url": "https://www.farsnews.ir/rss", "icon": "🟡"},
    "تسنیم": {"url": "https://www.tasnimnews.com/fa/rss/feed/0/7/0/%D8%A2%D8%AE%D8%B1%DB%8C%D9%86-%D8%A7%D8%AE%D8%A8%D8%A7%D8%B1-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86-%D9%88-%D8%AC%D9%87%D8%A7%D9%86", "icon": "🟠"},
    "خبرآنلاین": {"url": "https://www.khabaronline.ir/rss", "icon": "🟣"},
    "تابناک": {"url": "https://www.tabnak.ir/fa/rss/allnews", "icon": "⚫"},
}

SEEN_FILE = "seen_news.json"

def load_seen_news():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_seen_news(seen):
    seen = seen[-500:]
    with open(SEEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(seen, f, ensure_ascii=False)

def send_to_bale(text):
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def fetch_rss(source_name, source_info, seen_links):
    news_list = []
    try:
        print(f"📡 {source_name}...")
        feed = feedparser.parse(source_info["url"])
        for entry in feed.entries[:10]:
            link = entry.get('link', '')
            title = entry.get('title', 'بدون عنوان')
            if link in seen_links:
                continue
            published = entry.get('published', entry.get('updated', 'تاریخ نامشخص'))
            summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
            if len(summary) > 200:
                summary = summary[:200] + "..."
            news_list.append({
                "source": source_name,
                "icon": source_info["icon"],
                "title": title,
                "link": link,
                "published": published,
                "summary": summary
            })
            seen_links.append(link)
    except Exception as e:
        print(f"❌ {source_name}: {e}")
    return news_list

def format_message(news):
    return f"""
{news['icon']} <b>{news['source']}</b>

📰 {news['title']}

🕐 {news['published']}

🔗 <a href='{news['link']}'>مشاهده خبر کامل</a>

#اخبار #{news['source'].replace(' ', '_')}
""".strip()

def main():
    print(f"🤖 شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    seen_links = load_seen_news()
    all_new_news = []
    for source_name, source_info in RSS_SOURCES.items():
        news_items = fetch_rss(source_name, source_info, seen_links)
        all_new_news.extend(news_items)
        time.sleep(2)
    print(f"📬 {len(all_new_news)} خبر جدید")
    sent_count = 0
    for news in all_new_news:
        if send_to_bale(format_message(news)):
            sent_count += 1
        time.sleep(3)
    save_seen_news(seen_links)
    print(f"✅ {sent_count} خبر ارسال شد")

if __name__ == "__main__":
    main()
