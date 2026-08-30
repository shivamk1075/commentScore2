import time
import streamlit as st
from commentscore.data.hn_fetch import search_hn_stories, fetch_hn_comments
from commentscore.features.preprocess import preprocess_comments
from commentscore.models.classify import classify_comments

st.set_page_config(page_title="Hacker News Sentiment | CommentScore", page_icon=":material/article:", layout="wide")

st.markdown("""
<style>
    /* =========================================
       1. GLOBAL TYPOGRAPHY (Titles & Captions)
       ========================================= */
    h1 {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stCaptionContainer"] {
        font-size: 1.15rem !important;
        color: #475569 !important;
    }
    /* Headers inside the result cards */
    h4 { 
        font-size: 1.3rem !important;
        color: #0F172A !important;
        margin-bottom: 0.5rem !important;
    }

    /* =========================================
       2. WIDGETS & INPUTS (Search, Select, Radio)
       ========================================= */
    /* Input Labels */
    [data-testid="stWidgetLabel"] p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }
    /* Text Input and Select Box text */
    [data-baseweb="input"] input,
    [data-baseweb="select"] div {
        font-size: 1.1rem !important;
        padding: 4px 8px !important;
    }
    /* Radio buttons in sidebar */
    [data-baseweb="radio"] div {
        font-size: 1.1rem !important;
    }

    /* =========================================
       3. PRIMARY BUTTONS
       ========================================= */
    [data-testid="baseButton-primary"] {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        transition: transform 0.1s ease;
    }
    [data-testid="baseButton-primary"]:active {
        transform: scale(0.98);
    }

    /* =========================================
       4. METRICS & ALERTS (KPIs and feedback)
       ========================================= */
    [data-testid="stMetricLabel"] p {
        font-size: 1.05rem !important;
        color: #475569 !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    /* Alerts (Success/Warning/Error text) */
    [data-testid="stAlert"] p {
        font-size: 1.05rem !important;
    }
    /* Tabs */
    [data-baseweb="tab"] p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* =========================================
       5. RESULT CARDS (Hover & Layout)
       ========================================= */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.08) !important;
        border-color: #94A3B8 !important;
    }

    /* =========================================
       6. SIDEBAR NAV
       ========================================= */
    [data-testid="stSidebarNav"] span {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.header("Inference engine")
analysis_mode = st.sidebar.radio(
    "Select NLP engine:",
    options=["Fast analysis (TF-IDF + SGD)", "Full analysis (DistilBERT)"]
)
mode_flag = "Full" if "Full" in analysis_mode else "Fast"

def render_sentiment_bar(pos, neu, neg):
    total = pos + neu + neg
    if total == 0: return ""
    return f"""
    <div style="width: 100%; height: 6px; background-color: #F1F5F9; border-radius: 3px; display: flex; overflow: hidden; margin: 10px 0px;">
        <div style="width: {(pos/total)*100}%; background-color: #10B981;"></div>
        <div style="width: {(neu/total)*100}%; background-color: #94A3B8;"></div>
        <div style="width: {(neg/total)*100}%; background-color: #EF4444;"></div>
    </div>
    """

st.title("Hacker News Topics Sentiment")
st.caption("Measure tech reception, skepticism, and praise on product launches.")

with st.container(border=True):
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        hn_query = st.text_input("Search HN topics:", placeholder="e.g. Show HN: FastAPI")
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        run_btn = st.button("Search discussions", type="primary", use_container_width=True)

if hn_query:
    story_limit = 20 if mode_flag == "Fast" else 8
    comment_limit = 50 if mode_flag == "Fast" else 20
    start_time = time.time()

    with st.spinner(f"Analyzing discussions with {mode_flag.lower()} engine..."):
        stories = search_hn_stories(hn_query, limit=story_limit)
        results = []
        total_comments = 0

        for s in stories:
            comments = fetch_hn_comments(s["id"], max_comments=comment_limit)
            if comments:
                total_comments += len(comments)
                input_data = preprocess_comments(comments) if mode_flag == "Fast" else comments
                labels = classify_comments(input_data, mode=mode_flag)
                
                pos_c = [c for c, l in zip(comments, labels) if l == "POSITIVE"]
                neg_c = [c for c, l in zip(comments, labels) if l == "NEGATIVE"]

                results.append({
                    "title": s["title"],
                    "author": s["author"],
                    "points": s["points"],
                    "url": s["url"],
                    "hn_url": s["hn_url"],
                    "pos": labels.count("POSITIVE"),
                    "neu": labels.count("NEUTRAL"),
                    "neg": labels.count("NEGATIVE"),
                    "top_pos": pos_c[0] if pos_c else None,
                    "top_neg": neg_c[0] if neg_c else None
                })
        latency = time.time() - start_time

    if results:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Stories evaluated", len(results))
        k2.metric("Comments scored", total_comments)
        k3.metric("Top story points", max(r["points"] for r in results))
        k4.metric("Latency", f"{latency:.2f}s")

        st.write("")
        for r in results:
            with st.container(border=True):
                st.markdown(f"#### [{r['title']}]({r['url']})")
                st.caption(f"Author: **{r['author']}** | Upvotes: **{r['points']}** | [HN Discussion]({r['hn_url']})")
                st.markdown(render_sentiment_bar(r['pos'], r['neu'], r['neg']), unsafe_allow_html=True)
                
                if r["top_pos"]:
                    st.success(f"Community praise: \"{r['top_pos']}\"", icon=":material/thumb_up:")
                if r["top_neg"]:
                    st.error(f"Skepticism: \"{r['top_neg']}\"", icon=":material/warning:")
    else:
        st.info("No matching stories found.", icon=":material/info:")