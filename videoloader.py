from youtube import Youtube
from postgres import PostgresDatabase
from chatgptupdate import ChatGPT
import traceback
import log
import os
import shutil
import re


exercises = ['pushup', 'incline pushup', 'decline pushup', 'knee pushup']



class VideoLoader:
    def __init__(self):
        self.postgres = PostgresDatabase()
        self.youtube = Youtube()
        self.chatgpt = ChatGPT()
        self.videotableextracolumns = ["gendercount", "lighting", "audio"]
        self.videotablename = "youtubevideo"
        self.videotablecolumns = self.postgres.get_table_columns(self.videotablename)
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            shutil.rmtree(logs_dir)  # Remove the existing logs directory and all its contents
        os.makedirs(logs_dir)  # Create a fresh new logs directory
    
    def clean_transcript(self, transcript):

        # Remove special characters, including non-breaking spaces
        transcript = transcript.replace('\xa0', ' ')
      #  transcript = re.sub(r'[^\w\s]', '', transcript)
        transcript = transcript.encode('ascii', 'ignore').decode('ascii')

        # Convert to lowercase and remove extra whitespace
    #  transcript = transcript.lower()
        transcript = ' '.join(transcript.split())

        # Handle newlines and tabs
        transcript = transcript.replace('\n', ' ').replace('\t', ' ')

        return transcript
    
    #func
    def loadExerciseBasedVideos(self, exercises = exercises, printresults=False, max_videos_per_exercise=5, limit_inserts=False, insertnewrelations=False):
        """
        Take a list of exercise names and query Youtube for videos that are of a certain duration, have captions, and have that 
        exercise as the search query. Ask ChatGPT if this is likely an exercise demo and if it is, then populate
        each of the tables with the proper information about the video and the exercise. 
        """

        #for logging total number of successful and unsuccessful video loads
        total_successes = 0
        total_unlikely_videos = 0
        total_detail_failures = 0
        total_json_load_failures = 0

        for exercise in exercises:
            video_count = 0
            print(f"Searching for exercise: {exercise}")
            page_token = None

            while not limit_inserts or (limit_inserts and video_count < max_videos_per_exercise):
                       # Step 1: Use search().list() to find videos
                
                search_response = self.youtube.youtubebuild.search().list(
                    part='snippet',
                    q=exercise,
                    type='video',
                    maxResults=50,
                    videoDuration='short',
                    videoEmbeddable='true',
                    videoCaption='closedCaption',
                    safeSearch='strict',
                    pageToken=page_token
                ).execute()
                
             #   search_response = self.youtube.search_youtube(exercise, max_videos_per_exercise)
                #search_response = search_youtube()
             

                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                channel_ids = {item['snippet']['channelId'] for item in search_response.get('items', [])}

                  # Fetch video details using videos().list()
                videos_response =  self.youtube.youtubebuild.videos().list(
                    id=','.join(video_ids),
                    part='contentDetails,statistics,status'
                ).execute()

                # Fetch channel subscriber counts using channels().list()
                channels_response =  self.youtube.youtubebuild.channels().list(
                    id=','.join(channel_ids),
                    part='statistics'
                ).execute()

                for item in search_response.get('items', []):
                    video_id = item['id']['videoId']
                    video_info = next((v for v in videos_response.get('items', []) if v['id'] == video_id), None)
                    channel_id = item['snippet']['channelId']
                    channel_title = item['snippet']['channelTitle'] 
                    channel_info = next((c for c in channels_response.get('items', []) if c['id'] == channel_id), None)
                    
                    # Extract the necessary details
                    likes = video_info['statistics'].get('likeCount', '0') if video_info else '0'
                    subscribers = channel_info['statistics'].get('subscriberCount', '0') if channel_info else '0'
                    video_duration = video_info['contentDetails']['duration'] if video_info else None
                    is_embeddable = video_info['status']['embeddable'] if video_info else None
                    video_title = item['snippet']['title']
                    thumbnail = item['snippet']['thumbnails']['default']['url']
                   
                  #  video_duration, is_embeddable, thumbnail, video_title, likes = self.youtube.get_video_data(item)

                    # Extract minutes and seconds from duration string
                    minutes, seconds = self.youtube.extract_time_from_duration(video_duration)
                    total_time = minutes * 60 + seconds

                    if self.youtube.is_short_duration(total_time) and is_embeddable:
                        rawtranscript = self.youtube.get_transcript_from_api(video_id)
                        transcript = self.clean_transcript(rawtranscript)


                        try:
                            likely_exercise_video = self.chatgpt.is_likely_exercise_video(video_id, video_title, channel_title, transcript, total_time)

                            if int(likely_exercise_video) > 0:
                                insert_data_columns = [video_id, video_title, likes, channel_id, channel_title, 'ChannelHandle', subscribers, thumbnail, transcript, total_time]
            
                                # Insert video data into the database
                                self.postgres.insert_data(
                                    self.videotablename, self.videotablecolumns,
                                    insert_data_columns + [0] * len(self.videotableextracolumns), 'videoid'
                                )

                                gptquerydata = {
                                    'video_title': video_title,
                                    'channel_title': channel_title,
                                    'transcript': transcript,
                                    'total_time_seconds': total_time
                                }
                                query = self.chatgpt.formulate_chat_gpt_exercise_query(gptquerydata)
                                json_data = self.chatgpt.get_exercise_details(query, 2)
                                exercise_id, existingregressionids, existingprogressionids,existingvariationids = self.postgres.load_json(json_data, youtubevideoId=video_id, insertnewrelations=insertnewrelations)
                              #  self.postgres.handle_existing_exercises_adjustments(exercise_id, existingregressionids, existingprogressionids,existingvariationids, self.chatgpt)
                                
                                self.postgres.conn.commit()
                                video_count += 1
                                total_successes += 1
                                log.log_counter(exercise, video_id, video_title, likely_exercise_video, video_count)
                                if video_count >= max_videos_per_exercise:
                                    break
                            else:
                                self.postgres.conn.rollback()
                                total_unlikely_videos += 1
                                log.log_error(video_id, video_title, likely_exercise_video, "Unlikely exercise video detected", "no traceback")  # Ensure this function logs the error to the file
                        except Exception as e:
                            self.postgres.conn.rollback()
                            error_traceback = traceback.format_exc()
                            print(f"Rolling back any db updates for video {video_id} - error occurred:", str(e))
                            log.log_error(video_id, video_title, likely_exercise_video,  str(e), error_traceback)  # Log any exception that occurs
                            if 'exercise details' in str(e).lower():
                                total_detail_failures += 1
                            else:
                                total_json_load_failures += 1

                if video_count >= max_videos_per_exercise:
                    break           
                page_token = search_response.get('nextPageToken')
                if not page_token:
                    break

            print(f"Finished searching for {exercise}")

        # Log aggregate results after processing all exercises
        log.log_aggregate_results(total_successes, total_unlikely_videos, total_detail_failures, total_json_load_failures)

        if printresults:
            query = "SELECT * FROM youtubevideo LIMIT 5;"
            result = self.postgres.fetch_query(query)
    '''
    def loadExerciseBasedVideos(self, exercises = exercises, printresults = False, max_videos_per_exercise=5, limit_inserts = False, insertnewrelations = False):
        """
        Take a list of exercise names and query Youtube for videos that are of a certain duration, have captions, and have that 
        exercise as the search query. Ask ChatGPT if this is likely an exercise demo and if it is, then populate
        each of the tables with the proper information about the video and the exercise. 
        """
        for exercise in exercises:
            video_count = 0
            print(f"Searching for exercise: {exercise}")
            page_token = None

            while not limit_inserts or (limit_inserts and video_count < max_videos_per_exercise):
                # Step 1: Use search().list() to find videos
                search_response = self.youtube.youtubebuild.search().list(
                    part='snippet',
                    q=exercise,
                    type='video',
                    maxResults=max_videos_per_exercise,
                    videoDuration='short',
                    videoEmbeddable='true',
                    videoCaption='closedCaption',
                    safeSearch='strict',
                    pageToken=page_token
                ).execute()

                  # Collect video IDs and channel IDs from search results
                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                channel_ids = {item['snippet']['channelId'] for item in search_response.get('items', [])}

                # Fetch video details using videos().list()
                videos_response =  self.youtube.youtubebuild.videos().list(
                    id=','.join(video_ids),
                    part='contentDetails,statistics,status'
                ).execute()

                # Fetch channel subscriber counts using channels().list()
                channels_response =  self.youtube.youtubebuild.channels().list(
                    id=','.join(channel_ids),
                    part='statistics'
                ).execute()

                # Process video and channel responses to extract the necessary information
                for item in search_response.get('items', []):
                    video_id = item['id']['videoId']
                    video_info = next((v for v in videos_response.get('items', []) if v['id'] == video_id), None)
                    channel_id = item['snippet']['channelId']
                    channel_title = item['snippet']['channelTitle'] 
                    channel_info = next((c for c in channels_response.get('items', []) if c['id'] == channel_id), None)
                    
                    # Extract the necessary details
                    likes = video_info['statistics'].get('likeCount', '0') if video_info else '0'
                    subscribers = channel_info['statistics'].get('subscriberCount', '0') if channel_info else '0'
                    video_duration = video_info['contentDetails']['duration'] if video_info else None
                    is_embeddable = video_info['status']['embeddable'] if video_info else None
                    video_title = item['snippet']['title']
                    thumbnail = item['snippet']['thumbnails']['default']['url']
                   
                  #  video_duration, is_embeddable, thumbnail, video_title, likes = self.youtube.get_video_data(item)

                    # Extract minutes and seconds from duration string
                    minutes, seconds = self.youtube.extract_time_from_duration(video_duration)
                    total_time = minutes * 60 + seconds

                    if self.youtube.is_short_duration(total_time) and is_embeddable:
                     
                            transcript = self.youtube.get_transcript_from_api(video_id)

                            #Query the ChatGPT API to check if the video is likely an exercise video
                            try:
                                likely_exercise_video = self.chatgpt.is_likely_exercise_video(video_id, video_title, channel_title, transcript, total_time)

                                if int(likely_exercise_video)>0:
                                    insert_data_columns = [video_id, video_title, likes, channel_id, channel_title, 'ChannelHandle', subscribers, thumbnail, transcript, total_time]
            
                                    # Insert video data into the database
                                    self.postgres.insert_data(
                                        self.videotablename, self.videotablecolumns,
                                        insert_data_columns + [0] * len(self.videotableextracolumns), 'videoid'
                                    )

                                    gptquerydata = {
                                        'video_title': video_title,
                                        'channel_title': channel_title,
                                        'transcript': transcript,
                                        'total_time_seconds': total_time
                                    }
                                    query = self.chatgpt.formulate_chat_gpt_exercise_query(gptquerydata)
                                      
                                    json_data = self.chatgpt.get_exercise_details(gptquerydata, query, 1)
                                     # Load the JSON data into the database
                                    self.postgres.load_json(json_data, youtubevideoId=video_id, insertnewrelations=insertnewrelations)
     
                                    video_count += 1                           
                                else:
                                    raise Exception("Unlikely exercise video detected")
                                          
                                    
                            except Exception as e:
                                print(f"An error occurred for video ID {video_id}: {str(e)}")
                                log_error(video_id, str(e))
                                if "Unlikely exercise video" in str(e):
                                    # Log the unlikely exercise video and do not increment the video counter
                                    continue

                page_token = search_response.get('nextPageToken')
                if not page_token:
                    break

            # Outside the while loop, ready for the next exercise
            print(f"Finished searching for {exercise}")

        

        if(printresults):
            query = """
                SELECT *
                FROM youtubevideo
                LIMIT 5;
                """
            result = self.postgres.fetch_query(query)
    '''
    def loadChannelBasedVideos(self, printresults = False, enable_limit=True):
        self.youtube.insert_all_channel_ids_to_postgres(enable_limit)
        if(printresults):
            query = """
                SELECT *
                FROM youtubevideo
                LIMIT 5;
                """
            result = self.postgres.fetch_query(query)
           


