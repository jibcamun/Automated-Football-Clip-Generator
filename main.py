#!/usr/bin/env python3
import argparse
import json
import os
from video_utils import build_short_from_folder, export_clip
from upload_youtube import upload_video

DEFAULT_CONFIG = "config.example.json"

def parse_args():
    p = argparse.ArgumentParser(description="Build a football short and upload to YouTube.")
    p.add_argument("--input-dir", required=True, help="Folder containing source clips")
    p.add_argument("--output", required=True, help="Output short filename (mp4)")
    p.add_argument("--title", default=None, help="YouTube title")
    p.add_argument("--description", default=None, help="YouTube description")
    p.add_argument("--tags", default=None, help="Comma-separated tags")
    p.add_argument("--music", default=None, help="Optional background music file")
    p.add_argument("--privacy", default=None, choices=["public","unlisted","private"], help="Video privacy setting")
    p.add_argument("--config", default=DEFAULT_CONFIG, help="Path to config JSON")
    return p.parse_args()

def load_config(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def main():
    args = parse_args()
    cfg = load_config(args.config)

    title = args.title or cfg.get("default_title", "Football Short #Shorts")
    description = args.description or cfg.get("default_description", "")
    tags = (args.tags.split(",") if args.tags else cfg.get("default_tags", []))
    privacy = args.privacy or cfg.get("privacyStatus", "private")

    # build the short
    print("Building short from:", args.input_dir)
    final = build_short_from_folder(args.input_dir, music_path=args.music)
    print("Exporting to:", args.output)
    export_clip(final, args.output)

    # upload
    print("Uploading to YouTube (this will open an OAuth prompt on first run)...")
    client_secrets = cfg.get("client_secrets", "client_secrets.json")
    credentials_file = cfg.get("credentials_file", "token.json")
    video_id = upload_video(args.output, title, description, tags, privacy, client_secrets_file=client_secrets, credentials_file=credentials_file)
    if video_id:
        print("Upload complete. Video ID:", video_id)
        print("Watch at: https://youtu.be/" + video_id)
    else:
        print("Upload failed.")

if __name__ == "__main__":
    main()
