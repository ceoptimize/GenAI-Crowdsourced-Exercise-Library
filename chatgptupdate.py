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



def sanitize_list(a_list):
    sanitized_elements = [stringfunctions.sanitize_string(name) for name in a_list]
    return sanitized_elements

class ChatGPT:
    def __init__(self, apikey=Api().chat_gpt_api):
        self.api_key = apikey
        self.model_engine = "text-davinci-003"
       # self.model_engine = "text-curie-003"
        openai.api_key = self.api_key
    

    
    def get_exercise_basics(self, video_title):
        user_message = f'Given the exercise video title {video_title}, provide a detailed description of how to do the exercises as a step by step process' 
        response = self._get_chatgpt_response(user_message)
        exercise_description = response.choices[0].text
        return exercise_description


    def get_exercise_details(self, title, videoname = True, max_retries=3):
        valid_compensations = sanitize_list([
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
        ])
        print(valid_compensations)

        valid_bodyareas = sanitize_list([
            "Upper back",
            "Lower back",
            "Chest",
            "Quadriceps",
            "Hamstrings",
            "Glutes",
            "Biceps",
            "Triceps",
            "Core",
            "Shoulders",
            "Forearms"
        ])

        valid_equipment = sanitize_list([
            "Treadmill",
            "Stationary Bike",
            "Elliptical Machine",
            "Rowing Machine",
            "Dumbbell",
            "Barbell",
            "Kettlebell",
            "Resistance Band",
            "Medicine Ball",
            "Weight Bench",
            "Smith Machine",
            "Leg Press Machine",
            "Lat Pulldown Machine",
            "Cable Machine",
            "Stability Ball",
            "Jump Rope",
            "Yoga Mat",
            "TRX Suspension Trainer",
            "Battle Rope",
            "Plyometric Box",
            "Bench Press",
            "Pull-Up Bar",
            "Kettlebell",
            "Exercise Bike",
            "Power Rack",
            "Climbing Rope",
            "Foam Roller",
            "Ab Wheel",
            "Hula Hoop",
            "Squat Rack",
            "Punching Bag",
            "Speed Bag",
            "Heavy Bag",
            "Exercise Mat",
            "Resistance Band",
            "Rowing Machine",
            "Stair Stepper",
            "Exercise Ball",
            "Gymnastic Ring",
            "Trap Bar",
            "Battle Ropes",
            "Swiss Ball",
            "Medicine Ball",
            "Weight Plate",
            "Push-Up Bar",
            "Dip Station",
            "Roman Chair",
            "Cable Crossover Machine",
            "Smith Machine",
            "Hack Squat Machine",
            "Glute Ham Raise Machine",
            "Calf Raise Machine",
            "Seated Leg Curl Machine",
            "Leg Extension Machine",
            "Chest Fly Machine",
            "Lat Pulldown Machine",
            "Cable Row Machine",
            "Cable Pulldown Machine",
            "Treadmill",
            "Exercise Bike",
            "Cross Trainer",
            "No Equipment"
        ])

        format_code = (
            f'\n\n{{'
            #f'\n    "exercise_name": "The exact name of the exercise demonstrated",'
            f'\n    "exercise_name_primary": "The exercise name (same as the video title)" if videoname else "name of the exercise",'
            f'\n    "exercise_aliases": ["List of other well known aliases for this exercise, if there are any, outside of the primary name"],'
            f'\n    "difficulty": "On a scale of 1 (beginner) to 10 (expert) level, how difficult is this exercise to perform",'
            f'\n    "planes_of_motion": ["List of planes of motion involved"],'
            f'\n    "equipment": [{{'
            f'\n        "Name": "Name of the equipment, which must be constrained to the following: {json.dumps(valid_equipment)}",'
            f'\n        "Count": "Number of this equipment needed"'
            f'\n    }}],'
            f'\n    "proprioception": ["List of proprioceptive tools used"],'
            f'\n    "other_props": ["List of other props necessary to do the exercise"],'
            f'\n    "body_parts": {{'
            f'\n        "primary": "This field must be populated. Specify one primary body part or muscle group primarily engaged, which must be constrained to the following: {json.dumps(valid_bodyareas)}",'
            f'\n        "secondary": ["List of other body parts or muscle groups engaged, which must be constrained to the following: {json.dumps(valid_bodyareas)}"]'
            f'\n    }},'
            f'\n    "exercise_type": "Specify whether the exercise is a \'push\' or \'pull\' exercise",'
            f'\n    "OPT_model_phases": ["List the phase or phases of the NASM OPT model that the exercise falls into"],'
            f'\n    "exercise_category": ["Categorize the exercise (it can fall into multiple categories): balance, core, resistance, flexibility, cardio, plyometric, SAQ, neuromotor"],'
            f'\n    "joint_usage": "Specify the type of joint usage: isolation, multijoint, or full body",'
            f'\n    "sides": "Specify the type of sides: unilateral, bilateral, or alternating",'
            f'\n    "sports_relevance": ["List any sports where this exercise is specifically relevant or beneficial (e.g. golf, tennis, basketball)"],'
            f'\n    "corrective_exercise": ["List any valid_compensations or muscular imbalances that this exercise would help correct, including any of the following: {json.dumps(valid_compensations)}"],'
            f'\n    "contraindications": ["List any health conditions or situations where the exercise is contraindicated"],'
            f'\n    "additional_tags": ["List any additional tags relevant to the exercise"],'
            f'\n    "regressions": ["Provide a list of between 1 and 5 recognized actual exercises that one would need to be capable of performing before attempting this exercise (also known as regressions)"],'
            f'\n    "progressions": ["Provide a list of between 1 and 5 recognized actual exercises that would be more difficult or advanced compared to this exercise (also known as progressions)"],'
            f'\n    "variations": ["Provide a list of between 1 and 5 recognized actual exercises that are neither regressions nor progressions, but variations of this exercise"],'
            f'\n    "description": "Provide a detailed description or set of instructions for performing the exercise. Speak in terms of a single instance or repetition of the exercise. Don’t leave this field blank"'
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
                    f'\n    "corrective_exercise": ["List any valid_compensations or muscular imbalances that this exercise would help correct, including any of the following: {json.dumps(valid_compensations)}"],' \
                    f'\n    "contraindications": ["List any health conditions or situations where the exercise is contraindicated"],' \
                    f'\n    "additional_tags": ["List any additional tags relevant to the exercise"],' \
                    f'\n    "regressions": ["Provide a list of between 1 and 5 recognized actual exercises that one would need to be capable of performing before attempting this exercise (also known as regressions)"],' \
                    f'\n    "progressions": ["Provide a list of between 1 and 5 recognized actual exercises that would be more difficult or advanced compared to this exercise (also known as progressions)"],' \
                    f'\n    "variations": ["Provide a list of between 1 and 5 recognized actual exercises that are neither regressions nor progressions, but variations of this exercise"],' \
                    f'\n    "description": "Provide a detailed description or set of instructions for performing the exercise. Don’t leave this blank"' \
                    f'\n}}'"""
        print(user_message)
       

        for _ in range(max_retries):
            response = self._get_chatgpt_response(user_message)
            exercise_details = response.choices[0].text.strip()
            print("this is the raw output")
            print(exercise_details)

            if not exercise_details:
                print("empty details")
                raise Exception("Received an empty response from ChatGPT. Resubmitting request.")

            exercise_json = json.loads(exercise_details)
            print("here's the json")
            print(exercise_json)
            

            # Validate primary and secondary body parts
            primary_body_part = stringfunctions.sanitize_string(exercise_json["body_parts"]["primary"])
            print(primary_body_part)
            secondary_body_parts = sanitize_list(exercise_json["body_parts"]["secondary"])
            print(secondary_body_parts)
            print(1)
            # Validate valid_compensations
            print(exercise_json["corrective_exercise"])
            exercise_compensations = sanitize_list(exercise_json["corrective_exercise"])
            print(exercise_compensations)

           # Validate exercise equipment
            exercise_equipment_items = exercise_json["equipment"]
            print(exercise_equipment_items)
            print(2)
            for equipment_item in exercise_equipment_items:
                equipment_name = stringfunctions.sanitize_string(equipment_item.get("Name", ""))
                equipment_count = stringfunctions.sanitize_string(equipment_item.get("Count", ""))

                # Check if equipment_name is valid
                if equipment_name not in valid_equipment:
                    equipment_prompt = f'Given the video title "{title}", provide a valid equipment name from: {json.dumps(valid_equipment)}'
                    equipment_response = self._get_chatgpt_response(equipment_prompt)
                    equipment_item["Name"] = equipment_response.choices[0].text.strip()

                # Check if equipment_count is a number
                if not equipment_count.isdigit():
                    count_prompt = f'Given the video title "{title}", provide a valid equipment count as a number'
                    count_response = self._get_chatgpt_response(count_prompt)
                    equipment_item["Count"] = count_response.choices[0].text.strip()

            print(3)
            # Check if primary body part is valid
            if primary_body_part not in valid_bodyareas:
                primary_prompt = f'Given the video title "{title}", provide a valid primary body part from: {json.dumps(valid_bodyareas)}'
                primary_response = self._get_chatgpt_response(primary_prompt)
                exercise_json["body_parts"]["primary"] = stringfunctions.sanitize_string(primary_response.choices[0].text.strip())

            # Check if secondary body parts are valid
            invalid_secondary_parts = [part for part in secondary_body_parts if part not in valid_bodyareas]
            for invalid_part in invalid_secondary_parts:
                secondary_prompt = f'Given the video title "{title}", provide a valid secondary body part from: {json.dumps(valid_bodyareas)}'
                secondary_response = self._get_chatgpt_response(secondary_prompt)
                updated_secondary = secondary_response.choices[0].text.strip()
                secondary_body_parts.remove(invalid_part)
                secondary_body_parts.append(updated_secondary)
                exercise_json["body_parts"]["secondary"] = sanitize_list(secondary_body_parts)
            print(4)
            # Check if valid_compensations are valid
            invalid_compensations = [compensation for compensation in exercise_compensations if compensation not in valid_compensations]
            for invalid_compensation in invalid_compensations:
                compensation_prompt = f'Given the video title "{title}", provide a valid compensation from: {json.dumps(valid_compensations)}'
                compensation_response = self._get_chatgpt_response(compensation_prompt)
                updated_compensation = compensation_response.choices[0].text.strip()
                exercise_compensations.remove(invalid_compensation)
                exercise_compensations.append(updated_compensation)
                exercise_json["corrective_exercise"] = sanitize_list(exercise_compensations)

            # Re-validate the entire JSON after updates
            primary_body_part = exercise_json["body_parts"]["primary"]
            print("primary body part")
            print(primary_body_part)
            secondary_body_parts = exercise_json["body_parts"]["secondary"]
            exercise_compensations = exercise_json["corrective_exercise"]

            if (
                primary_body_part not in valid_bodyareas
                or any(part not in valid_bodyareas for part in secondary_body_parts)
                or any(compensation not in valid_compensations for compensation in exercise_compensations)
            ):
                raise ValueError("Invalid elements detected. Resubmitting request.")
                print("invalide parts")

            print("this is the final json")
            print("exercise_json")
            return exercise_json

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


