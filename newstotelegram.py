import requests
import feedparser
import hashlib
import json
from datetime import datetime
from pathlib import Path

# ======================================================
# TELEGRAM CONFIG
# ======================================================

BOT_TOKEN = "YOUR_BOT_TOKEN"

CHAT_IDS = [
    "5332984891",
    "-1002622207173"
]

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ======================================================
# HASH STORAGE
# ======================================================

HASH_FILE = Path("sent_news.json")

if HASH_FILE.exists():
    with open(HASH_FILE, "r") as f:
        sent_hashes = set(json.load(f))
else:
    sent_hashes = set()


# ======================================================
# TELEGRAM FUNCTION
# ======================================================

def send_telegram(message):

    for chat in CHAT_IDS:

        payload = {
            "chat_id": chat,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            requests.post(TELEGRAM_URL, data=payload, timeout=10)
        except Exception as e:
            print("Telegram Error:", e)


# ======================================================
# HIGH IMPACT KEYWORDS
# ======================================================

HIGH_IMPACT_KEYWORDS = [
    "rate cut", "rate hike", "fed", "rbi", "inflation",
    "war", "sanction", "crash", "spike", "ban",
    "emergency", "default", "shutdown"
]


# ======================================================
# RSS SOURCES
# ======================================================

NEWS_FEEDS = {

    "📈 Equity (India)": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.moneycontrol.com/rss/marketreports.xml",
        "https://www.business-standard.com/rss/markets-106.rss"
    ],

    "🛢️ Commodities": [
        "https://economictimes.indiatimes.com/commodity/rssfeeds/1167488.cms",
        "https://oilprice.com/rss/main",
        "https://www.kitco.com/rss/news"
    ],

    "🌍 Global": [
        "https://www.reuters.com/rssFeed/worldNews",
        "https://www.reuters.com/rssFeed/businessNews",
        "https://www.cnbc.com/id/100727362/device/rss/rss.html"
    ]
}


# ======================================================
# SCAN NEWS
# ======================================================

def scan_news():

    global sent_hashes

    for category, feeds in NEWS_FEEDS.items():

        for feed_url in feeds:

            try:

                feed = feedparser.parse(feed_url, agent="Mozilla/5.0")

                for entry in feed.entries[:10]:

                    title = entry.title
                    link = entry.link
                    published = entry.get("published", "Unknown")

                    news_hash = hashlib.sha256(title.encode()).hexdigest()

                    # Skip already sent
                    if news_hash in sent_hashes:
                        continue

                    sent_hashes.add(news_hash)

                    is_high_impact = any(
                        kw in title.lower() for kw in HIGH_IMPACT_KEYWORDS
                    )

                    now = datetime.now().strftime("%Y-%m-%d %H:%M")

                    if is_high_impact:

                        message = f"""
🚨 <b>HIGH IMPACT NEWS</b>

📊 <b>{category}</b>

📰 <b>{title}</b>

🔗 {link}

🕒 {published}
⏱ Bot: {now}
"""

                    else:

                        message = f"""
📰 <b>Market News</b>

📊 {category}

{title}

🔗 {link}
"""

                    print("Sending:", title)

                    send_telegram(message)

            except Exception as e:
                print("Feed Error:", e)


# ======================================================
# SAVE HASH FILE
# ======================================================

def save_hashes():

    with open(HASH_FILE, "w") as f:
        json.dump(list(sent_hashes), f)


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    scan_news()
    save_hashes()
