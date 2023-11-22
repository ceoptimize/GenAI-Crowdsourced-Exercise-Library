from youtube import Youtube
from postgres import PostgresDatabase
from chatgptupdate import ChatGPT
import traceback
import datetime
import error

exercises = ['deadlift', 'squat', 'lunge']

def log_error(video_id, error):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    traceback_str = traceback.format_exc()
    error_message = f"Timestamp: {timestamp}\n"
    error_message += f"Error occurred for video ID: {video_id}\n"
    error_message += f"Error message: {error}\n"
    error_message += f"Traceback:\n{traceback_str}\n"

    log_filename = "error_log.txt"
    with open(log_filename, "a") as log_file:
        log_file.write(error_message)

class VideoLoader:
    def __init__(self):
        self.postgres = PostgresDatabase()
        self.youtube = Youtube()
        self.chatgpt = ChatGPT()
        self.videotableextracolumns = ["gendercount", "lighting", "audio"]
        self.videotablename = "youtubevideo"
        self.videotablecolumns = self.postgres.get_table_columns(self.videotablename)

    #func
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

            while True:
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
                            likely_exercise_video = self.chatgpt.is_likely_exercise_video(video_id, video_title, channel_title, transcript, total_time)

                            if int(likely_exercise_video)>0:
                                #if it is, proceed to populating the video table. 
                                #and get exercise details from ChatGPT and populate all the other tables
                                print("likely exercise video " + video_id)
                           
                                insert_data_columns = [
                                    video_id, video_title, likes, channel_id, channel_title, 'ChannelHandle', subscribers, thumbnail,
                                    transcript, total_time
                                ]
                                
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
                                print(query)                             
                                
                           
                                try:
                                    json_data = self.chatgpt.get_exercise_details(gptquerydata, query, 1)
                                    print(json_data)
                                except Exception as e:
                                    print(f"An error occurred: {str(e)}")
                                    log_error(video_id, str(e))  # Call the logging function

                                # Assuming that 'json_data' is correctly set to a default or fallback value if needed
                                try:
                                    self.postgres.load_json(json_data, youtubevideoId=video_id, insertnewrelations=insertnewrelations)
                                except Exception as e:
                                    print(f"An error occurred: {str(e)}")
                                    log_error(video_id, str(e))  # Call the logging function

                                video_count += 1  # Increment the video counter
                                if video_count >= max_videos_per_exercise:
                                    print(f"Inserted {max_videos_per_exercise} videos for {exercise}, moving to next exercise.")
                                    break
                            else:
                                print("unlikely exercise video " + video_id)
            
                page_token = search_response.get('nextPageToken')
                if not page_token or video_count >= max_videos_per_exercise:
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

    def loadChannelBasedVideos(self, printresults = False, enable_limit=True):
        self.youtube.insert_all_channel_ids_to_postgres(enable_limit)
        if(printresults):
            query = """
                SELECT *
                FROM youtubevideo
                LIMIT 5;
                """
            result = self.postgres.fetch_query(query)
           


