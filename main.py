import re
from postgres import PostgresDatabase
import pandas as pd
import tabulate
from youtube import Youtube
from videoloader import VideoLoader
from exerciseinfoloader import ExerciseLoader


postgres = PostgresDatabase()

#drops current tables and recreates them 
def run(load_new_videos = False):
    if load_new_videos:
    #load_new_videos just means we want to reach out to Youtube and load the videos in again. If you don't you
    #are just going out to openai to get the information about the videos already loaded
        postgres.drop_schema()
        postgres.execute_sql_file('DBD/QuickDBD-Free Diagram-14.sql')
        postgres.get_tables()

        #loads videos into the youtube video table
        vl = VideoLoader()
        vl.loadExerciseBasedVideos(max_videos_per_exercise=3, limit_inserts = True, insertnewrelations = True)
       # vl.loadChannelBasedVideos(enable_limit = True)

        #gets the name of the exercises based off the videos 
        #el = ExerciseLoader()
        #el.load_exercises_from_videos(insertnewrelations=True, limit = 11)

        #prints all the tables and their contents
      #  postgres.print_all_table_contents()
        postgres.get_video_id_array()
        postgres.print_all_table_contents()
    else:

        postgres.truncate_tables(tables_to_keep=['youtubevideo'])
        postgres.get_tables()
            #gets the name of the exercises based off the videos 
        el = ExerciseLoader()
        el.load_exercises_from_videos(insertnewrelations=True, limit = 11)

        #prints all the tables and their contents
        postgres.print_all_table_contents()

        #connects the tables into a denormalizaed view using keys
        #table = postgres.get_denormalized_table()
        #for row in table:
        #    print(row)

def connect_tables():
        table = postgres.get_denormalized_table()
        for row in table:
            print(row)


run(load_new_videos=True)
#connect_tables()





# Print the current database name
#print("Current Database:", current_db)
#print(queryresults)
postgres.close()
#df = pd.DataFrame(queryresults)
#print(df)
#print(tabulate.tabulate(df, headers='keys', tablefmt='psql'))