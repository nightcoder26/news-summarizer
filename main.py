import os
import re
from googleapiclient.discovery import build

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCz8QaiQxApLq8sLNcszYyJw"  
KEYWORDS = ["Vantage with Palki Sharma", "Vantage This Week With Palki Sharma"]
MIN_DURATION_MINUTES = 30

def extract_duration_minutes(duration):
    """Convert YouTube duration format (PT#H#M#S) to total minutes."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return None  

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 60 + minutes + (seconds / 60)

def get_latest_filtered_video():
    if not API_KEY:
        print("⚠️ API Key is missing! Check your .env file.")
        return None

    youtube = build("youtube", "v3", developerKey=API_KEY)

    search_response = youtube.search().list(
        part="id,snippet",
        channelId=CHANNEL_ID,
        maxResults=25,
        order="date",
        type="video",
        eventType="none"  
    ).execute()

    video_items = search_response.get("items", [])
    video_ids = [item["id"]["videoId"] for item in video_items]
    video_titles = {item["id"]["videoId"]: item["snippet"]["title"] for item in video_items}

    if not video_ids:
        print("❌ No uploaded videos found.")
        return None

    details_response = youtube.videos().list(
        part="contentDetails",
        id=",".join(video_ids)
    ).execute()

    for video in details_response.get("items", []):
        video_id = video["id"]
        title = video_titles.get(video_id, "Unknown Title")
        duration = video["contentDetails"]["duration"]
        minutes = extract_duration_minutes(duration)

        if minutes is None:
            # print(f"⚠️ Skipping (Invalid/Processing Video): {title}")
            continue

        # print(f"🔍 Checking: {title} ({minutes:.2f} min)")

        if minutes >= MIN_DURATION_MINUTES and any(keyword.lower() in title.lower() for keyword in KEYWORDS):
            # print(f"✅ Selected: {title} ({minutes:.2f} min)")
            return f"https://www.youtube.com/watch?v={video_id}"

    print("Not found")
    return None

video_url = get_latest_filtered_video()
print("Filtered video:", video_url)
