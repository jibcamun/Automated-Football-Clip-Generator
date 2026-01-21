# Football Shorts Maker & Uploader

This simple app assembles vertical (9:16) football shorts from source clips and uploads them to YouTube as Shorts.

Requirements
- Python 3.8+
- FFmpeg (moviepy depends on ffmpeg). Install ffmpeg on your system.
- A Google Cloud project with YouTube Data API v3 enabled and OAuth 2.0 Client ID (Desktop app).

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

Setup Google credentials
1. Create OAuth 2.0 Client ID (Desktop) in Google Cloud Console.
2. Download the `client_secrets.json` and place it next to the code.
3. On first run the app will prompt for OAuth and will save credentials to `token.json`.

Usage
```bash
python main.py \
  --input-dir ./clips \
  --output out_short.mp4 \
  --title "Amazing Football Short #Shorts" \
  --description "A short compilation. #Shorts" \
  --tags "football,goals,highlights" \
  --music background.mp3
```

Notes
- The app crops/resizes clips to 1080x1920 (vertical). Final duration is capped at 60s.
- To make the upload work, enable the YouTube Data API and use the `client_secrets.json`.
- For privacy: you can set `--privacy private|unlisted|public`. Default is `private`.
- Always respect copyrights for clips and music.

Files included:
- `main.py` — main CLI
- `video_utils.py` — processing helpers
- `upload_youtube.py` — uploader and auth
- `config.example.json` — example configuration
- `requirements.txt` — pip deps
