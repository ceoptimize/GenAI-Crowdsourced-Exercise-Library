from googleapiclient.discovery import build
import re
import json
from  postgres import PostgresDatabase
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow



SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


#channel_ids = ['UCXrWnUUIza2gpaXhVknC55Q']
channel_ids = ['UCpyjZrR0so-aHFIyg2U0cyw', 'UCXrWnUUIza2gpaXhVknC55Q']
#search_query = 'intitle:"Landmine Lateral Raise"'
#channel_id = 'UCpyjZrR0so-aHFIyg2U0cyw'
 #   "VideoID" string   NOT NULL,
#    "ChannelID" string   NOT NULL,
#    "ChannelName" string   NOT NULL,
#    "ChannelHandle" string   NOT NULL,
#    "ThumbnailUrl" string   NOT NULL,
#    "Duration" int   NOT NULL,
#    "GenderCount" int   NOT NULL,
#    "Lighting" int   NOT NULL,
#    "Audio" int   NOT NULL,

class Youtube:
    def __init__(self, search_query = None):
       # self.api_key = 'AIzaSyBc9qycvVaBAeG9DV8KewsLKGnmVyBUkgk' #crowdsourcevideo project
        self.api_key = 'AIzaSyBxz4yP7xttz7Xe59ZNfaYCHIP_N8VBc9Q'  #crowdsourcevideo2 project
        self.channel_ids = channel_ids
        self.search_params = {
            'q': search_query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': 50,
            'videoDuration' : 'short',
        }
        self.youtubebuild = self.youtubebuild() 
        self.videotablename = "youtubevideo"
        self.postgres = PostgresDatabase()
        self.videotablecolumns = self.postgres.get_table_columns(self.videotablename)
       # self.videotablecolumns = ["VideoId", "ChannelId", "ChannelName", "ChannelHandle", "ThumbnailUrl", "Duration"]
        self.videotableextracolumns = ["gendercount", "lighting", "audio"]

    def authenticate_youtube():
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file='client_secrets.json',
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        credentials = flow.run_local_server(port=0)
        youtube = build('youtube', 'v3', credentials=credentials)
        return youtube

    def convert_string_to_int(self, string_var):
        try:
            # Try to convert the string to an integer
            int_var = int(string_var)
            return int_var
        except ValueError:
            # If the string is not a number, set the integer variable to 0
            int_var = 0
            return int_var

    def youtubebuild(self, oauthenabled = False):
        if oauthenabled: 
            youtube = self.authenticate_youtube()
        else: 
            youtube = build('youtube', 'v3', developerKey=self.api_key)
       
        return youtube


    def insert_all_channel_ids_to_postgres(self, enable_limit=True):
        video_count = 0  # Counter for the number of videos processed
        for channel_id in self.channel_ids:
            if enable_limit and video_count >= 5:
                break
            self.get_channel_videos_insert_to_postgres(channel_id)
            video_count += 1
        self.postgres.close()
    

    def get_channel_videos_insert_to_postgres(self, channel_id, captions_enabled = False, limitvideocount = 5):
        page_token = None
        print(channel_id)
        res = self.youtubebuild.channels().list(part='snippet', id=channel_id).execute()
        channel_title = res['items'][0]['snippet']['title']
        channel_handle = res['items'][0]['snippet']['customUrl']
        
        print(channel_title)
        
        # This block of code retrieves videos from a YouTube channel, processes their data,
        # and inserts relevant information into a PostgreSQL database. It operates in an
        # infinite loop, fetching videos in batches of up to 50 until a certain limit is reached
        # or there are no more videos to retrieve. The loop breaks when either the limit
        # is less than 50 or there is no 'nextPageToken' indicating the end of the video list.
        while True:
            res =  self.youtubebuild.search().list(part='id', channelId=channel_id, maxResults=min(50, limitvideocount), type='video', pageToken=page_token).execute()
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
                    if captions_enabled:
                        captions = self.get_video_captions(video_id)
                        insertdatacolumns =  [video_id, videotitle, channel_id, channel_title, channel_handle, thumbnail, captions, totaltime]
                    else: 
                        insertdatacolumns =  [video_id, videotitle, channel_id, channel_title, channel_handle, thumbnail, 'None', totaltime]
                    print(self.videotablecolumns)
                    print(insertdatacolumns)
                    #filteredinsertdatacolumns = list(filter(lambda x: x not in self.videotableextracolumns, self.videotablecolumns))
                 #   self.postgres.insert_data(self.videotablename, self.videotablecolumns,  insertdatacolumns + [0] * len(self.videotableextracolumns))
                  

                     # Store the captions along with other data in the database
                    self.postgres.insert_data(self.videotablename, self.videotablecolumns, insertdatacolumns + [0] * len(self.videotableextracolumns))

            if(limitvideocount >= 50):
                page_token = res.get('nextPageToken')
                if not page_token:
                    break
            else: 
                break

    def get_video_data(self, video_id): 
        res = self.youtubebuild.videos().list(id=video_id, part='contentDetails, status, snippet').execute()
        duration = res['items'][0]['contentDetails']['duration']
        is_embeddable = res['items'][0]['status']['embeddable']
        print(is_embeddable)
        title = res['items'][0]['snippet']['title']
        thumbnails = res['items'][0]['snippet']['thumbnails']['default']['url']
        print(thumbnails)

        return duration, is_embeddable, thumbnails, title


    def is_short_duration(self, totaltime):
        if (totaltime < 60) & (totaltime > 5):
            return True
        else:
            return False

    def get_video_captions(self, video_id):
        captions_response = self.youtubebuild.captions().list(
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
        caption_response = self.youtubebuild.captions().download(
            id=caption_id
        ).execute()

        caption_text = caption_response['body']

        return caption_text



