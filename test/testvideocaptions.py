from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_oauthlib.flow
import json
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

class CaptionTest:
    def __init__(self, client_secrets_file='client_secrets3.json'):
        self.client_secrets_file = client_secrets_file
        self.client = None
        self.scopes = SCOPES
        self.api_service_name = API_SERVICE_NAME
        self.api_version = API_VERSION
        self.authenticate_youtube()

    def authenticate_youtube(self):
        # Load client secrets from the JSON file
        with open(self.client_secrets_file) as file:
            client_secrets = json.load(file)

        # Create credentials flow from client secrets
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes)

        # Run the OAuth flow and obtain credentials
        credentials = flow.run_local_server(port=8080)

        # Build the YouTube API client
        self.client = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials)

    def find_video_with_captions(self):
        search_response = self.client.search().list(
            part='snippet',
            q='Closed captions',
            type='video',
            videoCaption='closedCaption',
            maxResults=10
        ).execute()

        for item in search_response['items']:
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            print("Checking video:", video_id, "-", video_title)

            # Check if third-party contributions are enabled for captions
            video_response = self.client.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()

            video = video_response['items'][0]
            status = video['status']
            if status['license'] == 'youtube' and status['publicStatsViewable']:
                print("Third-party contributions enabled. Video ID:", video_id)
                return video_id

        print("No video found with enabled third-party contributions for captions.")
        return None

    def get_video_captions(self, video_id):
        captions_response = self.client.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()

        captions = captions_response.get('items', [])

        if captions:
            caption_id = captions[0]['id']
            caption_text = self.retrieve_caption_text(caption_id)
            return caption_text

        return None

    def retrieve_caption_text(self, caption_id):
        caption_response = self.client.captions().download(
            id=caption_id,
            tfmt='srt'
        ).execute()

        caption_text = caption_response.decode("utf-8")
        return caption_text


# Instantiate the CaptionTest class
caption_test = CaptionTest()

# Find a video with enabled third-party contributions for captions
video_id = caption_test.find_video_with_captions()

if video_id:
    print("Found video with captions. Video ID:", video_id)

    # Download captions for the video
    captions = caption_test.get_video_captions(video_id)

