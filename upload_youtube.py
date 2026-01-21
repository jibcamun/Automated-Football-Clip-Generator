import json
import os
import pathlib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service(client_secrets_file="client_secrets.json", credentials_file="token.json"):
    creds = None
    if os.path.exists(credentials_file):
        creds = Credentials.from_authorized_user_file(credentials_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_console()
        # save for next runs
        with open(credentials_file, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description="", tags=None, privacyStatus="private", client_secrets_file="client_secrets.json", credentials_file="token.json"):
    """
    Uploads a video file to YouTube (resumable upload). Returns the uploaded video id.
    """
    youtube = get_authenticated_service(client_secrets_file, credentials_file)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or []
        },
        "status": {
            "privacyStatus": privacyStatus
        }
    }

    media_body = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True, mimetype="video/*")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media_body
    )

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if response:
                return response.get("id")
        except Exception as e:
            error = e
            retry += 1
            if retry > 5:
                raise
            sleep_time = (2 ** retry)
            time.sleep(sleep_time)
    return None
