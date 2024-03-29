from gptquestiongenerator import QuestionGenerator
from modelpricing import ModelPricing
import hashlib
import datetime 
import sys
import os
from openai import OpenAI
from pymongo import MongoClient
from openai_communication import OpenAICommunication, TikTokenCommunication
from mongodb import MongoDBManager
import json
import tiktoken
from postgres import PostgresDatabase
import logging


# Load the configuration
CONFIG_PATH = 'config/config.json'
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

# Initialize communication and database manager
openai_comm = OpenAICommunication(api_key=os.environ.get("OPENAI_API_KEY", config['openai']['api_key']))
tiktoken_comm = TikTokenCommunication()
mongodb_manager = MongoDBManager(
    uri=os.environ.get("MONGODB_URI", config['mongodb']['uri']),
    db_name=config['mongodb']['database'],
    gpt_entries_coll=config['mongodb']['collections']['gpt_entries'],
    unsent_question_maps_coll=config['mongodb']['collections']['unsent_question_maps']
)


def generate_gpt_response(messages, model="gpt-3.5-turbo", max_tokens=180, temperature=0):
    print(messages)
    response = openai_comm.chat_completion_request(
        messages, model, max_tokens, temperature)
    print(response)
    response_content = response.choices[0].message.content

    prompt_tokens_gpt = response.usage.prompt_tokens
    print(response.usage)
    completion_tokens_gpt = response.usage.completion_tokens

    return response_content, prompt_tokens_gpt, completion_tokens_gpt


def write_gpt_response_to_mongodb(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, max_tokens, total_cost, temperature, model, input_feature_list: list, output_feature, question_map, user_response, messages, message_hash):
    # Create a dictionary for the new data
    logger = setup_logger(name = 'mongo_db_logger', log_file = 'logs/mongo_db.log', level = logging.ERROR)
    try:
        input_features_dicts = [{"feature": feature, "value": value}
                                for feature, value in input_feature_list]
        new_data = {
            "response_content": response_content,
            "prompt_tokens_tiktoken": prompt_tokens_tiktoken,
            "prompt_tokens_gpt": prompt_tokens_gpt,
            "completion_tokens_gpt": completion_tokens_gpt,
            "max_tokens_prompt": max_tokens,
            "total_cost": total_cost,
            "temperature": temperature,
            "model": model,
            "input_features": input_features_dicts,
            "output_feature": output_feature,
            "question_map": question_map,
            "user_response": user_response,
            "messages": messages,
            "message_hash": message_hash,  # Add the hash of the message
            "timestamp": datetime.datetime.now(),
        }

        # Insert the new data into MongoDB
        inserted_document = mongodb_manager.insert_gpt_entry(new_data)
        print(f"Document inserted with _id: {inserted_document.inserted_id}")
    except Exception as e:
         # Log the exception with detailed context
        logger.exception(f"Error inserting document into MongoDB: {e} - Data: {new_data}")


def write_gpt_response_to_jsonlfile(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, max_tokens, total_cost, temperature, model, input_feature_list: list, output_feature, question_map, user_response,  messages, message_hash, filename='playground/json/gpt_response.json'):
    # Create a dictionary for the new data
    input_features_dicts = [{"feature": feature, "value": value}
                            for feature, value in input_feature_list]

    new_data = {
        "response_content": response_content,
        # Assuming you meant to use prompt_tokens_tiktoken here
        "prompt_tokens_tiktoken": prompt_tokens_tiktoken,
        "prompt_tokens_gpt": prompt_tokens_gpt,
        "completion_tokens_gpt": completion_tokens_gpt,
        "max_tokens_prompt": max_tokens,
        "total_cost": total_cost,
        "temperature": temperature,
        "model": model,
        "input_features": input_features_dicts,
        "output_feature": output_feature,
        "question_map": question_map,
        "user_response": user_response,
        "messages": messages,
        "message_hash": message_hash,  # Add the hash of the message
        "timestamp": datetime.datetime.now().isoformat(),
    }

    # Append the new data as a JSON Line
    with open(filename, "a") as f:  # Using "a" mode to append to the file
        json.dump(new_data, f)
        f.write("\n")  # Ensure the next record is on a new line


def calculate_cost_of_gpt_response(prompt_tokens, completion_tokens_gpt, model):
    model_pricing = ModelPricing()
    input_cost, output_cost, token_basis = model_pricing.get_model_cost(model)
    if input_cost and output_cost and token_basis:
        input_cost = input_cost * (prompt_tokens / token_basis)
        output_cost = output_cost * (completion_tokens_gpt / token_basis)
        total_cost = input_cost + output_cost
        return total_cost
    else:
        return None


def setup_logger(name, log_file, level=logging.ERROR):
    """Set up and return a logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:  # Avoid adding multiple handlers to the same logger
        logger.setLevel(level)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger




class QuestionMapProcessor:

    """
    Processes all the question maps from one question map filepath, and handles interactions with GPT models and databases.
    """
     
    def __init__(self, openai_comm, tiktoken_comm, db_manager, pg, question_map_type="initial", model="gpt-4-0125-preview",
                 role="personal trainer", max_tokens=300, temperature=0, interactive=False,
                 previewmessage=True, sendtoGPT=False, writetojson=False, writetomongo=False):
        """
        Initializes the FeatureQuestionProcessor with API communication instances, database manager, and other settings.
        
        Parameters:
            openai_comm (OpenAICommunication): An instance for OpenAI API communication.
            tiktoken_comm (TikTokenCommunication): An instance for TikToken API communication.
            db_manager (MongoDBManager): An instance for MongoDB operations.
            model (str): The GPT model to use for generating responses.
            role (str): The role to use in the question generation process.
            max_tokens (int): Maximum number of tokens in the GPT response.
            temperature (float): Temperature for the GPT response generation.
            interactive (bool): Whether to interactively ask the user to send requests to GPT.
            previewmessage (bool): Whether to preview the message before sending it to GPT.
            sendtoGPT (bool): Whether to send the message to GPT for processing.
            writetojson (bool): Whether to write the response to a JSONL file.
            writetomongo (bool): Whether to write the response to MongoDB.
        """
        self.openai_comm = openai_comm
        self.tiktoken_comm = tiktoken_comm
        self.db_manager = db_manager
        self.qg = QuestionGenerator(role=role)
        self.pg = pg
        self.input_feature_list = []
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.interactive = interactive
        self.previewmessage = previewmessage
        self.sendtoGPT = sendtoGPT
        self.writetojson = writetojson
        self.writetomongo = writetomongo
        self.role = role
        self.question_map_type = question_map_type

        # Determine the question map file path based on the type
        if question_map_type == "initial":
            self.question_map_filepath = config['questionmapfilepath']['initial']
        elif question_map_type == "general":
            self.question_map_filepath = config['questionmapfilepath']['general']
        elif question_map_type == "secondary":
            self.question_map_filepath = config['questionmapfilepath']['secondary']
        else:
            raise ValueError(f"Invalid question map type: {question_map_type}")

    def message_generator(self, system_message_role, system_message_formatting, user_message):

        """
        Generates a message dictionary for interaction with the GPT model.

        Parameters:
            system_message_role (str): The role of the system in the message.
            system_message_formatting (str): The formatting of the system message.
            user_message (str): The user's message.

        Returns:
            list: A list of message dictionaries.
        """

        return [
            {"role": "system", "content": system_message_role +
                " " + system_message_formatting},
            {"role": "user", "content": user_message},
        ]

    def process_map(self):
            logger = setup_logger('process_map_logger', 'logs/process_map.log')
      #  try:
            with open(self.question_map_filepath, "r") as f:
                for line_number, line in enumerate(f, 1):
                    try:
                        question_map = json.loads(line)
                    except json.JSONDecodeError as e:
                        error_msg = f"Error decoding JSON on line {line_number} of {self.question_map_filepath}: {e.msg}"
                        logger.error(error_msg)
                        continue
                    
                    # Process the question map based on its type
                    if self.question_map_type == "initial" or self.question_map_type == "general":
                        self.process_initial_general_question(
                            question_map, self.previewmessage, self.sendtoGPT, self.writetojson, self.writetomongo)
                    elif self.question_map_type == "secondary":
                        self.process_secondary_question(
                            question_map, self.previewmessage, self.sendtoGPT, self.writetojson, self.writetomongo)
                    else:
                        print("Invalid question map type")
                        return None
   #     except Exception as e:
      #      logger.exception(f"Failed to process the file {self.question_map_filepath}: {e}")

    

    def process_initial_general_question(self, question_map, previewmessage, sendtoGPT, writetojson, writetomongo):
        self.skip_remaining = False  # Reset the flag for each new question map
        self.auto_process_remaining = False  # Reset the flag for each new question map
        feature1 = question_map["feature_pair"][0]
        feature2 = question_map["feature_pair"][1]
        include_choices = question_map["include_choices"] if "include_choices" in question_map else None
        json_format = question_map["json_format"] if "json_format" in question_map else None
        feature1values = self.pg.get_single_feature_values_from_db(feature1)

        for feature1value in feature1values:
            if self.skip_remaining:
                print(
                    f"Skipping remaining items for feature '{feature1}' due to 'na' response.")
                break  # Exit the loop early

            self.input_feature_list.append((feature1, feature1value))
            system_message_role, system_message_formatting, user_message = self.qg.generate_question(
                ((feature1, feature1value), feature2), json_format=json_format, include_choices=include_choices)
            messages = self.message_generator(
                system_message_role, system_message_formatting, user_message)
            self.process_messages(question_map, messages, previewmessage, sendtoGPT, writetojson,
                                  writetomongo, self.input_feature_list, feature2, 'playground/json/gpt_response.json')

    
    def process_secondary_question(self, question_map,  previewmessage, sendtoGPT, writetojson, writetomongo, max_tokens, temperature):
        self.skip_remaining = False  # Reset the flag for each new question map
        self.auto_process_remaining = False  # Reset the flag for each new question map
        featurepair1 = question_map["feature_pair1"]
        featurepair2 = question_map["feature_pair2"]
        feature1a = featurepair1[0]
        feature1b = featurepair1[1]
        feature1rel = featurepair1[2] if len(featurepair1) > 2 else None
        feature2a = featurepair2[0]
        feature2b = featurepair2[1] if len(featurepair2) > 1 else None
        feature2rel = featurepair2[2] if len(featurepair2) > 2 else None
        include_choices = question_map["include_choices"] if "include_choices" in question_map else None
        json_format = question_map["json_format"] if "json_format" in question_map else None
        feature1avalues = self.pg.get_single_feature_values_from_db(feature1a)
        feature1bvalues = self.pg.get_single_feature_values_from_db(feature1b)

        for feature1avalue in feature1avalues:
            for feature1bvalue in feature1bvalues:
                if self.skip_remaining:
                    print(
                        f"Skipping remaining items for feature '{feature1a}' and '{feature1b}' due to 'na' response.")
                    return  # Exit the function early
                self.input_feature_list.append((feature1a, feature1avalue))
                self.input_feature_list.append((feature1b, feature1bvalue))
                system_message_role, system_message_formatting, user_message = self.qg.generate_question_double(
                    ((feature1a, feature1avalue), feature1b, feature1bvalue), feature1rel, feature2a, json_format=json_format, include_choices=include_choices)
                messages = self.message_generator(
                    system_message_role, system_message_formatting, user_message)
                self.process_messages(question_map, messages, previewmessage, sendtoGPT, writetojson,
                                      writetomongo, self.input_feature_list, feature2a, 'playground/json/gpt_response.json')

    def process_messages(self, question_map, messages, previewmessage, sendtoGPT, writetojson, writetomongo, input_feature_list, output_feature, filename):
        prompt_tokens_tiktoken = self.tiktoken_comm.num_tokens_from_messages(
            messages)
        predicted_total_cost = calculate_cost_of_gpt_response(
            prompt_tokens_tiktoken, self.max_tokens, self.model)

        if previewmessage:
            print(json.dumps(messages, indent=4))
            print(
                f"Number of tokens: {prompt_tokens_tiktoken} and predicted cost: {predicted_total_cost}")

        if sendtoGPT and self.interactive and not self.auto_process_remaining:
            user_response = input(
                "Send to ChatGPT? (y/n/ya/exit/edit): ").strip().lower()
            if user_response == 'edit':
                print("Current message:", messages[-1]['content'])
                edited_message = input(
                    "Enter the edited message or press enter to keep it unchanged: ")
                if edited_message:
                    messages[-1]['content'] = edited_message
            if user_response in ['y', 'ya', 'edit']:
                if user_response == 'ya':
                    self.auto_process_remaining = True
                response_content, prompt_tokens_gpt, completion_tokens_gpt = generate_gpt_response(
                    messages, model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
            elif user_response == 'na':
                print("Skipping all remaining messages for this question map.")
                self.skip_remaining = True
                # send unsent question map to unsent collection along with the messages and the user response
                db_manager.unsent_question_maps_coll.insert_one(
                    {"question_map": question_map, "messages": messages, "user_response": user_response})
                return
            elif user_response == 'n':
                print("Message not sent to ChatGPT.")
                # send unsent question map to unsent collection along with the messages
                db_manager.unsent_question_maps_coll.insert_one(
                    {"question_map": question_map, "messages": messages, "user_response": user_response})

                return  # Stop processing this message
            elif user_response == 'exit':
                print("Exiting the program.")
                sys.exit()

        # If auto_process_remaining is True, automatically process the messages without user interaction
        elif sendtoGPT and self.auto_process_remaining:
            response_content, prompt_tokens_gpt, completion_tokens_gpt = generate_gpt_response(
                messages, model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
            user_response = 'yaauto'
        elif sendtoGPT and not self.interactive:
            response_content, prompt_tokens_gpt, completion_tokens_gpt = generate_gpt_response(
                messages, model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
            user_response = 'auto'
        else:
            print("Preview only.")
            return

        # Calculate a hash for the message
        message_hash = hashlib.sha256(json.dumps(
            messages, sort_keys=True).encode()).hexdigest()

        total_cost = calculate_cost_of_gpt_response(
            prompt_tokens_gpt, completion_tokens_gpt, self.model)
        # Process the response content
        if sendtoGPT and writetojson:
            write_gpt_response_to_jsonlfile(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, self.max_tokens,
                                            total_cost, self.temperature, self.model, input_feature_list, output_feature, question_map, user_response, messages, message_hash)
        if sendtoGPT and writetomongo:
            write_gpt_response_to_mongodb(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, self.max_tokens,
                                          total_cost, self.temperature, self.model, input_feature_list, output_feature, question_map, user_response,  messages, message_hash)


if __name__ == "__main__":
    openai_comm = OpenAICommunication(api_key=os.environ.get("OPENAI_API_KEY", config['openai']['api_key']))
    tiktoken_comm = TikTokenCommunication()

    db_manager = MongoDBManager(
        uri=os.environ.get("MONGODB_URI", config['mongodb']['uri']),
        db_name=config['mongodb']['database'],
        gpt_entries_coll=config['mongodb']['collections']['gpt_entries'],
        unsent_question_maps_coll=config['mongodb']['collections']['unsent_question_maps']
    )

    pg = PostgresDatabase()
    

    # Choose the question map based on your requirements
   # question_map_filepath = config['questionmapfilepath']['initial']  # For example, using the initial question map

   
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

    

    '''
    MAP OUT THE DIFFERENT SCENARIOS 
      e.g. user says proceed but the job fails
          user says proceed and the job succeeds
          user says don't proceed

          and for ones where we dont proceed then when we change the input files how does that get loaded back in
    Desired process:
    1. Iterate though a list of features and values
        a. Generate a question DONE
        b. User inputs submit if they want to proceed (in console?) DONE
        c. If yes, send to GPT and write to MongoDB DONE
        d. For ones where the user does not want to proceed, write to JSONL file or data store for later processing (or write both, with an indicator of y/ya/n?, also with dates? Add a y/ya/n? indicator to the JSONL file or data store for later processing) DONE
        e. Need some error handling/logging when reading the jsonL file and processing the messages and writing to mongo FAILS
        e. For ones that did get processed, write the features and values to a mapping table so we know what features we have processed. This mapping table will later
        be used to update the Postgres database with the new features and values.
    

    '''
