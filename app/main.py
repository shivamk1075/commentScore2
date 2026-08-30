import streamlit as st

st.set_page_config(
    page_title="CommentScore | NLP Streaming Engine",
    page_icon="insights",
    layout="wide"
)

# Custom CSS for cards AND sidebar typography
st.markdown("""
<style>
    /* =========================================
       1. SIDEBAR TYPOGRAPHY
       ========================================= */
       
    /* Increase font size for Sidebar Navigation Links */
    [data-testid="stSidebarNav"] span {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
    }

    /* Increase font size for any regular text or widget labels in the sidebar */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label {
        font-size: 1.1rem !important;
    }
    
    /* Increase sidebar headers if you add any */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        font-size: 1.4rem !important;
    }


    /* =========================================
       2. CLICKABLE MAIN CARDS
       ========================================= */
       
    .clickable-card {
        display: block;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 28px;
        text-decoration: none !important;
        background-color: #FFFFFF; 
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        border-left: 6px solid #CBD5E1; 
    }

    .clickable-card h3 {
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0F172A !important; 
    }
    
    .clickable-card .use-case {
        font-weight: 600;
        margin-bottom: 12px;
        font-size: 1.15rem;
        color: #1E293B !important; 
    }
    
    .clickable-card .description {
        font-size: 1.05rem;
        margin-bottom: 0;
        line-height: 1.6;
        color: #475569 !important; 
    }

    .card-yt:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px -5px rgba(239, 68, 68, 0.15);
        border-left-color: #EF4444; 
        background-color: #FEF2F2; 
    }
    
    .card-gh:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px -5px rgba(139, 92, 246, 0.15);
        border-left-color: #8B5CF6; 
        background-color: #F5F3FF; 
    }

    .card-hn:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px -5px rgba(249, 115, 22, 0.15);
        border-left-color: #F97316; 
        background-color: #FFF7ED; 
    }
</style>
""", unsafe_allow_html=True)

st.title("CommentScore", text_alignment="center")
st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.2rem; margin-bottom: 3.5rem;'>Multi-platform developer community sentiment engine</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <a href="youtube" target="_self" class="clickable-card card-yt">
        <h3>YouTube ranker</h3>
        <div class="use-case">Use case: Tutorial quality & usability</div>
        <p class="description">Filters high-friction videos via comment sentiment and pinpoints confusing timestamps.</p>
    </a>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <a href="github" target="_self" class="clickable-card card-gh">
        <h3>GitHub Repository</h3>
        <div class="use-case">Use case: Open-source prioritization</div>
        <p class="description">Ranks open repository issues by community frustration level to streamline maintainer workflow.</p>
    </a>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <a href="hackernews" target="_self" class="clickable-card card-hn">
        <h3>Hacker News sentiment</h3>
        <div class="use-case">Use case: Product launch reception</div>
        <p class="description">Aggregates discussion threads to evaluate community consensus, skepticism, and praise.</p>
    </a>
    """, unsafe_allow_html=True)