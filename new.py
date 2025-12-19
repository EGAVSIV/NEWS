import streamlit as st
import feedparser
import time
from datetime import datetime

# ======================================================
# CONFIG
# ======================================================
REFRESH_INTERVAL_MS = 1000  # 1 second

HIGH_IMPACT_KEYWORDS = [
    "rate cut", "rate hike", "fed", "rbi", "inflation",
    "war", "sanction", "crash", "spike", "ban",
    "emergency", "default", "shutdown"
]

# ======================================================
# RSS FEEDS (FREE SOURCES)
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
# STREAMLIT CONFIG
# ======================================================
st.set_page_config(
    page_title="📡 Market News Intelligence",
    layout="wide"
)

st.title("📡 Indian Market News Intelligence Dashboard")
st.caption("Live News | High Impact Alerts | Multi-Source")

# Auto refresh
st.experimental_autorefresh(
    interval=REFRESH_INTERVAL_MS,
    key="news_refresh"
)

# ======================================================
# INPUTS
# ======================================================
col1, col2, col3 = st.columns(3)

with col1:
    impact_type = st.selectbox(
        "🎯 Impact Type",
        ["📈 Equity (India)", "🛢️ Commodities", "🌍 Global"]
    )

with col2:
    st.markdown("⏱ **Auto Refresh:** 1 second")

with col3:
    st.markdown(f"🕒 **Last Update:** {datetime.now().strftime('%H:%M:%S')}")

# ======================================================
# FETCH & DISPLAY NEWS
# ======================================================
st.divider()
st.subheader(f"📰 Latest News — {impact_type}")

feeds = NEWS_FEEDS[impact_type]
high_impact_found = False

for feed_url in feeds:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link.lower()

        is_high_impact = any(
            kw in title.lower() for kw in HIGH_IMPACT_KEYWORDS
        )

        if is_high_impact:
            high_impact_found = True
            st.error(f"🚨 HIGH IMPACT: {title}")
        else:
            st.success(f"🟢 {title}")

        st.markdown(f"🔗 [Read Full News]({entry.link})")
        st.caption(f"🕒 {entry.get('published', 'Time not available')}")
        st.markdown("---")

# ======================================================
# ALERT SECTION
# ======================================================
if high_impact_found:
    st.toast("🚨 High Impact Market News Detected!", icon="⚠️")
