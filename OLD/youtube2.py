from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_oauthlib.flow
import json
import os
import googleapiclient.discovery
import googleapiclient.errors
from youtubeapis.postgres import PostgresDatabase
import re

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

channel_ids = ['UCpyjZrR0so-aHFIyg2U0cyw', 'UCXrWnUUIza2gpaXhVknC55Q']

class Youtube:
    def __init__(self, search_query=None, client_secrets_file='client_secrets3.json'):
        self.channel_ids = channel_ids
        self.client_secrets_file = client_secrets_file
        self.client = None
        self.scopes = SCOPES
        self.api_service_name = API_SERVICE_NAME
        self.api_version = API_VERSION
        self.authenticate_youtube()
        self.videotablename = "youtubevideo"
        self.videotablecolumns = ["VideoId", "ChannelId", "ChannelName", "ChannelHandle", "ThumbnailUrl", "Duration"]
        self.postgres = PostgresDatabase()
        self.videotableextracolumns = ["gendercount", "lighting", "audio"]

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

    def insert_all_channel_ids_to_postgres(self, enable_limit=True):
        video_count = 0  # Counter for the number of videos processed
        for channel_id in self.channel_ids:
            if enable_limit and video_count >= 5:
                break
            print("one")
            self.get_channel_videos_insert_to_postgres(channel_id)
            video_count += 1
        self.postgres.close()

    def get_channel_videos_insert_to_postgres(self, channel_id):
        page_token = None
        res = self.client.channels().list(part='snippet', id=channel_id).execute()
        channel_title = res['items'][0]['snippet']['title']
        channel_handle = res['items'][0]['snippet']['customUrl']
        while True:
            res = self.client.search().list(part='id', channelId=channel_id, maxResults=50, type='video', pageToken=page_token).execute()
            for item in res['items']:
                video_id = item['id']['videoId']
                video_duration, is_embeddable, thumbnail, videotitle = self.get_video_data(video_id)
                print(videotitle)
                pattern = "(?<=PT)(?P<minutes>\d*M)*(?P<seconds>\d*S)*"
                timegroups = re.findall(pattern,video_duration)
                minutes = self.convert_string_to_int(re.split('M', timegroups[0][0])[0])
                seconds = self.convert_string_to_int(re.split('S', timegroups[0][1])[0])
                totaltime = minutes*60+seconds

                if self.is_short_duration(totaltime) and is_embeddable:
                    print(f'Video ID: {video_id}, Duration: {video_duration}')
                    captions = self.get_video_captions(video_id)
                    insertdatacolumns =  [video_id, videotitle, channel_id, channel_title, channel_handle, thumbnail, captions, totaltime]
                    print(self.videotablecolumns)
                    print(insertdatacolumns)
                    #filteredinsertdatacolumns = list(filter(lambda x: x not in self.videotableextracolumns, self.videotablecolumns))
                 #   self.postgres.insert_data(self.videotablename, self.videotablecolumns,  insertdatacolumns + [0] * len(self.videotableextracolumns))
                  

                     # Store the captions along with other data in the database
                    self.postgres.insert_data(self.videotablename, self.videotablecolumns, insertdatacolumns + [0] * len(self.videotableextracolumns))


            page_token = res.get('nextPageToken')
            if not page_token:
                break

    def get_video_data(self, video_id):
        res = self.client.videos().list(id=video_id, part='contentDetails, status, snippet').execute()
        duration = res['items'][0]['contentDetails']['duration']
        is_embeddable = res['items'][0]['status']['embeddable']
        title = res['items'][0]['snippet']['title']
        thumbnails = res['items'][0]['snippet']['thumbnails']['default']['url']
        return duration, is_embeddable, thumbnails, title

    def is_short_duration(self, totaltime):
        if (totaltime < 60) & (totaltime > 5):
            return True
        else:
            return False

    def get_video_captions(self, video_id):
        captions_response = self.client.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()

        captions = captions_response.get('items', [])

        # Process captions as per your requirement
        captions_text = []
        for caption in captions:
            caption_language = caption['snippet']['language']
            caption_text = self.retrieve_caption_text(caption['id'])  # Implement a function to retrieve the caption text
            captions_text.append({'language': caption_language, 'text': caption_text})

        return captions_text

    def retrieve_caption_text(self, caption_id):
        caption_response = self.client.captions().download(
            id=caption_id
        ).execute()

        caption_text = caption_response['body']

        return caption_text

    def convert_string_to_int(self, string_var):
        try:
            # Try to convert the string to an integer
            int_var = int(string_var)
            return int_var
        except ValueError:
            # If the string is not a number, set the integer variable to 0
            int_var = 0
            return int_var