import openai
import json
from OLD.api import Api
import requests
import json
import psycopg2
import openai
from postgres import PostgresDatabase
import concurrent.futures
import re

class ChatGPT:
    def __init__(self, apikey=Api().chat_gpt_api):
        self.api_key = apikey
        self.model_engine = "text-davinci-003"
       # self.model_engine = "text-curie-003"
        openai.api_key = self.api_key
    """
    def rate_video_title(self, title):
            #prompt = f'If you had to give a probability with no prior knowledge of whether the video with this video title "{title}" is a single exercise video demonstration appropriate for including in an exercise library, what probability would you give it? The response should be a number between 1 and 10, 10 being complete certainty'
            prompt = f'This is a video from a youtube channel related to fitness. Rate from 1 to 10, with 10 being certain: Is "{title}" a single exercise video demonstration appropriate for an exercise library?'
            openai.api_key = self.api_key

            completion = openai.Completion.create(
                engine = self.model_engine,
                prompt = prompt,
                max_tokens = 5,
                n = 1, 
                stop = None, 
                temperature = .1
            )

            if completion['choices']:
                result = completion['choices'][0]['text'].strip()
                return int(result) if result.isdigit() else 'AI is unsure'
            else:
                return 'Error occurred'"""
    
    def get_exercise_basics(self, video_title):
        user_message = f'Given the exercise video title {video_title}, provide a detailed description of how to do the exercises as a step by step process' 
        response = self._get_chatgpt_response(user_message)
        exercise_description = response.choices[0].text
        return exercise_description

    """
    def get_exercise_basics(self, video_title):
        user_message = f'Given the exercise video title {video_title}, provide a detailed description of how to do the exercises as a step by step process' 
      #  user_message = f'How do you perform the following exercise? Provide detailed instructions:  {video_title}'
        # Generate a response from ChatGPT
        response = openai.Completion.create(
            engine=self.model_engine,
            prompt=user_message,
            max_tokens=3000,
         #   n=1,
          #  stop=None,
          #  temperature=0.7,
        )

        # Retrieve the exercise details from the model's response
        exercise_description = response.choices[0].text
        return (exercise_description)"""

    def get_exercise_details(self, title, videoname = True):
        compensations = [
            "Rounded Shoulders",
            "Forward Head Posture",
            "Knee Valgus",
            "Knee Varus",
            "Pronation Distortion Syndrome",
            "Lower Crossed Syndrome",
            "Upper Crossed Syndrome",
            "Scapular Winging",
            "Anterior Pelvic Tilt",
            "Excessive Forward Lean",
            "Feet Turned Outward (Excessive External Rotation)",
            "Knees Moving Inward (Valgus Collapse)",
            "Feet Pronation (Flattening of Arches)",
            "Heels Rising Off the Ground",
            "Loss of Lumbar Curve (Excessive Flexion or Extension)",
            "Forward Head Posture",
            "Shoulder Elevation or Shrugging"
        ]

        format_code = (
            f'\n\n{{'
            #f'\n    "exercise_name": "The exact name of the exercise demonstrated",'
            f'\n    "exercise_name": "The exact name of the exercise demonstrated" if videoname else "Exact name of the exercise",'
            f'\n    "planes_of_motion": ["List of planes of motion involved"],'
            f'\n    "equipment": [{{'
            f'\n        "Name": "Name of the equipment",'
            f'\n        "Count": "Number of this equipment needed"'
            f'\n    }}],'
            f'\n    "proprioception": ["List of proprioceptive tools used"],'
            f'\n    "other_props": ["List of other props necessary to do the exercise"],'
            f'\n    "body_parts": {{'
            f'\n        "primary": "Specify one primary body part or muscle group primarily engaged",'
            f'\n        "secondary": ["List of other body parts or muscle groups engaged"]'
            f'\n    }},'
            f'\n    "exercise_type": "Specify whether the exercise is a \'push\' or \'pull\' exercise",'
            f'\n    "OPT_model_phases": ["List the phase or phases of the NASM OPT model that the exercise falls into"],'
            f'\n    "exercise_category": ["Categorize the exercise (it can fall into multiple categories): balance, core, resistance, flexibility, cardio, plyometric, SAQ, neuromotor"],'
            f'\n    "joint_usage": "Specify the type of joint usage: isolation, multijoint, or full body",'
            f'\n    "sides": "Specify the type of sides: unilateral, bilateral, or alternating",'
            f'\n    "sports_relevance": ["List any sports where this exercise is specifically relevant or beneficial (e.g. golf, tennis, basketball)"],'
            f'\n    "corrective_exercise": ["List any compensations or muscular imbalances that this exercise would help correct, including any of the following: {json.dumps(compensations)}"],'
            f'\n    "contraindications": ["List any health conditions or situations where the exercise is contraindicated"],'
            f'\n    "additional_tags": ["List any additional tags relevant to the exercise"],'
            f'\n    "regressions": ["Provide a list of between 1 and 5 recognized actual exercises that one would need to be capable of performing before attempting this exercise (also known as regressions)"],'
            f'\n    "progressions": ["Provide a list of between 1 and 5 recognized actual exercises that would be more difficult or advanced compared to this exercise (also known as progressions)"],'
            f'\n    "variations": ["Provide a list of between 1 and 5 recognized actual exercises that are neither regressions nor progressions, but variations of this exercise"],'
            f'\n    "description": "Provide a detailed description or set of instructions for performing the exercise. Don’t leave this blank"'
            f'\n}}'
        )

        if videoname:
            user_message = f'Given the video title "{title}", provide exercise details in the following format: {format_code}'
        else: 
            user_message = f'Given the exercise "{title}", provide exercise details in the following format: {format_code}'


        """
        user_message = f'Given the video title "{title}", provide exercise details in the following format:' \
                    f'\n\n{{' \
                    f'\n    "exercise_name": "The exact name of the exercise demonstrated",' \
                    f'\n    "planes_of_motion": ["List of planes of motion involved"],' \
                    f'\n    "equipment": [{{' \
                    f'\n        "Name": "Name of the equipment",' \
                    f'\n        "Count": "Number of this equipment needed"' \
                    f'\n    }}],' \
                    f'\n    "proprioception": ["List of proprioceptive tools used"],' \
                    f'\n    "other_props": ["List of other props necessary to do the exercise"],' \
                    f'\n    "body_parts": {{' \
                    f'\n        "primary": "Specify one primary body part or muscle group primarily engaged",' \
                    f'\n        "secondary": ["List of other body parts or muscle groups engaged"]' \
                    f'\n    }},' \
                    f'\n    "exercise_type": "Specify whether the exercise is a \'push\' or \'pull\' exercise",' \
                    f'\n    "OPT_model_phases": ["List the phase or phases of the NASM OPT model that the exercise falls into"],' \
                    f'\n    "exercise_category": ["Categorize the exercise (it can fall into multiple categories): balance, core, resistance, flexibility, cardio, plyometric, SAQ, neuromotor"],' \
                    f'\n    "joint_usage": "Specify the type of joint usage: isolation, multijoint, or full body",' \
                    f'\n    "sides": "Specify the type of sides: unilateral, bilateral, or alternating",' \
                    f'\n    "sports_relevance": ["List any sports where this exercise is specifically relevant or beneficial (e.g. golf, tennis, basketball)"],' \
                    f'\n    "corrective_exercise": ["List any compensations or muscular imbalances that this exercise would help correct, including any of the following: {json.dumps(compensations)}"],' \
                    f'\n    "contraindications": ["List any health conditions or situations where the exercise is contraindicated"],' \
                    f'\n    "additional_tags": ["List any additional tags relevant to the exercise"],' \
                    f'\n    "regressions": ["Provide a list of between 1 and 5 recognized actual exercises that one would need to be capable of performing before attempting this exercise (also known as regressions)"],' \
                    f'\n    "progressions": ["Provide a list of between 1 and 5 recognized actual exercises that would be more difficult or advanced compared to this exercise (also known as progressions)"],' \
                    f'\n    "variations": ["Provide a list of between 1 and 5 recognized actual exercises that are neither regressions nor progressions, but variations of this exercise"],' \
                    f'\n    "description": "Provide a detailed description or set of instructions for performing the exercise. Don’t leave this blank"' \
                    f'\n}}'"""

        response = self._get_chatgpt_response(user_message)
        exercise_details = response.choices[0].text.strip()
        exercise_json = json.loads(exercise_details)

        # Generate a response from ChatGPT
        """
        response = openai.Completion.create(
            engine=self.model_engine,
            prompt=user_message,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Retrieve the exercise details from the model's response
        exercise_details = response.choices[0].text.strip()

        # Convert the exercise details to a JSON object
        #todo try catch
        print("HELLO")
        print(exercise_details)
        exercise_json = json.loads(exercise_details)"""

        return exercise_json

    def _get_chatgpt_response(self, prompt):
        completion = openai.Completion.create(
            engine=self.model_engine,
            prompt=prompt,
            max_tokens=3000
        )
        return completion

    def process_exercise(self, title):
        exercise_json = self.get_exercise_details(title)
        print(json.dumps(exercise_json, indent=4))

    def process_exercise_titles(self, exercise_titles):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_exercise, title) for title in exercise_titles]
            concurrent.futures.wait(futures)





# Test the ChatGPT class
"""
chat_gpt = ChatGPT()
video_title = "weighted pushup"
exercise_json = chat_gpt.get_exercise_details(video_title)
print(json.dumps(exercise_json, indent=4))


video_titles = ['weighted pushup', 'air squat']

# Use ThreadPoolExecutor to run the function in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
   # futures = {executor.submit(chat_gpt.rate_video_title, title): title for title in video_titles}
    futures = {executor.submit(chat_gpt.rate_video_title, title): title for title in video_titles}
    for future in concurrent.futures.as_completed(futures):
        title = futures[future]
        try:
            rating = future.result()
            print(f'Video: {title}, Rating: {rating}')
        except Exception as exc:
            print(f'Video: {title}, generated an exception: {exc}')

"""