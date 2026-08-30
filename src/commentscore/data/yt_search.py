import os
import re
from typing import List
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import socket

socket.setdefaulttimeout(300)

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

class SearchResult:
    def __init__(self, title: str, uploader: str, url: str, duration: str, video_id: str):
        self.title = title
        self.uploader = uploader
        self.url = url
        self.duration = duration
        self.id = video_id

    def __repr__(self):
        return f"SearchResult(title={self.title}, uploader={self.uploader})"

def parse_iso_duration(iso_duration: str) -> str:
    """Converts YouTube API ISO 8601 duration (PT1H2M10S) to a readable format."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if not match:
        return "Unknown"
    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"

def yt_search(search_term: str, limit: int = 200) -> List[SearchResult]:
    """Search YouTube via API and handle pagination up to the limit."""
    results = []
    next_page_token = None

    # Step 1: Search for Video IDs
    while len(results) < limit:
        # The search API returns max 50 items per page
        max_results = min(50, limit - len(results))
        
        search_request = youtube.search().list(
            part="id,snippet",
            q=search_term,
            type="video",
            maxResults=max_results,
            pageToken=next_page_token
        )
        search_response = search_request.execute()
        
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            break

        # Step 2: Fetch Video Details (needed for duration)
        video_request = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(video_ids)
        )
        video_response = video_request.execute()

        for item in video_response.get("items", []):
            results.append(SearchResult(
                title=item["snippet"]["title"],
                uploader=item["snippet"]["channelTitle"],
                url=f"https://youtube.com/watch?v={item['id']}",
                duration=parse_iso_duration(item["contentDetails"]["duration"]),
                video_id=item["id"]
            ))

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break

    return results


def get_trending_education_videos(limit: int = 10) -> List[SearchResult]:
    """Fetch recent, highly-viewed education videos (Category 27) as a proxy for trending."""
    results = []
    
    # Calculate the date for 30 days ago to get recent "trending" content
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
    
    # Step 1: Use search() instead of videos() to guarantee results
    search_request = youtube.search().list(
        part="id",
        type="video",
        videoCategoryId="27", # Education
        order="viewCount",    # Sort by most viewed
        publishedAfter=thirty_days_ago, # Only recent videos
        regionCode="US",
        maxResults=min(limit, 50)
    )
    search_response = search_request.execute()
    
    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
    if not video_ids:
        return results

    # Step 2: Fetch the video details (title, uploader, duration) using the IDs
    video_request = youtube.videos().list(
        part="snippet,contentDetails",
        id=",".join(video_ids)
    )
    video_response = video_request.execute()

    for item in video_response.get("items", []):
        results.append(SearchResult(
            title=item["snippet"]["title"],
            uploader=item["snippet"]["channelTitle"],
            url=f"https://youtube.com/watch?v={item['id']}",
            duration=parse_iso_duration(item["contentDetails"]["duration"]),
            video_id=item["id"]
        ))
        
    return results