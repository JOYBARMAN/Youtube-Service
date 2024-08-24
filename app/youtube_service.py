import os, httplib2, pytz, tempfile

from rest_framework.exceptions import APIException

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from datetime import datetime, timedelta


class YoutubeServiceApi:
    def __init__(self):
        self.CLIENT_SECRET = "/home/joy/Desktop/Projects/youtube/client_secret.json"
        self.STORAGE = Storage("credentials.storage")
        self.SCOPES = ["https://www.googleapis.com/auth/youtube"]
        self.discovery_url = (
            "https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest"
        )
        self.credentials = self.authorize_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build(
            "youtube", "v3", http=self.http, discoveryServiceUrl=self.discovery_url
        )

    def authorize_credentials(self):
        # Fetch credentials from storage
        credentials = self.STORAGE.get()
        # If the credentials doesn't exist in the storage location then run the flow
        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(self.CLIENT_SECRET, scope=self.SCOPES)
            http = httplib2.Http()
            credentials = run_flow(flow, self.STORAGE, http=http)

        return credentials

    def get_schedule_date_time(self, days=0):
        # Get the current time in Bangladeshi Time (Asia/Dhaka)
        bangladesh_tz = pytz.timezone("Asia/Dhaka")
        publish_time = datetime.now(bangladesh_tz)

        if days > 0:
            publish_time = publish_time + timedelta(days=days)

        # Convert the publish time to UTC
        publish_time_utc = publish_time.astimezone(pytz.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        return publish_time_utc

    def get_media_file(self, video_path):
        # Save the InMemoryUploadedFile to a temporary file
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in video_path.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Define the media file object
            media_file = MediaFileUpload(temp_file_path, chunksize=-1, resumable=True)
            return media_file

        except Exception as e:
            raise APIException(f"Error processing the video file: {e}")

        finally:
            # Cleanup the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def upload_video(
        self, video_path, title: str, description: str, tags: list, category_id: int
    ):
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {"privacyStatus": "private"},
        }

        try:
            # Call the API's videos.insert method to upload the video on youtube
            videos = self.service.videos()
            response = videos.insert(
                part="snippet,status",
                body=body,
                media_body=self.get_media_file(video_path),
            ).execute()
            return response


        except HttpError as e:
            raise APIException(f"An HTTP error {e.resp.status} occurred: {e}")