import aiohttp
import os


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

SEARCH_BASE_URL = "https://www.googleapis.com/customsearch/v1"
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3/search"


async def search_images(query: str, start: int = 1) -> list[dict]:
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "searchType": "image",
        "num": 10,
        "start": start,
        "fields": "items(title,link,image(contextLink,thumbnailLink,byteSize),displayLink)",
        "rights": "cc_publicdomain,cc_attribute,cc_sharealike,cc_noncommercial,cc_nonderived",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    items = data.get("items", [])
    results = []
    for item in items:
        img = item.get("image", {})
        results.append({
            "title": item.get("title", "No title"),
            "url": item.get("link", ""),
            "page_url": img.get("contextLink", ""),
            "thumbnail": img.get("thumbnailLink", ""),
            "source": item.get("displayLink", ""),
            "license": _detect_license(item),
        })
    return results


async def search_web(query: str, start: int = 1) -> list[dict]:
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 10,
        "start": start,
        "fields": "items(title,link,snippet,displayLink)",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    items = data.get("items", [])
    results = []
    for item in items:
        results.append({
            "title": item.get("title", "No title"),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": item.get("displayLink", ""),
        })
    return results


async def search_news(query: str, start: int = 1) -> list[dict]:
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 10,
        "start": start,
        "tbm": "nws",
        "fields": "items(title,link,snippet,displayLink)",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    items = data.get("items", [])
    results = []
    for item in items:
        results.append({
            "title": item.get("title", "No title"),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": item.get("displayLink", ""),
        })
    return results


async def search_videos(query: str, page_token: str | None = None) -> tuple[list[dict], str | None]:
    params = {
        "key": YOUTUBE_API_KEY,
        "q": query,
        "part": "snippet",
        "type": "video",
        "maxResults": 10,
        "fields": "items(id/videoId,snippet(title,channelTitle,description,thumbnails/high/url)),nextPageToken",
    }
    if page_token:
        params["pageToken"] = page_token
    async with aiohttp.ClientSession() as session:
        async with session.get(YOUTUBE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    items = data.get("items", [])
    next_token = data.get("nextPageToken")
    results = []
    for item in items:
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId", "")
        results.append({
            "title": snippet.get("title", "No title"),
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "channel": snippet.get("channelTitle", "Unknown"),
            "description": snippet.get("description", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        })
    return results, next_token


def _detect_license(item: dict) -> str:
    title = item.get("title", "").lower()
    link = item.get("link", "").lower()
    metatags = item.get("pagemap", {}).get("metatags", [{}])
    meta = metatags[0] if metatags else {}

    license_url = meta.get("og:license", "") or meta.get("license", "")

    if "creativecommons" in license_url or "creativecommons" in link:
        return "CC License (Creative Commons)"
    if "publicdomain" in license_url or "public domain" in title:
        return "Public Domain"
    if "wikipedia" in link or "wikimedia" in link:
        return "CC BY-SA (Wikipedia/Wikimedia)"
    if "unsplash" in link:
        return "Unsplash License (Free to use)"
    if "pixabay" in link:
        return "Pixabay License (Free to use)"
    if "pexels" in link:
        return "Pexels License (Free to use)"
    return "Copyright status unknown — check source"
