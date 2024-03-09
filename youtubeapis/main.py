import re
from youtubeapis.postgres import PostgresDatabase
import tabulate
from youtubeapis.youtube import Youtube
from youtubeapis.videoloader import VideoLoader
from youtubeapis.exerciseinfoloader import ExerciseLoader
import os
import youtubeapis.stringfunctions as stringfunctions
from pymongo import MongoClient
import json


postgres = PostgresDatabase()

# drops current tables and recreates them
mongoclient = MongoClient('mongodb+srv://ceoptimize:C$g$9292greer@ceoptimize.i3l3wkq.mongodb.net/')
db = mongoclient['ExerciseDB']
collection = db['GPTEntries']


def run(load_new_videos=False):
    if load_new_videos:
        # load_new_videos just means we want to reach out to Youtube and load the videos in again. If you don't you
        # are just going out to openai to get the information about the videos already loaded
        postgres.drop_schema()
        postgres.execute_sql_file('DBD/Postgresschema.sql')
        postgres.get_tables()
        postgres.load_valid_data('jsondata/validdata.json')
        postgres.load_valid_relationships(
            'jsondata/validdatarelationship.json')
       # postgres.load_gpt_json_data()
      #  run_for_all_answer_files('supportsurface_bodyposition')
     #   run_for_all_answer_files('body position', 'support surface')
     #   run_for_all_answer_files('support surface', 'body position')
        load_and_update_postgres_from_mongo(collection)

       # postgres.load_manualgpt_support_surface_body_position_data('questionsandanswers/supportsurface_bodyposition/answers_supportsurface_bodyposition.json')
     #   postgres.load_manualgpt_body_position_support_surface_data('questionsandanswers/bodyposition_supportsurface/answers_bodyposition_supportsurface.json')

        # loads videos into the youtube video table
        # vl = VideoLoader()
        # vl.loadExerciseBasedVideos(max_videos_per_exercise=3, limit_inserts = True, insertnewrelations = True)
       # vl.loadChannelBasedVideos(enable_limit = True)

        # gets the name of the exercises based off the videos
        # el = ExerciseLoader()
        # el.load_exercises_from_videos(insertnewrelations=True, limit = 11)

        # prints all the tables and their contents
      #  postgres.print_all_table_contents()
       # postgres.get_video_id_array()
     #   postgres.print_all_table_contents()
    else:

        postgres.truncate_tables(tables_to_keep=['youtubevideo'])
        postgres.get_tables()
        # gets the name of the exercises based off the videos
        el = ExerciseLoader()
        el.load_exercises_from_videos(insertnewrelations=True, limit=11)

        # prints all the tables and their contents
        postgres.print_all_table_contents()

        # connects the tables into a denormalizaed view using keys
        # table = postgres.get_denormalized_table()
        # for row in table:
        #    print(row)

def load_and_update_postgres_from_mongo(collection, get_features_from_response = True):
    documents = collection.find({})  # Adjust the query as needed
    for doc in documents:
      
      #  input_feature = doc["input_features"][0]["feature"]
     #   input_value = doc["input_features"][0]["value"]
      #  output_feature = doc["output_feature"]
        response_content = doc["response_content"]
        if response_content:
            try: 
                
                response_content_clean = stringfunctions.clean_json_response(response_content)
                response_data = json.loads(response_content_clean )
                response_data = stringfunctions.preprocess_response_content_keys(response_data)
               
                # Assuming the first key is the input feature and the second key is the output feature

                if get_features_from_response:
                    keys = list(response_data.keys())
                    input_feature = keys[0]
                    output_feature = keys[1]
                    input_value = response_data[input_feature]
                  #  print(f"input_feature: {input_feature}, input_value: {input_value}, output_feature: {output_feature}")
                else: 
                    input_feature = doc["input_features"][0]["feature"]
                    input_value = doc["input_features"][0]["value"]
                    output_feature = doc["output_feature"]

                print("Updating Postgres with Mongo _id:", doc['_id'])
        
                postgres.update_postgres_with_document_from_mongo(doc['_id'], input_feature, input_value, output_feature, response_data)

            except json.JSONDecodeError:
                print(f"Failed to parse JSON from response_content in document with _id: {doc['_id']}")



def run_for_all_answer_files(feature1, feature2):
    # Define the base directory by prepending 'questionsandanswers' to the given directory
    # the directory is the concatenation of the words in feature1 after removing spaces, a '_' and the words in feature2 after removing spaces
    directory = feature1.replace(' ', '') + '_' + feature2.replace(' ', '')
    base_directory = os.path.join('questionsandanswers', directory)

    # Define a dictionary mapping function names to function objects
   # function_map = {
   #     'supportsurface_bodyposition': postgres.load_manualgpt_support_surface_body_position_data,
   #     'bodyposition_supportsurface': postgres.load_manualgpt_body_position_support_surface_data
   #     # Add other functions here as needed
   # }

    # Check if the function_name is in the function_map
  #  if directory not in function_map:
  #      print(f"Invalid function name: {directory}")
  #      return

    # Walk through all subdirectories of the base directory
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            # Check if the current file starts with "answers_" and ends with ".json"
            if file.startswith('answers_') and file.endswith('.json'):
                # Construct the full path to the file
                file_path = os.path.join(root, file)

                # Extract the folder name directly below the base_directory from the root path
                # This assumes a standardized path structure
                folder_name = os.path.relpath(
                    root, base_directory).split(os.sep)[0]

                # Call the method with the full path
                postgres.load_manualgpt_feature1_feature2_data(
                    file_path, folder_name, feature1, feature2)
               # postgres.load_manualgpt_body_position_support_surface_data(file_path, folder_name)

                # Call the selected function with the file_path and folder_name as arguments
            #    selected_function = function_map[directory]
               # selected_function(file_path, folder_name)


def connect_tables():
    table = postgres.get_denormalized_table()
    for row in table:
        print(row)


run(load_new_videos=True)
# connect_tables()


# Print the current database name
# print("Current Database:", current_db)
# print(queryresults)
postgres.close()

# df = pd.DataFrame(queryresults)
# print(df)
# print(tabulate.tabulate(df, headers='keys', tablefmt='psql'))
