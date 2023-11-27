import openai
import json
from api import Api
import requests
import json
import psycopg2
import openai
from postgres import PostgresDatabase
import concurrent.futures
import re
import stringfunctions

standard_exercise_names = {
    "push up": ["push-up", "pushup"],
    # Add more standard names and their variations here
}

def standardize_exercise_name(name, standard_names):
    words = name.split()  # Split the name into words
    new_words = []
    for word in words:
        for standard, synonyms in standard_names.items():
            # Check if the word is in the synonyms list
            if word in synonyms:
                word = standard  # Replace it with the standard term
                break  # Break the loop once a replacement is done
        new_words.append(word)  # Add the word to the new words list
    return ' '.join(new_words)  # Reconstruct the name

'''
def standardize_exercise_name(name, standard_names):
    for standard, synonyms in standard_names.items():
        if name in synonyms:
            return standard
    return name
'''
    
def replace_chars(text, char_to_replace, replacement_char):
    return text.replace(char_to_replace, replacement_char)

def to_singular(word):
        # Check for 'es' or 's' at the end of the word, but not 'ss' (like in 'press')
        if word.endswith('es') and not word.endswith('ss') and not word.endswith('ees'):
            return word[:-2]
        elif word.endswith('s') and not word[-2:] == 'ss':
            return word[:-1]
        return word

def sanitize_list(a_list):
    sanitized_elements = [stringfunctions.sanitize_string(name) for name in a_list]
    return sanitized_elements

class ChatGPT:
    def __init__(self, apikey=Api().chat_gpt_api):
        self.api_key = apikey
        self.model_engine = "text-davinci-003"
       # self.model_engine = "text-curie-003"
        openai.api_key = self.api_key
           # Read the JSON data into a dictionary
        with open('valid_data.json', 'r') as json_file:
            valid_data = json.load(json_file)

        self.valid_equipment = sanitize_list(valid_data['equipment'])
        self.valid_bodyareas = sanitize_list(valid_data['bodyareas'])
        self.valid_compensations = sanitize_list(valid_data['compensations'])
    

    def is_likely_exercise_video(self, video_id, video_title, channel_title, transcript, duration):
        # Construct the prompt for querying ChatGPT
        prompt = (
            f"Video ID: {video_id}\n"
            f"Title: {video_title}\n"
            f"Channel: {channel_title}\n"
            f"Transcript: {transcript}\n"
            f"Duration: {duration}\n\n"
            "Based on the information provided, could this video stand alone as one exercise in an exercise library that a fitness professional uses for programming for clients? (Be sure not to include videos focused on a personal experience, transformation, competition, or advertising a piece of equipment.) Answer with '1' for a Confident Yes and '0' for Unsure or Maybe, and '-1' for a Confident No."
           # "Based on the information provided, is this video likely to be a professional exercise demonstration of ONE exercise only with instructions focused on how to properly perform the technique of the exercise, and not focused on a personal experience, transformation, competition, or piece of equipment? Or to put it differently - could this be one exercise in an exercise library? Answer with '1' for a Confident Yes and '0' for Unsure or Maybe, and '-1' for a Confident No."
        )

        # Get the response from ChatGPT
        response = self._get_chatgpt_response(prompt)

        # Process the response to determine if it's likely an exercise video
        try:
            # Assuming the response is structured with a choice and text
            choice_text = response.choices[0].text.strip()

            # Parse the response as a binary outcome
            is_exercise_video = 1 if choice_text == '1' else 0

            return is_exercise_video
        except Exception as e:
            # Handle exceptions such as an empty response, API errors, etc.
            print(f"An error occurred while determining if the video is an exercise video: {str(e)}")
            return 0  # Default to 0 if there's an error or ambiguous response
    
    def formulate_chat_gpt_exercise_query(self, gptquerydata):
        

        format_code = (
            f'\n\n{{'
            f'\n    "exercise_name_primary": "The name of the exercise demonstrated",'
            f'\n    "exercise_aliases": ["List of other known aliases for this exercise, if there are any, outside of the primary name"],'
            f'\n    "difficulty": "On a scale of 1 (beginner) to 10 (expert) level, how difficult is this exercise to perform",'
            f'\n    "planes_of_motion": ["List of planes of motion involved"],'
            f'\n    "equipment": [{{'
            f'\n        "Name": "Name of the equipment, which must be constrained to the following: {self.valid_equipment}",'
            f'\n        "Count": "Minimum number of this equipment needed (THIS FIELD SHOULD BE AN INTEGER)"'
            f'\n    }}],'
            f'\n    "proprioception": ["List of proprioceptive tools used"],'
            f'\n    "other_props": ["List of other props necessary to do the exercise"],'
            f'\n    "body_parts": {{'
            f'\n        "primary": "This field must be populated. Specify one primary body part or muscle group primarily engaged, which must be constrained to the following: {self.valid_bodyareas}",'
            f'\n        "secondary": ["List of other body parts or muscle groups engaged, which must be constrained to the following: {self.valid_bodyareas}"]'
            f'\n    }},'
            f'\n    "exercise_type": "Specify whether the exercise is a \'push\' or \'pull\' exercise",'
            f'\n    "OPT_model_phases": ["List the phase or phases of the NASM OPT model that the exercise falls into"],'
            f'\n    "exercise_category": ["Categorize the exercise (it can fall into multiple categories): balance, core, resistance, flexibility, cardio, plyometric, SAQ, neuromotor"],'
            f'\n    "joint_usage": "Specify the type of joint usage: isolation, multijoint, or full body",'
            f'\n    "sides": "Specify the type of sides: unilateral, bilateral, or alternating",'
            f'\n    "sports_relevance": ["List any sports where this exercise is specifically relevant or beneficial (e.g. golf, tennis, basketball)"],'
            f'\n    "corrective_exercise": ["List any valid_compensations or muscular imbalances that this exercise would help correct, including any of the following: {self.valid_compensations}"],'
            f'\n    "contraindications": ["List any health conditions or situations where the exercise is contraindicated"],'
            f'\n    "additional_tags": ["List any additional tags relevant to the exercise"],'
            f'\n    "regressions": ["Provide a list of between 1 and 5 recognized actual exercises that one would need to be capable of performing before attempting this exercise (also known as regressions)"],'
            f'\n    "progressions": ["Provide a list of between 1 and 5 recognized actual exercises that would be more difficult or advanced compared to this exercise (also known as progressions)"],'
            f'\n    "variations": ["Provide a list of between 1 and 5 recognized actual exercises that are neither regressions nor progressions, but variations of this exercise"],'
            f'\n    "description": "Provide a detailed description or set of instructions for performing the exercise. Speak in terms of a single instance or repetition of the exercise. Do not mention a certain number of rep range or count even if the transcript does. Absolutely do not copy or paraphrase closely the transcript. Use your knowledge of how to do the exercise as well. Don’t leave this field blank"'
            f'\n}}'
        )

      
        user_message = f'Given the youtube video information "{gptquerydata}", provide exercise details in the following format: {format_code} and please only use singular (not plural) in listing all items like exercise names, aliases, regressions, progressions and variations, equipment names, bodyparts, etc because they need to represent unique items in a database'

        return(user_message)
 

    '''
    def validate_and_correct_types(self, data: dict, expected_types: dict) -> dict:
        """
        Validates the types of the data fields and corrects them if necessary.

        :param data: The JSON data to validate.
        :param expected_types: A dictionary mapping the data fields to their expected types.
        :return: The validated and corrected data.
        """
        for key, expected_type in expected_types.items():
            if key in data:
                if not isinstance(data[key], expected_type):
                    print(f"The field '{key}' has an incorrect type. Expected {expected_type}, got {type(data[key])}.")
                    # Construct a query for the specific field
                    user_message = f"What should be the {expected_type.__name__} value for the field '{key}'?"
                    # Get the response from ChatGPT
                    response = self._get_chatgpt_response(user_message)
                    # Parse and integrate the corrected value
                    corrected_value = response.choices[0].text.strip()
                    try:
                        # Convert the corrected value to the expected type
                        corrected_value = expected_type(corrected_value)
                        data[key] = corrected_value
                    except ValueError:
                        print(f"Failed to convert the value for '{key}' to {expected_type.__name__}.")
                        # Handle the conversion error (e.g., log, raise exception, etc.)
                # If the type is correct, no action is needed
            else:
                print(f"The field '{key}' is missing.")
                # Handle the missing key (e.g., log, raise exception, etc.)
        return data
    '''
    
    '''
    def singularize_exercises(self, exercise_json):
        keys_to_singularize = ['exercise_name_primary', 'exercise_aliases', 'regressions', 'progressions', 'variations']
        
        for key in keys_to_singularize:
            if key in exercise_json:
                if isinstance(exercise_json[key], list):
                    exercise_json[key] = [to_singular(item) for item in exercise_json[key]]
                elif isinstance(exercise_json[key], str):
                    exercise_json[key] = to_singular(exercise_json[key])
        
        return exercise_json
    '''

    def clean_exercises(self, exercise_json):
        keys_to_clean = ['exercise_name_primary', 'exercise_aliases', 'regressions', 'progressions', 'variations']
        
        for key in keys_to_clean:
            if key in exercise_json:
                if isinstance(exercise_json[key], list):
                    exercise_json[key] = [
                        standardize_exercise_name(replace_chars(to_singular(item), '-', ' '), standard_exercise_names)
                        for item in exercise_json[key]
                    ]
                elif isinstance(exercise_json[key], str):
                    exercise_json[key] = standardize_exercise_name(replace_chars(to_singular(exercise_json[key]), '-', ' '), standard_exercise_names)
        
        return exercise_json
    
    def get_exercise_details(self, gptquerydata, user_message, max_retries=3):
        for _ in range(max_retries):
            response = self._get_chatgpt_response(user_message)
            if response.choices:
                exercise_details = response.choices[0].text.strip()
                print("ChatGPT response:")
                print(exercise_details)
                
                # Try to parse the response into JSON
                try:
                    exercise_json = json.loads(exercise_details)
                    print("Parsed JSON:")
                    print(exercise_json)
                    '''
                    expected_types = {
                        "exercise_name_primary": str,
                        "exercise_aliases": list,
                        "difficulty": int,
                        "planes_of_motion": list,
                        # Add other fields and their expected types here
                    }
                    
                    # Validate and correct types
                    exercise_json = self.validate_and_correct_types(exercise_json, expected_types)
                    '''
                    exercise_json = self.clean_exercises(exercise_json)
                    return exercise_json    
                
                except json.JSONDecodeError:
                    print("Failed to parse JSON. Response may not be in JSON format.")
            else:
                print("Received an empty or invalid response from ChatGPT. Resubmitting request.")
        
        # If max_retries reached without obtaining valid JSON, raise an exception.
        raise Exception("Unable to obtain valid exercise details after multiple retries")

    def _get_chatgpt_response(self, prompt):
    
        try:
            completion = openai.Completion.create(
                engine=self.model_engine,
                prompt=prompt,
                max_tokens=2000
            )
            
            # Print the length of choices
            print(f"Length of choices: {len(completion.choices)}")
            
            if not completion.choices or len(completion.choices) == 0:
                print("EMPTY RESPONSE")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            completion = None
        
        return completion

    def process_exercise(self, title):
        exercise_json = self.get_exercise_details(title)
        print(json.dumps(exercise_json, indent=4))

    def process_exercise_titles(self, exercise_titles):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_exercise, title) for title in exercise_titles]
            concurrent.futures.wait(futures)


