```markdown
# Streamlit UI for Football Shorts Maker

This Streamlit app wraps the video-building and YouTube upload flow in a browser UI.

Quick start:
1. Ensure you have `ffmpeg` installed and on PATH.
2. Place `client_secrets.json` (Google OAuth Desktop credentials) next to the code.
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

How it works:
- Upload multiple video clips in the web UI.
- Optionally upload a music file.
- Click "Build Short" to crop/resize and concatenate clips into a 1080x1920 MP4, capped at 60s.
- Preview the generated short in the browser.
- Click "Upload to YouTube" to perform OAuth and upload the video. On first upload the app will open a browser window for Google OAuth consent and save credentials to `token.json`.

Notes:
- The app uses `run_local_server` OAuth flow for a smoother web experience.
- Make sure the YouTube Data API v3 is enabled for your Google Cloud project and that your OAuth client includes the correct redirect URIs (local server defaults are used by `google-auth-oauthlib`).
- Respect copyright for clips and music before uploading.

```
