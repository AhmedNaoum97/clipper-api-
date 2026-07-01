# Clipper API

A FastAPI service that turns long-form YouTube videos into short-form vertical clips (9:16) ready for TikTok and YouTube Shorts.

## What it does

Accepts a YouTube URL, downloads the video, cuts it into fixed-duration segments, and reformats each clip to 1080x1920 vertical with a blurred background fill. Returns a list of hosted clip URLs.

## Stack

- FastAPI (API framework)
- yt-dlp (video download)
- FFmpeg (clipping and vertical formatting)
- Docker (deployment)

## Endpoint

`POST /clip`

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "clip_duration": 55
}
```

Response:

```json
{
  "job_id": "uuid",
  "clip_count": 4,
  "clips": ["https://.../clip_000.mp4", "..."]
}
```

## Running locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Requires FFmpeg installed on the host.

## Deployment

Deployed via Docker. The included Dockerfile installs FFmpeg and runs the app on port 8080.
