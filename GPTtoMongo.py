import sys
import os
from openai import OpenAI
from pymongo import MongoClient

from api import Api
import json
import tiktoken
from postgres import PostgresDatabase
import logging

apikey = Api().chat_gpt_api

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", apikey))
from datetime import datetime
import hashlib

# Get the directory of the current script
current_dir = os.path.dirname(__file__)

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)
from modelpricing import ModelPricing
from gptquestiongenerator import QuestionGenerator 

mongoclient = MongoClient('mongodb+srv://ceoptimize:C$g$9292greer@ceoptimize.i3l3wkq.mongodb.net/')
db = mongoclient['ExerciseDB']
collection = db['GPTEntries']
unsentcollection = db['UnsentQuestionMaps']


initial_questions_map_filepath= "jsondata/initialquestiongeneratormap.jsonl"
questions_map_filepath = "jsondata/questiongeneratormap.jsonl"
secondary_questions_map_filepath = "jsondata/secondaryquestiongeneratormap.jsonl"



def chat_completion_request(messages, model= "gpt-3.5-turbo", max_tokens=180, temperature=0):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
    


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def generate_gpt_response(messages, model = "gpt-3.5-turbo", max_tokens= 180, temperature = 0):
    print(messages)
    response = chat_completion_request(messages, model, max_tokens, temperature)
    print(response)
    response_content =response.choices[0].message.content

   
    prompt_tokens_gpt = response.usage.prompt_tokens
    print(response.usage)
    completion_tokens_gpt = response.usage.completion_tokens

    return response_content, prompt_tokens_gpt, completion_tokens_gpt

def write_gpt_response_to_mongodb(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, max_tokens, total_cost, temperature, model, input_feature_list: list, output_feature, question_map, user_response, messages, message_hash):
        # Create a dictionary for the new data
    try: 
        input_features_dicts = [{"feature": feature, "value": value} for feature, value in input_feature_list]
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
            "timestamp": datetime.now(),
        }
        
        # Insert the new data into MongoDB
        inserted_document = collection.insert_one(new_data)
        print(f"Document inserted with _id: {inserted_document.inserted_id}")
    except Exception as e:
        # Log the error
      #  logging.error(f"Error inserting document into MongoDB: {e}")
        error_logger = setup_logger('mongo_db_insert_error_logger', 'logs/mongo_db_insert_error.log')
        #log the error along with the new_data
        error_logger.error(f"Error inserting document into MongoDB: {e} Data: {new_data}")
        print(f"Error inserting document into MongoDB: {e}")


    
def write_gpt_response_to_jsonlfile(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, max_tokens, total_cost, temperature, model, input_feature_list: list, output_feature, question_map, user_response,  messages, message_hash, filename = 'playground/json/gpt_response.json'):
    # Create a dictionary for the new data
    input_features_dicts = [{"feature": feature, "value": value} for feature, value in input_feature_list]

    new_data = {
        "response_content": response_content,
        "prompt_tokens_tiktoken": prompt_tokens_tiktoken,  # Assuming you meant to use prompt_tokens_tiktoken here
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
        "timestamp": datetime.now().isoformat(),
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



def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up a logger for error logging."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


    
class FeatureQuestionProcessor:
    def __init__(self, 
                 model="gpt-4-0125-preview", 
                 role = "personal trainer",
                 max_tokens=300, 
                 temperature=0, 
                 questions_map_filepath = initial_questions_map_filepath, 
                 interactive = False,
                 previewmessage=True, 
                 sendtoGPT=False, 
                 writetojson=False, 
                 writetomongo = False
                 ):
        self.qg = QuestionGenerator(role = role)
        self.pg = PostgresDatabase()
        self.input_feature_list = []
        self.interactive = interactive
        self.model = model
        self.questions_map_filepath = questions_map_filepath
        self.previewmessage = previewmessage
        self.sendtoGPT = sendtoGPT
        self.writetojson = writetojson
        self.writetomongo = writetomongo
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.auto_process_remaining = False
        self.skip_remaining = False
        self.process_map(questions_map_filepath, previewmessage, sendtoGPT, writetojson, writetomongo)



    def message_generator(self, system_message_role, system_message_formatting, user_message):
        return [
            {"role": "system", "content": system_message_role + " " + system_message_formatting},
            {"role": "user", "content": user_message},
        ]
    
    def process_map(self, filepath, previewmessage, sendtoGPT, writetojson, writetomongo):
        error_logger = setup_logger('question_map_error_logger', 'logs/question_map_error.log')
        with open(filepath, "r") as f:
        
            for line_number, line in enumerate(f, 1):
                try:
                    question_map = json.loads(line)
                except json.JSONDecodeError as e:
                    error_msg = f"Error decoding JSON on line {line_number} of {filepath}: {e.msg}\nProblematic line: {line.strip()}"
                    error_logger.error(error_msg)
                    continue
                question_map = json.loads(line)
                if filepath == initial_questions_map_filepath:
                    self.process_initial_general_question(question_map, previewmessage, sendtoGPT, writetojson, writetomongo)
                elif  filepath == questions_map_filepath:
                    self.process_initial_general_question(question_map,  previewmessage, sendtoGPT, writetojson, writetomongo)
                elif filepath == secondary_questions_map_filepath:
                    self.process_secondary_question(question_map, previewmessage, sendtoGPT, writetojson, writetomongo)
                else: 
                    print("Invalid questions map file path")
                    return None
                
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
                    print(f"Skipping remaining items for feature '{feature1}' due to 'na' response.")
                    break  # Exit the loop early

                self.input_feature_list.append((feature1, feature1value))
                system_message_role, system_message_formatting, user_message = self.qg.generate_question(((feature1, feature1value), feature2), json_format=json_format, include_choices = include_choices)
                messages = self.message_generator(system_message_role, system_message_formatting, user_message)
                self.process_messages(question_map, messages, previewmessage, sendtoGPT, writetojson, writetomongo, self.input_feature_list, feature2, 'playground/json/gpt_response.json')    

 

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
                            print(f"Skipping remaining items for feature '{feature1a}' and '{feature1b}' due to 'na' response.")
                            return  # Exit the function early
                        self.input_feature_list.append((feature1a, feature1avalue))
                        self.input_feature_list.append((feature1b, feature1bvalue))
                        system_message_role, system_message_formatting, user_message = self.qg.generate_question_double(((feature1a, feature1avalue), feature1b, feature1bvalue), feature1rel, feature2a, json_format = json_format, include_choices = include_choices)
                        messages = self.message_generator(system_message_role, system_message_formatting, user_message)
                        self.process_messages(question_map, messages, previewmessage, sendtoGPT, writetojson, writetomongo, self.input_feature_list, feature2a, 'playground/json/gpt_response.json')

   
    def process_messages(self, question_map, messages, previewmessage, sendtoGPT, writetojson, writetomongo, input_feature_list, output_feature, filename):
        prompt_tokens_tiktoken = num_tokens_from_messages(messages)
        predicted_total_cost = calculate_cost_of_gpt_response(prompt_tokens_tiktoken, self.max_tokens, self.model)
        
        if previewmessage:
            print(json.dumps(messages, indent=4))
            print(f"Number of tokens: {prompt_tokens_tiktoken} and predicted cost: {predicted_total_cost}")

        if sendtoGPT and self.interactive and not self.auto_process_remaining:
            user_response = input("Send to ChatGPT? (y/n/ya/exit/edit): ").strip().lower()
            if user_response == 'edit':
                print("Current message:", messages[-1]['content'])
                edited_message = input("Enter the edited message or press enter to keep it unchanged: ")
                if edited_message:
                    messages[-1]['content'] = edited_message
            if user_response in ['y', 'ya', 'edit']:
                if user_response == 'ya':
                    self.auto_process_remaining = True  
                response_content, prompt_tokens_gpt, completion_tokens_gpt = generate_gpt_response(messages, model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
            elif user_response == 'na':
                print("Skipping all remaining messages for this question map.")
                self.skip_remaining = True
                #send unsent question map to unsent collection along with the messages and the user response
                unsentcollection.insert_one({"question_map": question_map, "messages": messages, "user_response": user_response})
                return
            elif user_response == 'n':
                print("Message not sent to ChatGPT.")
                #send unsent question map to unsent collection along with the messages
                unsentcollection.insert_one({"question_map": question_map, "messages": messages, "user_response": user_response})
                
                return  # Stop processing this message
            elif user_response == 'exit':
                print("Exiting the program.")
                sys.exit()

        # If auto_process_remaining is True, automatically process the messages without user interaction
        elif sendtoGPT and self.auto_process_remaining:
            response_content, prompt_tokens_gpt, completion_tokens_gpt = generate_gpt_response(messages, model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
            user_response = 'yaauto'
        elif sendtoGPT and not self.interactive:
            response_content, prompt_tokens_gpt, completion_tokens_gpt = generate_gpt_response(messages, model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
            user_response = 'auto'
        else:
            print("Preview only.")
            return

        # Calculate a hash for the message
        message_hash = hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest()


        total_cost = calculate_cost_of_gpt_response(prompt_tokens_gpt, completion_tokens_gpt, self.model)
        # Process the response content
        if sendtoGPT and writetojson:
            write_gpt_response_to_jsonlfile(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, self.max_tokens, total_cost, self.temperature, self.model, input_feature_list, output_feature, question_map, user_response, messages, message_hash)
        if sendtoGPT and writetomongo:
            write_gpt_response_to_mongodb(response_content, prompt_tokens_tiktoken, prompt_tokens_gpt, completion_tokens_gpt, self.max_tokens, total_cost, self.temperature, self.model, input_feature_list, output_feature, question_map, user_response,  messages, message_hash)




if __name__ == "__main__":
 
   
    processor = FeatureQuestionProcessor( 
        model="gpt-4-0125-preview", 
        max_tokens=300, 
        temperature=0, 
        questions_map_filepath=initial_questions_map_filepath,  
        previewmessage=True, 
        sendtoGPT= True, 
        interactive = True,
        writetojson=True, 
        writetomongo = True,
        role = "personal trainer"
        )


    
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
    
    