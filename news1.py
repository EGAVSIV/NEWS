import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(
    page_title="🌍 Real-Time News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "https://real-time-news-data.p.rapidapi.com"
API_KEY = "dcf7805987msh85a00f07e43ce0dp1c7845jsn45d7487e52ad"  # move to st.secrets later

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "real-time-news-data.p.rapidapi.com"
}

# ================= SESSION =================
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# ================= FETCHER =================
def fetch(endpoint, params=None):
    try:
        r = session.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception as e:
        st.error(str(e))
        return []

# ================= SIDEBAR =================
st.sidebar.title("📰 News Filters")

country = st.sidebar.selectbox(
    "Country",
    {"India": "IN", "United States": "US", "World": "US"}
)

category = st.sidebar.selectbox(
    "Category",
    ["Top Headlines", "Search", "World", "Finance", "Technology", "Sports"]
)

search_query = st.sidebar.text_input("Search Keyword", "Stock Market")

limit = st.sidebar.slider("Number of Articles", 10, 200, 50)

refresh = st.sidebar.button("🔄 Refresh News")

# ================= MAIN =================
st.markdown("## 🌍 Real-Time News Dashboard")
st.caption("Fast • Filterable • Market Ready")

# ================= ROUTING =================
params = {
    "country": country,
    "lang": "en",
    "limit": limit
}

if category == "Top Headlines":
    news = fetch("/top-headlines", params)

elif category == "Search":
    params.update({"query": search_query})
    news = fetch("/search", params)

elif category == "World":
    params.update({"topic": "WORLD"})
    news = fetch("/topic-headlines", params)

elif category == "Finance":
    params.update({"query": "Stock Market OR RBI OR Inflation OR Economy"})
    news = fetch("/search", params)

elif category == "Technology":
    params.update({"topic": "TECHNOLOGY"})
    news = fetch("/topic-headlines", params)

elif category == "Sports":
    params.update({"query": "Cricket OR Football"})
    news = fetch("/search", params)

else:
    news = []

# ================= DISPLAY =================
if not news:
    st.info("No news found. Try different filters.")

for item in news:
    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(item.get("title", "No title"))
            st.write(item.get("snippet", ""))
            st.markdown(f"🔗 [Read full article]({item.get('link', '#')})")

        with col2:
            st.markdown(f"**Source**: {item.get('source', 'NA')}")
            t = item.get("published_datetime_utc")
            if t:
                st.markdown(f"🕒 {t[:19].replace('T',' ')}")

        st.divider()

# ================= FOOTER =================
st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
