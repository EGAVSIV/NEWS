import streamlit as st
import feedparser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import hashlib
import time
import base64

# ======================================================
# SOUND MAP (Different sound per category)
# ======================================================
SOUND_MAP = {
    "📈 Equity (India)": "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg",
    "🛢️ Commodities": "https://actions.google.com/sounds/v1/alarms/beep_short.ogg",
    "🌍 Global": "https://actions.google.com/sounds/v1/alarms/siren_whistle.ogg",
}

def play_alert_sound(category):
    sound_url = SOUND_MAP.get(category)

    if sound_url:
        st.markdown(
            f"""
            <audio autoplay>
                <source src="{sound_url}" type="audio/ogg">
            </audio>
            """,
            unsafe_allow_html=True
        )



def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

USERS = st.secrets["users"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and hash_pwd(p) == USERS[u]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()


if "seen_news_hashes" not in st.session_state:
    st.session_state.seen_news_hashes = set()



# ======================================================
# CONFIG
# ======================================================
REFRESH_INTERVAL_MS = 60000  # 1 second

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
        "https://www.kitco.com/rss/news",
        "https://www.reuters.com/markets/commodities/energy",
        "https://lngjournal.com",
        "https://www.fxempire.com/commodities/natural-gas",
        "https://www.investing.com/news/commodities-news",
        "https://oilprice.com/Energy/Energy-General",
        "https://www.alcircle.com/news"
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
    page_title="📰 Market News Intelligence",
    layout="wide",
    page_icon="🗞️"
)

# 🔄 MANUAL + AUTO REFRESH (NO EXTERNAL LIB)
# =====================================================
c1, c2, c3 = st.columns([1.2, 1.8, 6])

with c1:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

with c2:
    auto_refresh = st.toggle("⏱ Auto Refresh (5 min)", value=False)

with c3:
    st.caption("Manual refresh forces fresh NOAA weather + NG demand recalculation")
# =====================================================
# AUTO REFRESH TIMER (SAFE)
# =====================================================
if auto_refresh:
    now = time.time()
    last = st.session_state.get("last_refresh", 0)

    if now - last > 5 * 60:  # 30 minutes
        st.session_state["last_refresh"] = now
        st.cache_data.clear()
        st.rerun()


st.title("📡 Indian Market News Intelligence Dashboard")
st.caption("Live News | High Impact Alerts | Multi-Source")
col_logo, col_ticker = st.columns([0.22, 0.78]) 
with col_logo: 
    st.image("Assets/sgy1.png", width=220)


# ✅ CORRECT AUTO-REFRESH
st_autorefresh(
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
        list(NEWS_FEEDS.keys())
    )

with col2:
    st.markdown("⏱ **Auto Refresh:** Every 1 Minute")

with col3:
    st.markdown(f"🕒 **Last Update:** {datetime.now().strftime('%H:%M:%S')}")

# ======================================================
# FETCH & DISPLAY NEWS
# ======================================================
st.divider()
st.subheader(f"📰 Latest News — {impact_type}")

high_impact_found = False

for feed_url in NEWS_FEEDS[impact_type]:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link

        news_hash = hashlib.sha256(title.encode()).hexdigest()
        is_high_impact = any(
            kw in title.lower() for kw in HIGH_IMPACT_KEYWORDS
        )
        is_new_news = news_hash not in st.session_state.seen_news_hashes
        if is_high_impact:
            st.error(f"🚨 HIGH IMPACT: {title}")

        if is_high_impact:
            high_impact_found = True
            st.error(f"🚨 HIGH IMPACT: {title}")
            if is_new_news:
                high_impact_found = True
                play_alert_sound(impact_type)
                st.session_state.seen_news_hashes.add(news_hash)
        else:
            st.success(f"🟢 {title}")

        st.markdown(f"🔗 [Read Full News]({link})")
        st.caption(f"🕒 {entry.get('published', 'Time not available')}")
        st.markdown("---")

# ======================================================
# ALERT
# ======================================================
if high_impact_found:
    st.toast("🚨 NEW High Impact Market News Detected!", icon="⚠️")

    if not st.session_state.alert_played:
        play_alert_sound()
        st.session_state.alert_played = True
else:
    # Reset flag when no high impact news exists
    st.session_state.alert_played = False




st.markdown("""
---
**Designed by:-  
Gaurav Singh Yadav**   
🩷💛🩵💙🩶💜🤍🤎💖  Built With Love 🫶  
Energy | Commodity | Quant Intelligence 📶  
📱 +91-8003994518 〽️   
📧 yadav.gauravsingh@gmail.com ™️
""")
