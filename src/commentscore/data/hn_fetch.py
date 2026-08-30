import requests

def search_hn_stories(query: str, limit: int = 25) -> list[dict]:
    """Search Hacker News for stories matching a query."""
    url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage={limit}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return []
    
    hits = response.json().get("hits", [])
    results = []
    for h in hits:
        results.append({
            "id": h["objectID"],
            "title": h.get("title") or "No title",
            "author": h.get("author", "anonymous"),
            "points": h.get("points", 0),
            "num_comments": h.get("num_comments", 0),
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
            "hn_url": f"https://news.ycombinator.com/item?id={h['objectID']}"
        })
    return results

def fetch_hn_comments(story_id: str, max_comments: int = 100) -> list[str]:
    """Fetch top comments for a specific Hacker News story ID."""
    url = f"https://hn.algolia.com/api/v1/items/{story_id}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return []
    
    data = response.json()
    comments = []

    def extract_children(node):
        if len(comments) >= max_comments:
            return
        for child in node.get("children", []):
            text = child.get("text")
            if text:
                comments.append(text)
            extract_children(child)

    extract_children(data)
    return comments[:max_comments]