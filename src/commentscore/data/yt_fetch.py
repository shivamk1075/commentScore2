import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import socket

socket.setdefaulttimeout(300)

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

def fetch_comments(video_id: str, max_results: int = 50) -> list[str]:
    """Fetch top 50 comments for a video in a single API call."""
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=max_results,
        )
        response = request.execute()
        for item in response.get("items", []):
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )
    except Exception:
        pass # Fails silently if comments are disabled
    return comments