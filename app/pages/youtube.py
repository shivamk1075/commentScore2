import time
import streamlit as st
import pandas as pd
import re
from commentscore.data.yt_search import yt_search
from commentscore.data.yt_fetch import fetch_comments 
from commentscore.features.preprocess import preprocess_comments
from commentscore.models.classify import classify_comments
from commentscore.models.aggregate import aggregate_video_sentiment

st.set_page_config(page_title="YoutubeRanks | CommentScore", page_icon=":material/play_circle:", layout="wide")

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
    options=["Fast analysis (TF-IDF + SGD)", "Full analysis (DistilBERT)"],
    help="Fast uses linear classification for speed. Full uses transformer attention for deep context."
)
mode_flag = "Full" if "Full" in analysis_mode else "Fast"

def duration_to_seconds(duration_str):
    parts = duration_str.split(":")
    if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
    return int(duration_str) if duration_str.isdigit() else 0

def render_sentiment_bar(pos, neu, neg):
    total = pos + neu + neg
    if total == 0: return ""
    p_pct = (pos / total) * 100
    nu_pct = (neu / total) * 100
    ng_pct = (neg / total) * 100
    return f"""
    <div style="width: 100%; height: 6px; background-color: #F1F5F9; border-radius: 3px; display: flex; overflow: hidden; margin: 12px 0px;">
        <div style="width: {p_pct}%; background-color: #10B981;" title="Positive: {p_pct:.1f}%"></div>
        <div style="width: {nu_pct}%; background-color: #94A3B8;" title="Neutral: {nu_pct:.1f}%"></div>
        <div style="width: {ng_pct}%; background-color: #EF4444;" title="Negative: {ng_pct:.1f}%"></div>
    </div>
    """

def extract_timestamps(neg_comments):
    timestamps = []
    for comment in neg_comments:
        timestamps.extend(re.findall(r'\b\d{1,2}:\d{2}\b', comment))
    return list(set(timestamps))[:4]

def extract_badges(raw_text):
    badges = []
    text = raw_text.lower()
    if any(w in text for w in ['deprecated', 'old version', 'outdated']): badges.append("Outdated")
    if any(w in text for w in ['slow down', 'rushed', 'too fast', 'hard to follow']): badges.append("Too fast")
    if any(w in text for w in ['error', 'bug', 'crash', 'fail']): badges.append("Broken code")
    return badges

@st.cache_data(show_spinner=False)
def analyze_youtube(search_term: str, current_mode: str):
    vid_limit = 20 if current_mode == "Fast" else 8
    comment_limit = 40 if current_mode == "Fast" else 15
    
    start_time = time.time()
    search_results = yt_search(search_term, limit=vid_limit)
    recommendations = []
    total_comments_processed = 0

    for result in search_results:
        try:
            raw_comments = fetch_comments(result.id, max_results=comment_limit)
            if raw_comments and len(raw_comments) >= 5:
                total_comments_processed += len(raw_comments)
                input_data = preprocess_comments(raw_comments) if current_mode == "Fast" else raw_comments
                labels = classify_comments(input_data, mode=current_mode)
                
                pos_comments = [c for c, l in zip(raw_comments, labels) if l == "POSITIVE"]
                neg_comments = [c for c, l in zip(raw_comments, labels) if l == "NEGATIVE"]
                
                video_verdict = aggregate_video_sentiment(preprocess_comments(raw_comments), labels)
                pos_count = labels.count("POSITIVE")
                neg_count = labels.count("NEGATIVE")
                
                if (pos_count + neg_count) > 5 and 0.4 <= (pos_count / (pos_count + neg_count)) <= 0.6:
                    video_verdict = "Controversial"

                recommendations.append({
                    "title": result.title,
                    "uploader": result.uploader,
                    "url": result.url,
                    "duration": result.duration,
                    "duration_sec": duration_to_seconds(result.duration),
                    "video_id": result.id,
                    "verdict": video_verdict,
                    "pos": pos_count,
                    "neu": labels.count("NEUTRAL"),
                    "neg": neg_count,
                    "top_pos": pos_comments[0] if pos_comments else None,
                    "top_neg": neg_comments[0] if neg_comments else None,
                    "all_comments": raw_comments,
                    "timestamps": extract_timestamps(neg_comments),
                    "badges": extract_badges(" ".join(raw_comments))
                })
        except Exception:
            continue
            
    latency = time.time() - start_time
    return recommendations, latency, total_comments_processed

st.title("YouTube Ranker")
st.caption("Evaluate tutorial efficacy and extract friction points using audience feedback.")

with st.container(border=True):
    col_input, col_sort, col_btn = st.columns([3, 2, 1])
    with col_input:
        query = st.text_input("Tutorial topic:", placeholder="e.g. Docker for beginners")
    with col_sort:
        sort_mode = st.selectbox("Sort output by:", ["Sentiment rank (verdict)", "Highest praise ratio", "Shortest duration"])
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        execute_search = st.button("Analyze content", type="primary", use_container_width=True)

if query:
    with st.spinner(f"Running {mode_flag.lower()} inference across YouTube discussions..."):
        results, latency, comment_count = analyze_youtube(query, mode_flag)

    if results:
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        useful_count = sum(1 for r in results if r["verdict"] == "Useful")

        kpi1.metric("Videos evaluated", f"{len(results)}")
        kpi2.metric("Comments scored", f"{comment_count}")
        kpi3.metric("Useful tutorials", f"{useful_count} / {len(results)}")
        kpi4.metric("Inference latency", f"{latency:.2f}s")

        st.write("")

        if sort_mode == "Highest praise ratio":
            results.sort(key=lambda x: x["pos"] / max(1, (x["pos"] + x["neu"] + x["neg"])), reverse=True)
        elif sort_mode == "Shortest duration":
            results.sort(key=lambda x: x["duration_sec"])
        else:
            rank_map = {"Useful": 0, "Controversial": 1, "Partially Useful": 2, "Not Useful": 3}
            results.sort(key=lambda x: rank_map.get(x["verdict"], 4))

        for res in results:
            with st.container(border=True):
                col_thumb, col_info = st.columns([1, 4])
                with col_thumb:
                    st.image(f"https://img.youtube.com/vi/{res['video_id']}/hqdefault.jpg", use_container_width=True)
                    st.caption(f"Duration: {res['duration']}")
                with col_info:
                    st.markdown(f"#### [{res['title']}]({res['url']})")
                    
                    badge_html = "".join([f"<span style='background-color: #F1F5F9; color: #475569; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; margin-left: 8px;'>{b}</span>" for b in res['badges']])
                    st.markdown(f"**Channel:** {res['uploader']} | **Verdict:** {res['verdict']} {badge_html}", unsafe_allow_html=True)
                    
                    st.markdown(render_sentiment_bar(res['pos'], res['neu'], res['neg']), unsafe_allow_html=True)
                    
                    t1, t2 = st.tabs(["Key highlights", "Diagnostics"])
                    with t1:
                        if res["top_pos"]: st.success(f"Praise: \"{res['top_pos']}\"", icon=":material/thumb_up:")
                        if res["top_neg"]: st.error(f"Friction: \"{res['top_neg']}\"", icon=":material/warning:")
                        if res["timestamps"]: st.warning(f"Reported confusion timestamps: {', '.join(res['timestamps'])}", icon=":material/schedule:")
                    with t2:
                        st.caption(f"Sentiment counts: {res['pos']} Positive | {res['neu']} Neutral | {res['neg']} Negative")
    else:
        st.info("No matching videos with sufficient comment data found.", icon=":material/info:")