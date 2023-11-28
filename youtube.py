from googleapiclient.discovery import build
import re
import json
from  postgres import PostgresDatabase
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable






SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


#channel_ids = ['UCXrWnUUIza2gpaXhVknC55Q']
channel_ids = ['UCpyjZrR0so-aHFIyg2U0cyw', 'UCXrWnUUIza2gpaXhVknC55Q']
#starting_exercises = ['squat', 'deadlift', 'bench press', 'overhead press', 'bent over row', 'pull-up', 'chin-up', 'push-up', 'dip', 'lunge']
#starting_exercises = ['deadlift']
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
      #  self.api_key = 'AIzaSyBc9qycvVaBAeG9DV8KewsLKGnmVyBUkgk' #crowdsourcevideo project
      #  self.api_key = 'AIzaSyBxz4yP7xttz7Xe59ZNfaYCHIP_N8VBc9Q'  #crowdsourcevideo2 project
       # self.api_key =  'AIzaSyAvYkCC1husjU70PwUykUodl5PaWVpMVAY'
        self.api_key = 'AIzaSyC7Mf2gwPmI5mtAXXinAG565kE2VO_5Q9c' #crowdsourcedvideo4
     #   self.api_keys = [
           # 'AIzaSyCIGxPcXwnwizKyrmmXX-sYjcgruiMG6o4' #ceoptimize videoplatform
           # 'AIzaSyC7Mf2gwPmI5mtAXXinAG565kE2VO_5Q9c', #crowdsourcedvideo4
      #      'AIzaSyBxz4yP7xttz7Xe59ZNfaYCHIP_N8VBc9Q'  #crowdsorucedvideo2
           # 'AIzaSyAvYkCC1husjU70PwUykUodl5PaWVpMVAY', #crowdsourcedvideo3
           # 'AIzaSyBc9qycvVaBAeG9DV8KewsLKGnmVyBUkgk' #crowdsourcedvideo
            
     #   ]
   #     self.current_api_key_index = 0
 
        self.channel_ids = channel_ids
        self.search_params = {
            'q': search_query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': 50,
            'videoDuration' : 'short',
            'videoCaption': 'closedCaption', 
            'relevanceLanguage': 'en'
        }
        self.youtubebuild = self.build_youtube_client() 
  
    def rotate_api_key(self):
        self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_api_key_index]
        self.youtubebuild = self.build_youtube_client()  # Rebuild the client with the new API key

    
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

    def build_youtube_client(self, oauthenabled = False):
        if oauthenabled: 
            youtube = self.authenticate_youtube()
        else: 
            youtube = build('youtube', 'v3', developerKey=self.api_key)
           # youtube = build('youtube', 'v3', developerKey=self.api_keys[self.current_api_key_index])

       
        return youtube
    
    def search_youtube(self, exercise, max_results):
       # try:
        search_response = self.youtubebuild.search().list(
            part='snippet',
            q=exercise,
            type='video',
            maxResults=max_results,
            videoDuration='short',
            videoEmbeddable='true',
            videoCaption='closedCaption',
            safeSearch='strict'
        ).execute()
        return search_response
        '''
        except Exception as e:
            if "quota" in str(e).lower():
                self.rotate_api_key()
                return self.search_youtube(exercise, max_results)  # Retry the search with the new API key
            else:
                raise
        '''

    def extract_time_from_duration(self, duration):
        # Parse the ISO 8601 duration format from YouTube API response
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        return (hours * 60 + minutes), seconds

    def get_transcript_from_api(self, video_id): 
        try:
             # Retrieve the transcript using youtube_transcript_api
             transcript = YouTubeTranscriptApi.get_transcript(video_id)
                  # Concatenate transcript texts
             transcript_text = ' '.join([i['text'] for i in transcript])
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
             transcript_text = 'No transcript available'
        return transcript_text
    

    def get_video_data(self, item): 
        video_id = item['id']['videoId']
        res = self.youtubebuild.videos().list(id=video_id, part='contentDetails, status, snippet, statistics').execute()
        duration = res['items'][0]['contentDetails']['duration']
        is_embeddable = res['items'][0]['status']['embeddable']
        title = res['items'][0]['snippet']['title']
        thumbnails = res['items'][0]['snippet']['thumbnails']['default']['url']
        likes = res['items'][0]['statistics'].get('likeCount', '0')  # Use .get() to avoid KeyError if 'likeCount' does not exist

        return duration, is_embeddable, thumbnails, title, likes


    def is_short_duration(self, totaltime):
        if (totaltime < 60) & (totaltime > 5):
            return True
        else:
            return False

 

    '''
    def search_youtube_on_exercise(self, exercise, max_videos_per_exercise=50):
            print(f"Searching for exercise: {exercise}")
            self.search_params['q'] = exercise
            page_token = None
            videos_remaining = max_videos_per_exercise

            while videos_remaining > 0:
                search_response = self.youtubebuild.search().list(
                    part='id,snippet',
                    q=self.search_params['q'],
                    maxResults=min(50, videos_remaining),
                    type='video',
                    videoDuration='short',
                    videoCaption='closedCaption',
                    pageToken=page_token
                ).execute()

                items = search_response.get('items', [])
                if not items:
                    print(f"No results for {exercise}")
                    break  # Exit the while loop if no items are found

                for item in items:
                    video_id = item['id']['videoId']
                    video_duration, is_embeddable, thumbnail, video_title = self.get_video_data(video_id)

                    # Extract minutes and seconds from duration string
                    minutes, seconds = self.extract_time_from_duration(video_duration)
                    total_time = minutes * 60 + seconds

                    if self.is_short_duration(total_time) and is_embeddable:
                            try:
                                # Retrieve the transcript using youtube_transcript_api
                                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                                # Concatenate transcript texts
                                transcript_text = ' '.join([i['text'] for i in transcript])
                            except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
                                transcript_text = 'No transcript available'

                            # Insert the data into PostgreSQL database
                            insert_data_columns = [
                                video_id, video_title, item['snippet']['channelId'],
                                item['snippet']['channelTitle'], 'ChannelHandle', thumbnail,
                                transcript_text, total_time
                            ]

                            self.postgres.insert_data(
                                self.videotablename, self.videotablecolumns,
                                insert_data_columns + [0] * len(self.videotableextracolumns)
                            )


                videos_remaining -= len(items)
                page_token = search_response.get('nextPageToken')

                if not page_token:
                    break  # If there is no next page, exit the while loop

            # Outside the while loop, ready for the next exercise
            print(f"Finished searching for {exercise}")'''

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


   