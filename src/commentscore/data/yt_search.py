# import requests
# import json
# import re
# from typing import List, Optional

# DURATION_MATCH_THRESHOLD = 10  # seconds

# class Track:
#     def __init__(self, title: str, artist: str, album: str, duration: int):
#         self.title = title
#         self.artist = artist
#         self.album = album
#         self.duration = duration

#     def __repr__(self):
#         return f"Track(title={self.title}, artist={self.artist}, album={self.album}, duration={self.duration})"


# class SearchResult:
#     def __init__(self, title: str, uploader: str, url: str, duration: str, video_id: str, live: bool, source_name: str):
#         self.title = title
#         self.uploader = uploader
#         self.url = url
#         self.duration = duration
#         self.id = video_id
#         self.live = live
#         self.source_name = source_name

#     def __repr__(self):
#         return f"SearchResult(title={self.title}, uploader={self.uploader}, url={self.url}, duration={self.duration}, id={self.id}, live={self.live})"


# def convert_string_duration_to_seconds(duration_str: str) -> int:
#     """Convert a YouTube duration string (e.g., '2:30' or '1:10:30') to seconds."""
#     parts = duration_str.split(":")
#     if len(parts) == 1:
#         return int(parts[0])
#     elif len(parts) == 2:
#         minutes, seconds = int(parts[0]), int(parts[1])
#         return minutes * 60 + seconds
#     elif len(parts) == 3:
#         hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
#         return (hours * 60 * 60) + (minutes * 60) + seconds
#     return 0




# def yt_search(search_term: str, limit: int = 10) -> List[SearchResult]:
#     """Search YouTube for a term and return video search results."""
#     search_url = f"https://www.youtube.com/results?search_query={search_term}"

#     response = requests.get(search_url, headers={"Accept-Language": "en"})
#     if response.status_code != 200:
#         raise Exception("Failed to make a request to YouTube")

#     html_content = response.text
#     yt_initial_data_pattern = r"var ytInitialData = ({.*?});"
#     match = re.search(yt_initial_data_pattern, html_content)
#     if not match:
#         raise Exception("Could not find initial data in the page content")

#     yt_data = json.loads(match.group(1))
#     results = []

#     for item in yt_data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", []):
#         video_renderer = item.get("itemSectionRenderer", {}).get("contents", [{}])[0].get("videoRenderer", {})
#         if video_renderer:
#             video_id = video_renderer.get("videoId")
#             title = video_renderer.get("title", {}).get("runs", [{}])[0].get("text")
#             uploader = video_renderer.get("ownerText", {}).get("runs", [{}])[0].get("text")
#             duration = video_renderer.get("lengthText", {}).get("simpleText", "")
#             live = "Live" in duration

#             results.append(SearchResult(
#                 title=title,
#                 uploader=uploader,
#                 url=f"https://youtube.com/watch?v={video_id}",
#                 duration=duration,
#                 video_id=video_id,
#                 live=live,
#                 source_name="youtube"
#             ))

#             if len(results) >= limit:
#                 break

#     return results


# def get_youtube_id(track: Track) -> Optional[str]:
#     song_duration_in_seconds = track.duration
#     search_query = f"'{track.title}' {track.artist}"

#     search_results = yt_search(search_query, 10)
#     if not search_results:
#         raise Exception(f"No songs found for {search_query}")

#     # Try to match the closest duration
#     for result in search_results:
#         result_duration_in_seconds = convert_string_duration_to_seconds(result.duration)
#         if abs(result_duration_in_seconds - song_duration_in_seconds) <= DURATION_MATCH_THRESHOLD:
#             return result.id

#     # Fallback: return the first result even if not close in duration
#     if search_results:
#         print("No close match found. Falling back to first search result.")
#         return search_results[0].id

#     return None


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
