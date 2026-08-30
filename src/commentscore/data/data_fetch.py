# src/data_fetch.py
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

def fetch_comments(video_id: str, max_results: int = 500) -> list[str]:
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=max_results,
    )
    while request and len(comments) < max_results:
        response = request.execute()
        for item in response["items"]:
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )
        request = youtube.commentThreads().list_next(request, response)
    return comments

if __name__ == "__main__":
    sample = fetch_comments("VIDEO_ID_HERE", max_results=50)
    print(sample[:5])
