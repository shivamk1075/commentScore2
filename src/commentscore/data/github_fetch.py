import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "CommentScore-App"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

def fetch_github_issues(repo: str, limit: int = 25) -> list[dict]:
    """
    Fetch open issues and their comments for a given repo (e.g., 'streamlit/streamlit').
    """
    url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page={limit}"
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        return []

    issues_data = []
    for item in response.json():
        if "pull_request" in item:
            continue  # Skip pull requests to focus on bugs/issues
        
        comments_url = item.get("comments_url")
        raw_comments = []
        if comments_url and item.get("comments", 0) > 0:
            c_resp = requests.get(f"{comments_url}?per_page=30", headers=HEADERS, timeout=10)
            if c_resp.status_code == 200:
                raw_comments = [c["body"] for c in c_resp.json() if c.get("body")]

        issues_data.append({
            "id": item["id"],
            "number": item["number"],
            "title": item["title"],
            "user": item["user"]["login"],
            "html_url": item["html_url"],
            "comments_count": item["comments"],
            "comments": raw_comments
        })
    return issues_data