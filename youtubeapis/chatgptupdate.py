import openai
import json
import requests
import json
import psycopg2
import openai
import concurrent.futures
import re
import stringfunctions as stringfunctions
import log
import json
from openai_communication import OpenAICommunication, TikTokenCommunication
import os

# Load the configuration
CONFIG_PATH = 'config/config.json'
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

standard_exercise_names = {
    "push up": ["push-up", "pushup"],
    "one arm": ["onearm"]
    # Add more standard names and their variations here
}


def standardize_exercise_name(name, standard_names):
    # Replace hyphens with spaces to handle cases like "push-up"
    name = name.replace('-', ' ')
    words = name.split()  # Split the name into words

    new_words = []
    for word in words:
        # Apply to_singular to each word to ensure they are not plural
        singular_word = stringfunctions.to_singular(word)
        for standard, synonyms in standard_names.items():
            # Check if the singular word is in the synonyms list
            if singular_word.lower() in synonyms:
                singular_word = standard  # Replace it with the standard term
                break
        new_words.append(singular_word)  # Add the word to the new words list

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


def sanitize_list(a_list):
    sanitized_elements = [
        stringfunctions.sanitize_string(name) for name in a_list]
    return sanitized_elements


class ChatGPT:


    def __init__(self, openai_comm = OpenAICommunication(api_key=os.environ.get("OPENAI_API_KEY", config['openai']['api_key']))):
        self.openai_comm = openai_comm
        self.api_key = openai_comm.api_key
        self.model_engine = "gpt-3.5-turbo-1106"

        # Read the JSON data into a dictionary
        with open('resources/jsondata/valid_data.json', 'r') as json_file:
            valid_data = json.load(json_file)

        self.valid_equipment = sanitize_list(valid_data['equipment'])
        self.valid_bodyareas = sanitize_list(valid_data['bodyareas'])
        self.valid_compensations = sanitize_list(valid_data['compensations'])
        self.valid_adjustments = sanitize_list(valid_data['adjustmentareas'])

    def get_related_exercise_adjustments(self, primary_exercise_name, primary_exercise_desc, related_exercise_name, related_exercise_desc, relationship_type):
        # Construct the query
        '''
        prompt = (
            f"Primary Exercise: {primary_exercise_name}\n"
            f"Primary Exercise description: {primary_exercise_desc}\n\n"
            f"Related Exercise: {related_exercise_name}\n"
            f"Related Exercise description: {related_exercise_desc}\n\n"
            "You are PersonalTrainerGPT. Exercises can be progressed or regressed in the following adjustment areas: " + ', '.join(self.valid_adjustments) + ".\n\n"
            "Return a response in JSON format. Indicate if the related exercise is a regression or progression to the primary exercise in any of the adjustment areas. You do NOT have to use all of the adjustment areas - only the ones that apply."
            "The JSON format should look like this:\n"
            "{\n"
            "   \"related_exercise_id\": \"<id>\",\n"
            "   \"regression\": [list of adjustment areas],\n"
            "   \"progression\": [list of adjustment areas]\n"   
            "}"
        )
        '''

        prompt = (
            f"Primary Exercise: {primary_exercise_name}\n"
            f"Primary Exercise description: {primary_exercise_desc}\n\n"
            f"Related Exercise: {related_exercise_name}\n"
            f"Related Exercise description: {related_exercise_desc}\n\n"
            "You are PersonalTrainerGPT. Analyze the following adjustment areas for the exercises: " +
            ', '.join(self.valid_adjustments) + ".\n\n"
            "Based on what you already know about these exercises, and if it helps, the descriptions provided, return a response in JSON format. Indicate if the related exercise is a regression or progression to the primary exercise in any of the adjustment areas. If it is neither, then leave it out of both categories! I would rather have you omit an adjustment area then give false information."
            "Format the response as follows, ensuring to use double quotes for all keys and string values:\n"
            "{\n"
            "   \"related_exercise_id\": \"<related exercise ID>\",\n"
            "   \"regression\": [\"<adjustment area 1>\", \"<adjustment area 2>\", ...],\n"
            "   \"progression\": [\"<adjustment area 3>\", \"<adjustment area 4>\", ...]\n"
            "}\n"
            "Note: Do not include an adjustment area if it does not apply. Only use the areas that are relevant for the related exercise."
        )

        # Get the response from ChatGPT
        response = self._get_chatgpt_response(prompt)

        # Process and return the response
        if response.choices:
            adjustment_details_raw = response.choices[0].text.strip()

            # Clean the response and extract JSON
            cleaned_details = stringfunctions.clean_json_response(
                adjustment_details_raw)
            if cleaned_details is None:
                log.log_error(
                    "No valid JSON found in the response after attempting to clean json")
                return "Unable to determine adjustment details"
            else:
                log.log_details(cleaned_details)
            try:
                # Parse the cleaned response as JSON
                adjustment_json = json.loads(cleaned_details)

                return adjustment_json
            except json.JSONDecodeError as je:
                log.log_error(f"JSON parsing error: {je}")
                return "Unable to determine adjustment details"
        else:
            # Handle cases where the response is empty or invalid
            log.log_error(
                f"Adjustment details response is empty or invalid {je}")
            return "Unable to determine adjustment details"

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
            print(
                f"An error occurred while determining if the video is an exercise video: {str(e)}")
            return 0  # Default to 0 if there's an error or ambiguous response

    def formulate_chat_gpt_exercise_query(self, gptquerydata):

        format_code = (
            f'\n\n{{'
            f'\n    "exercise_name_primary": "The name of the exercise demonstrated",'
            f'\n    "exercise_aliases": ["List of other known names or aliases for this exercise, if there are any, outside of the primary name. This is NOT a variation of the exercise, but another name for the same exercise."],'
            f'\n    "difficulty": "On a scale of 1 (beginner) to 10 (expert) level, how difficult is this exercise to perform",'
            f'\n    "planes_of_motion": ["List of planes of motion involved"],'
            f'\n    "equipment": [{{'
            f'\n        "Name": "Name of the equipment, which must be constrained to the following: {self.valid_equipment}",'
            f'\n        "Count": "Minimum number of this equipment needed (THIS FIELD SHOULD BE AN INTEGER)"'
            f'\n    }}],'
            f'\n    "other_props": ["List of any other props or equipment necessary to do the exercise"],'
            f'\n    "body_parts": {{'
            f'\n        "primary": "This field must be populated. Specify one primary body part or muscle group primarily engaged, which must be constrained to the following: {self.valid_bodyareas}",'
            f'\n        "secondary": ["List of other body parts or muscle groups engaged, which must be constrained to the following: {self.valid_bodyareas}"]'
            f'\n    }},'
            f'\n    "exercise_mechanics": "Specify whether the exercise is a \'push\' or \'pull\' exercise",'
            f'\n    "OPT_model_phases": ["List the phase or phases of the NASM OPT model that the exercise falls into"],'
            f'\n    "exercise_category": ["Categorize the exercise (it can fall into multiple categories): balance, core, resistance, flexibility, cardio, plyometric, SAQ, neuromotor"],'
            f'\n    "joint_usage": "Specify the type of joint usage: isolation, multijoint, or full body",'
            f'\n    "sides": "Specify the type of sides: unilateral, bilateral, or alternating",'
            f'\n    "sports_relevance": ["List any sports where this exercise is specifically relevant or beneficial (e.g. golf, tennis, basketball)"],'
            f'\n    "corrective_exercise": ["List any valid compensations or muscular imbalances that this exercise would help correct, including any of the following: {self.valid_compensations}"],'
            f'\n    "contraindications": ["List any health conditions or situations where the exercise is contraindicated"],'
            f'\n    "additional_tags": ["List any additional tags relevant to the exercise"],'
            f'\n    "regressions": ["Provide a list of between 1 and 5 well-known and real exercises that one would need to be capable of performing before attempting this exercise (also known as regressions)"],'
            f'\n    "progressions": ["Provide a list of between 1 and 5 well-known and real exercises that would be more difficult or advanced compared to this exercise (also known as progressions)"],'
            f'\n    "variations": ["Provide a list of between 1 and 5 well-known and real exercises that are neither regressions nor progressions, but variations of this exercise"],'
            f'\n    "description": "Provide a detailed description or set of instructions for performing the exercise. Speak in terms of the mechanics of one single instance or repetition of the exercise. Do not mention performing a certain number of repetitions, rep range or count even if the transcript does. Absolutely do not copy or paraphrase closely the transcript. Use your knowledge of how to do the exercise as well. Don’t leave this field blank"'
            f'\n}}'
        )

        user_message = f'Act as PersonalTrainerGPT. Given the youtube video information "{gptquerydata}", provide exercise details in the following format: {format_code} and please only use singular (not plural) in listing all items. We need to build a database of unique items, so each item represents a single data element that can be used to inform workouts.'

        return (user_message)

    def clean_exercises(self, exercise_json):
        keys_to_clean = ['exercise_name_primary', 'exercise_aliases',
                         'regressions', 'progressions', 'variations']

        for key in keys_to_clean:
            if key in exercise_json:
                if isinstance(exercise_json[key], list):
                    exercise_json[key] = [
                        standardize_exercise_name(item, standard_exercise_names) for item in exercise_json[key]
                    ]
                elif isinstance(exercise_json[key], str):
                    exercise_json[key] = standardize_exercise_name(
                        exercise_json[key], standard_exercise_names)

        return exercise_json

    def get_exercise_details(self, user_message, max_retries=2):
        for _ in range(max_retries):
            response = self._get_chatgpt_response(user_message)
            if response.choices:
                exercise_details = response.choices[0].text.strip()
                print("ChatGPT response:")
                log.log_details(user_message)
                cleaned_details = stringfunctions.clean_json_response(
                    exercise_details)
                if cleaned_details is None:
                    log.log_details(
                        "No valid JSON found in the response after attempting to clean json")
                    continue
                log.log_details(cleaned_details)
                log.log_details(
                    f"Type of exercise_details: {type(cleaned_details)}, Length: {len(cleaned_details)}")

                try:
                    exercise_json = json.loads(cleaned_details)
                    log.log_details("Successful json load")

                except json.JSONDecodeError as je:
                    log.log_details(f"JSON parsing error: {je}")
                    continue  # Skip the rest of the loop and try again

                try:
                    # Assuming clean_exercises modifies the JSON and returns a new version
                    exercise_json = self.clean_exercises(exercise_json)
                    log.log_details("Successful json clean")
                    return exercise_json
                except Exception as e:
                    # Log the specific error from clean_exercises
                    log.log_details(
                        f"Error in clean_exercises method: {str(e)}")
            else:
                print(
                    "Received an empty or invalid response from ChatGPT. Resubmitting request.")

        # Log that all retries have been exhausted without success
        log.log_details("All retries exhausted without a successful response.")
        return None  # or some default value or action

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
            futures = [executor.submit(self.process_exercise, title)
                       for title in exercise_titles]
            concurrent.futures.wait(futures)
