from youtube import Youtube
from postgres import PostgresDatabase
from chatgptupdate import ChatGPT



class ExerciseLoader:
    def __init__(self):
        self.postgres = PostgresDatabase()
        self.youtube = Youtube()
        self.chatgpt = ChatGPT()

  

    def load_exercises_from_videos(self, videoid = 'ALL', printresults = False, insertnewrelations = False):
       
        if videoid != 'ALL':
           videotitle = self.postgres.get_video_title(videoid)
           json = self.chatgpt.get_exercise_details(videotitle, videoname=True)
           print(json)
           #TODO perform check to see all teh values are within what you expect of json before trying to load to db    
           self.postgres.load_json(json, youtubevideoId = videoid, insertnewrelations=insertnewrelations)
           print("done")
        else: 
           videoandtitlearray = self.postgres.get_video_id_and_title_array()
           print(videoandtitlearray)
           for videoandtitle in videoandtitlearray:
               videoid = videoandtitle[0]
               print(videoid)
               videotitle = videoandtitle[1]
               print(videotitle)
               json = self.chatgpt.get_exercise_details(videotitle, videoname=True)
               print(json)
               #TODO perform check to see all teh values are within what you expect of json before trying to load to db    
               self.postgres.load_json(json, youtubevideoId = videoid, insertnewrelations=insertnewrelations)
               print("done")


        if(printresults):
            self.postgres.print_all_table_contents()
            """
            table_names = self.postgres.get_tables(printenabled = False)
            for table_name in table_names:
                  query = f'SELECT * FROM {table_name} LIMIT 25'
                  result = self.postgres.fetch_query(query)
                  print(f"{table_name} table:")
                  for row in result:
                     print(row)"""

    def load_exercise(self, exercisename, printresults = True, insertnewrelations = False):
        json = self.chatgpt.get_exercise_details(exercisename, videoname = False)
        print(json)
        #TODO perform check to see all teh values are within what you expect of json before trying to load to db
  
        self.postgres.load_json(json, insertnewrelations = insertnewrelations)
        print("done")

        if(printresults):
            self.postgres.print_all_table_contents()
            """
            table_names = self.postgres.get_tables(printenabled = False)
            for table_name in table_names:
                  query = f'SELECT * FROM {table_name} LIMIT 25'
                  result = self.postgres.fetch_query(query)
                  print(f"{table_name} table:")
                  for row in result:
                     print(row)"""

          


