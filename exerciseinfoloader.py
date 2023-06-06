from youtube import Youtube
from postgres import PostgresDatabase
from chatgptupdate import ChatGPT
import traceback
import concurrent.futures



class ExerciseLoader:
    def __init__(self):
        self.postgres = PostgresDatabase()
        self.youtube = Youtube()
        self.chatgpt = ChatGPT()

  
    
    def load_exercises_from_videos(self, videoid = None, printresults = False, insertnewrelations = False, limit = None):
       
        if videoid is not None:
            videotitle = self.postgres.get_video_title(videoid)
            self.load_exercise_from_video(videoid, videotitle, insertnewrelations=False)
        
        else: 
            videoandtitlearray = self.postgres.get_video_id_and_title_array(limit = limit)

          #  exercise_titles = [videoandtitle[1] for videoandtitle in videoandtitlearray]

                            # Define a function to process a single video
            def process_video(videoandtitle, chatgptinstance):
                    videoid, videotitle = videoandtitle
                    try:
                        json = chatgptinstance.get_exercise_details(videotitle, videoname=True)
                        self.postgres.load_json(json, youtubevideoId=videoid, insertnewrelations=False)
                    except Exception as e:
                        # Handle the error, log it, and continue with the loop
                        traceback_str = traceback.format_exc()
                        error_message = f"Error occurred for video ID: {videoid}\n"
                        error_message += f"Error message: {str(e)}\n"
                        error_message += f"Traceback:\n{traceback_str}\n"

                        log_filename = "error_log.txt"
                        with open(log_filename, "a") as log_file:
                            log_file.write(error_message)

                        # Log the error message and traceback to a file or print them
                        print(f"Error occurred for video ID: {videoid}")
                        print(f"Error message: {str(e)}")
                        print(f"Continuing with the loop...")

                        # Process videos in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(lambda videoandtitle: process_video(videoandtitle, self.chatgpt), videoandtitlearray)
                   # executor.map(process_video, videoandtitlearray, self.chatgpt)

            """
            print(videoandtitlearray)
            for videoandtitle in videoandtitlearray:
                videoid = videoandtitle[0]
                print(videoid)
                videotitle = videoandtitle[1]
                print(videotitle)
                self.load_exercise_from_video(videoid, videotitle, insertnewrelations=False)
                continue"""
                
        if(printresults):
            self.postgres.print_all_table_contents()
           

    def load_exercise_from_video(self, videoid, videotitle, insertnewrelations = False):
        try:
            json = self.chatgpt.get_exercise_details(videotitle, videoname=True)
            print(json)
            self.postgres.load_json(json, youtubevideoId = videoid, insertnewrelations=insertnewrelations)
        except Exception as e:
            # Handle the error, log it, and continue with the loop
            traceback_str = traceback.format_exc()
            error_message = f"Error occurred for video ID: {videoid}\n"
            error_message += f"Error message: {str(e)}\n"
            error_message += f"Traceback:\n{traceback_str}\n"

            log_filename = "error_log.txt"
            with open(log_filename, "a") as log_file:
                    log_file.write(error_message)

            # Log the error message and traceback to a file or print them
            print(f"Error occurred for video ID: {videoid}")
            print(f"Error message: {str(e)}")
            print(f"Continuing with the loop...")
            

    def load_exercise(self, exercisename, printresults = True, insertnewrelations = False):
        json = self.chatgpt.get_exercise_details(exercisename, videoname = False)
        print(json)
        #TODO perform check to see all teh values are within what you expect of json before trying to load to db
  
        self.postgres.load_json(json, insertnewrelations = insertnewrelations)
        print("done")

        if(printresults):
            self.postgres.print_all_table_contents()
         

          


