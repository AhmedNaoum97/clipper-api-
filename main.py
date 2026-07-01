from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp
import subprocess
import os
import uuid
import glob

app = FastAPI()

CLIPS_DIR = "clips"
os.makedirs(CLIPS_DIR, exist_ok=True)

app.mount("/clips", StaticFiles(directory=CLIPS_DIR), name="clips")

class ClipRequest(BaseModel):
    url: str
    clip_duration: int = 55

@app.get("/")
def root():
    return {"status": "clipper-api running"}

@app.post("/clip")
def clip_video(request: ClipRequest):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(CLIPS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    # Step 1: Download video
    video_path = os.path.join(job_dir, "source.mp4")
    ydl_opts = {
        "outtmpl": video_path,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([request.url])

    # Step 2: Cut into 9:16 vertical clips with blur bars
    clips_output_dir = os.path.join(job_dir, "output")
    os.makedirs(clips_output_dir, exist_ok=True)

    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path,
        "-vf",
        (
            "split=2[blur][vid];"
            "[blur]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=20:20[bg];"
            "[vid]scale=1080:1080[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2"
        ),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-segment_time", str(request.clip_duration),
        "-f", "segment",
        "-reset_timestamps", "1",
        os.path.join(clips_output_dir, "clip_%03d.mp4")
    ]
    subprocess.run(ffmpeg_cmd)

    # Step 3: Return clip URLs
    clip_files = sorted(glob.glob(os.path.join(clips_output_dir, "clip_*.mp4")))
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
    clip_urls = [
        f"{base_url}/clips/{job_id}/output/{os.path.basename(f)}"
        for f in clip_files
    ]

    return {
        "job_id": job_id,
        "clip_count": len(clip_urls),
        "clips": clip_urls
    }