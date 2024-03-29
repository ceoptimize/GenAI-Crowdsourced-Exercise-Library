import os
from openai import OpenAI
from pymongo import MongoClient
from openai_communication import OpenAICommunication, TikTokenCommunication
from mongodb import MongoDBManager
import json
import tiktoken
from postgres import PostgresDatabase
import logging
from GPTtoMongo import QuestionMapProcessor
import stringfunctions as stringfunctions


# Load the configuration
CONFIG_PATH = 'config/config.json'
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)


def load_and_update_postgres_from_mongo(postgres, collection, get_features_from_response = True):
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


def main():
    openai_comm = OpenAICommunication(api_key=os.environ.get("OPENAI_API_KEY", config['openai']['api_key']))
    tiktoken_comm = TikTokenCommunication()

    db_manager = MongoDBManager(
        uri=os.environ.get("MONGODB_URI", config['mongodb']['uri']),
        db_name=config['mongodb']['database'],
        gpt_entries_coll=config['mongodb']['collections']['gpt_entries'],
        unsent_question_maps_coll=config['mongodb']['collections']['unsent_question_maps']
    )

    pg = PostgresDatabase()

   
    processor = QuestionMapProcessor(
        openai_comm=openai_comm,
        tiktoken_comm=tiktoken_comm,
        pg = pg,
        db_manager=db_manager,
        max_tokens=300,
        temperature=0,
        role="personal trainer",
        model="gpt-4-0125-preview",
        question_map_type="initial",
        previewmessage=True,
        sendtoGPT=True,
        interactive=True,
        writetojson=True,
        writetomongo=True
    )

    processor.process_map()

    #TODO: Add logic to load and update Postgres with data from MongoDB



if __name__ == "__main__":
    main()