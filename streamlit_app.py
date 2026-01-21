#!/usr/bin/env python3
"""
Streamlit web UI for building football shorts and uploading to YouTube.

Run:
  streamlit run streamlit_app.py

This app expects the helper modules (video_utils.py and upload_youtube.py) to be in the same directory.
"""
import streamlit as st
import tempfile
import shutil
import os
from pathlib import Path
from video_utils import build_short_from_folder, export_clip
import upload_youtube

st.set_page_config(page_title="Football Shorts Maker", layout="centered")

st.title("Football Shorts Maker (Streamlit)")
st.markdown("Upload source clips, optionally add background music, build a vertical short (<=60s) and upload to YouTube.")

with st.expander("Instructions"):
    st.markdown(
        """
- Upload one or more short clip files (mp4/mov/etc.). The app will crop/resize to 1080x1920 and concatenate up to 60s.
- Optionally upload a background music file (mp3/m4a).
- After building, preview the generated short and optionally upload to YouTube.
- On first YouTube upload, OAuth flow will open a browser window for login and consent.
"""
    )

# Uploaders
uploaded_videos = st.file_uploader("Upload video clips (multiple)", type=["mp4", "mov", "mkv", "avi", "webm"], accept_multiple_files=True)
uploaded_music = st.file_uploader("Optional background music (single)", type=["mp3", "m4a", "wav", "aac"], accept_multiple_files=False)

col1, col2 = st.columns(2)
with col1:
    title = st.text_input("YouTube Title", "Amazing Football Short #Shorts")
with col2:
    privacy = st.selectbox("Privacy", ["private", "unlisted", "public"], index=0)

description = st.text_area("YouTube Description", "Generated with Football Shorts Maker")
tags_input = st.text_input("Tags (comma-separated)", "football,shorts,highlights")
tags = [t.strip() for t in tags_input.split(",") if t.strip()]

build_btn = st.button("Build Short")

# Temporary working dir
if "work_dir" not in st.session_state:
    st.session_state.work_dir = None

if build_btn:
    if not uploaded_videos:
        st.error("Please upload at least one video clip.")
    else:
        tmpdir = tempfile.mkdtemp(prefix="football_shorts_")
        st.session_state.work_dir = tmpdir
        st.info(f"Saved {len(uploaded_videos)} clips to working directory: {tmpdir}")

        # save uploaded files
        saved_paths = []
        for up in uploaded_videos:
            dest = os.path.join(tmpdir, up.name)
            with open(dest, "wb") as f:
                f.write(up.getbuffer())
            saved_paths.append(dest)

        music_path = None
        if uploaded_music:
            music_dest = os.path.join(tmpdir, uploaded_music.name)
            with open(music_dest, "wb") as f:
                f.write(uploaded_music.getbuffer())
            music_path = music_dest

        st.info("Building the short. This may take a while depending on clip lengths and server resources.")
        progress_text = st.empty()
        progress_bar = st.progress(0.0)

        try:
            # build the short; we don't have per-step progress in moviepy, so use coarse updates
            progress_text.text("Processing clips (resizing + cropping)...")
            progress_bar.progress(0.2)
            final_clip = build_short_from_folder(tmpdir, music_path=music_path)
            progress_text.text("Exporting final video...")
            progress_bar.progress(0.6)

            out_file = os.path.join(tmpdir, "football_short.mp4")
            export_clip(final_clip, out_file)
            progress_bar.progress(1.0)
            progress_text.text("Done!")

            st.success("Short built successfully.")
            st.video(out_file)
            st.session_state.output_file = out_file
        except Exception as e:
            st.error(f"Error while building short: {e}")
            # cleanup
            try:
                shutil.rmtree(tmpdir)
            except Exception:
                pass
            st.session_state.work_dir = None
            st.session_state.output_file = None

# Upload section
if st.session_state.get("output_file"):
    st.markdown("---")
    st.subheader("Upload to YouTube")
    st.write("Title, description and tags can be adjusted before uploading.")
    upload_title = st.text_input("Upload Title", value=title)
    upload_description = st.text_area("Upload Description", value=description)
    upload_tags = st.text_input("Upload Tags (comma-separated)", value=",".join(tags))
    upload_privacy = st.selectbox("Upload Privacy", ["private", "unlisted", "public"], index=["private","unlisted","public"].index(privacy))

    upload_btn = st.button("Upload to YouTube")
    if upload_btn:
        st.info("Starting upload. An OAuth window may open (first time).")
        try:
            # call upload_youtube with run_local_server=True so browser-based OAuth is used
            video_id = upload_youtube.upload_video(
                st.session_state.output_file,
                upload_title,
                description=upload_description,
                tags=[t.strip() for t in upload_tags.split(",") if t.strip()],
                privacyStatus=upload_privacy,
                client_secrets_file="client_secrets.json",
                credentials_file="token.json",
                run_local_server=True,
                local_server_port=0
            )
            if video_id:
                st.success("Upload complete!")
                st.write(f"Watch: https://youtu.be/{video_id}")
            else:
                st.error("Upload failed (no video id returned).")
        except Exception as e:
            st.error(f"Upload failed: {e}")

# Cleanup button
if st.session_state.get("work_dir"):
    if st.button("Cleanup temporary files"):
        try:
            shutil.rmtree(st.session_state.work_dir)
        except Exception as e:
            st.warning(f"Cleanup error: {e}")
        st.session_state.work_dir = None
        st.success("Temporary files removed.")
