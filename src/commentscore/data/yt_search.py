import requests
import json
import re
from typing import List

class SearchResult:
    def __init__(self, title: str, uploader: str, url: str, duration: str, video_id: str, live: bool, source_name: str):
        self.title = title
        self.uploader = uploader
        self.url = url
        self.id = video_id
        self.duration = duration
        self.live = live
        self.source_name = source_name

    def __repr__(self):
        return f"SearchResult(title={self.title}, uploader={self.uploader}, url={self.url}, duration={self.duration}, id={self.id}, live={self.live})"

def yt_search(search_term: str, limit: int = 10) -> List[SearchResult]:
    """Search YouTube for a term and return video search results."""
    search_url = f"https://www.youtube.com/results?search_query={search_term}"
    response = requests.get(search_url, headers={"Accept-Language": "en"})
    if response.status_code != 200:
        raise Exception("Failed to make a request to YouTube")

    html_content = response.text
    yt_initial_data_pattern = r"var ytInitialData = ({.*?});"
    match = re.search(yt_initial_data_pattern, html_content)
    if not match:
        raise Exception("Could not find initial data in the page content")

    yt_data = json.loads(match.group(1))
    results = []

    # Loop through all sections and all video renderers
    sections = yt_data.get("contents", {}) \
        .get("twoColumnSearchResultsRenderer", {}) \
        .get("primaryContents", {}) \
        .get("sectionListRenderer", {}) \
        .get("contents", [])

    for section in sections:
        for content in section.get("itemSectionRenderer", {}).get("contents", []):
            video_renderer = content.get("videoRenderer", {})
            if video_renderer:
                video_id = video_renderer.get("videoId")
                title = video_renderer.get("title", {}).get("runs", [{}])[0].get("text")
                uploader = video_renderer.get("ownerText", {}).get("runs", [{}])[0].get("text")
                duration = video_renderer.get("lengthText", {}).get("simpleText", "")
                live = "Live" in duration

                results.append(SearchResult(
                    title=title,
                    uploader=uploader,
                    url=f"https://youtube.com/watch?v={video_id}",
                    duration=duration,
                    video_id=video_id,
                    live=live,
                    source_name="youtube"
                ))

                if len(results) >= limit:
                    return results
    return results
