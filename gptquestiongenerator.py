import json
import random
import os
from datetime import datetime  # Correctly import the datetime class
from chatgptupdate import ChatGPT
import log
from openai import OpenAI
import api
from typing import Tuple, Optional, Dict, Any





# Define the data
json_file_path = "jsondata/validdata.json"



with open(json_file_path, 'r') as file:
    data = json.load(file)


def write_questions_to_file(questions, category_name, base_directory='questionsandanswers', overwriteanswersfile = False):
    # Generate a timestamp string for the subfolder name
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Define the directory path for this specific category
    category_directory_path = os.path.join(base_directory, f'{category_name}')
    
    # Define the subfolder path within the category directory
    subfolder_path = os.path.join(category_directory_path, timestamp_str)
    
    # Ensure the subfolder exists
    os.makedirs(subfolder_path, exist_ok=True)
    
    # Define the full path for the questions file within the subfolder
    questions_file_path = os.path.join(subfolder_path, f'questions_{category_name}.txt')
    
    # Write questions to the file
    with open(questions_file_path, 'w') as file:
        for question in questions:
            file.write(question + '\n')
    
    # Define the full path for the answers file within the subfolder
    answers_file_path = os.path.join(subfolder_path, f'answers_{category_name}.json')
    
    # Create an empty answers file if it does not exist
    if overwriteanswersfile or not os.path.exists(answers_file_path):
        open(answers_file_path, 'a').close()




def handle_element_pairing(data, element_pair):
    # Default connector
    default_connector = " "

    if isinstance(element_pair, tuple):
        if len(element_pair) == 2:
            first_element, second_element = element_pair
            connector = default_connector
        elif len(element_pair) == 3:
            first_element, second_element, connector = element_pair
        else:
            raise ValueError("element_pair must be a tuple of 2 or 3 elements")

        # Trim elements and connector
        first_element = first_element.rstrip('s').strip()
        second_element = second_element.strip()
        connector = connector.strip()

        # Ensure spaces are added around the connector
        combined_category = f"{first_element} {connector} {second_element}"
        combined_elements_key = f"{first_element}{connector}{second_element}"
        combined_elements = combine_elements(data, (first_element, second_element, connector))
    else:
        combined_category = element_pair.rstrip('s').strip()
        combined_elements_key = element_pair.strip()
        combined_elements = data.get(element_pair, [])

    return combined_category, combined_elements, combined_elements_key




def combine_elements(data, elements_tuple):
    if len(elements_tuple) != 3:
        raise ValueError("elements_tuple must be a tuple of 3 elements (first category, second category, connector)")

    first_category, second_category, connector = elements_tuple
    combined_elements = []

    for first_element in data[first_category]:
        for second_element in data[second_category]:
            # Combine with proper spacing around the connector
            combined_elements.append(f"{first_element.strip()} {connector} {second_element.strip()}")

    return combined_elements



# Assuming the GPT model engine name is a constant for all questions
GPT_MODEL_ENGINE = "gpt-4"



'''
def generate_question(data, element_pair, json_format=None, include_choices=False, insertrelationship='', outputrange=None):
    # Unpack the element pair details
    category_singular, element = element_pair[0]
    second_category_singular, second_element = element_pair[1]

    choices_str = ""
    if include_choices:
        # Assuming 'second_elements_list' is provided or accessible somehow; you might need to adjust this part.
        second_elements_list = data[second_category_singular]  # This might need to be adjusted based on actual data structure
        choices_str = " The list must be a subset of (" + ", ".join([f"'{choice}'" for choice in second_elements_list]) + ")."
    elif outputrange is not None:
        lowerbound, upperbound = outputrange
        choices_str = f" (between {lowerbound} and {upperbound})"

    # Default JSON format with a confidence score
    default_format = {category_singular: element, second_category_singular: [{"name": second_element, "confidence score": "a number between 0 and 1"}]}

    # Merge custom fields if provided
    if json_format:
        default_format[second_category_singular][0].update(json_format)

    # Ensure "confidence_score" is the last item, if it exists in the format
    if "confidence score" in default_format[second_category_singular][0]:
        item = default_format[second_category_singular][0]
        item["confidence score"] = item.pop("confidence score")

    json_format_used = json.dumps(default_format, indent=2)

    question = f"For the {category_singular} '{element}', list only each applicable {insertrelationship} {second_category_singular} and omit those unlikely to be applied.{choices_str} Return answer in JSON format: {json_format_used}"
    
    return question
'''
def generate_questions(data, pairing, json_format=None, include_choices=False, insertrelationship='', outputrange=None):
    if outputrange is not None:
        lowerbound, upperbound = outputrange 

    questions = []

    # Handle the first and second parts of the pairing
    category_singular, elements_list, _ = handle_element_pairing(data, pairing[0])
    second_category_singular, second_elements_list, second_elements_list_key = handle_element_pairing(data, pairing[1])

    for element in elements_list:
        choices_str = ""
        if include_choices:
            choices_str = " The list must be a subset of (" + ", ".join([f"'{choice}'" for choice in second_elements_list]) + ")."
        elif outputrange is not None:
            choices_str = f" (between {lowerbound} and {upperbound})"
        
        # Default JSON format with a confidence score
        default_format = {category_singular: element, second_category_singular: [{"name": second_category_singular, "confidence score": "a number between 0 and 1"}]}

        # Merge custom fields if provided
        if json_format:
            default_format[second_category_singular][0].update(json_format)

        # Ensure "confidence_score" is the last item
        item = default_format[second_category_singular][0]
        item["confidence score"] = item.pop("confidence score")

        json_format_used = json.dumps(default_format, indent=2)

        question = f"For the {category_singular} '{element}', list only each applicable {insertrelationship} {second_category_singular} and omit those unlikely to be applied.{choices_str} Return answer in JSON format: {json_format_used}\n"
        questions.append(question)

    return questions




#The next questions are meant to populate the database with relevant pairs for other questions

#Generate questions for support surface and body position
questions_supportsurface_bodyposition = generate_questions(data, ("support surface", "body position"), include_choices=True)
questions_bodyposition_supportsurface = generate_questions(data, ("body position", "support surface"), include_choices=True)

# Generate questions for joints and joint movements
questions_joint_movement = generate_questions(data, ("joint", "joint movement"), include_choices=True)
questions_movement_joint = generate_questions(data, ("joint movement", "joint"), include_choices=True)


#Generate questions for injuries and body structures
questions_injury_bodystructure = generate_questions(data, ("injury", "body structure"), include_choices=True)
questions_bodystructure_injury = generate_questions(data, ("body structure", "injury"), include_choices=True)





# Print the questions
def print_initial_questions():
    print("\nQuestions for Support Surface and Body Position:")
    for question in questions_supportsurface_bodyposition[:5]:
        print(question)

    print("\nQuestions for Body Position and Support Surface:")
    for question in questions_bodyposition_supportsurface[:5]:
        print(question)

    print("\nQuestions for Joints and Joint Movements:")
    for question in questions_joint_movement[:5]:
        print(question)

    print("\nQuestions for Joint Movements and Joints:")
    for question in questions_movement_joint[:5]:
        print(question)

    print("\nQuestions for Injuries and Body Structures:")
    for question in questions_injury_bodystructure[:5]:
        print(question)

    print("\nQuestions for Body Structures and Injuries:")
    for question in questions_bodystructure_injury[:5]:
        print(question)


   

          


#The next questions are meant to be used for the actual questions and dont require db to e populated

#Genrate questions for health conditions and exercise characteristics
questions_healthcondition_exercisecharacteristics = generate_questions(data, ("health condition", "exercise characteristics"), insertrelationship="contraindicated", include_choices=True)

# Generate questions about compensations and muscles
questions_compensation_muscle = generate_questions(data, ("compensation", "muscle"), json_format={"status": "underactive/overactive"})

# Generate quetionss about muscles and exercises
questions_muscle_exercise = generate_questions(data, ("muscle", "exercise"), json_format={"muscle role": "agonist/synergist/stabilizer"}, outputrange = (10,30))

questions_equipment_exercise = generate_questions(data, ("equipment", "exercise"), json_format= {"equipment count": "count", "equipment role": "resistance/MFR/support/elevation/proprioceptive/spatialmarker"}, outputrange = (10,30))


questions_chain_exercise = generate_questions(data, ("chain", "exercise"), outputrange=(20,30))
    #consider adding only for certain muscle groups or body areas
questions_measurement_exercise =  generate_questions(data, ("measurement", "exercise"), outputrange=(10,30))
    #consider adding only for certain muscle groups or body areas
questions_sides_exercise = generate_questions(data, ("side type", "exercise"), outputrange=(10,30))
    #consider adding only for certain muscle groups or body areas

questions_exercise_focus = generate_questions(data, ("exercise focus", "exercise"), outputrange=(10,30))

questions_exercise_characteristics = generate_questions(data, ("exercise characteristics", "exercise"), outputrange=(10,30))

questions_sports_exercise = generate_questions(data, ("sports", "exercise"), outputrange=(10,30))


# Print the questions
def print_independent_questions():

    # Print the first five questions for Compensations and Muscles
    print("\nQuestions for Compensations and Muscles:")
    for question in questions_compensation_muscle[:5]:
        print(question)

    # Print the first five questions for Compensations and Muscles
    print("\nQuestions for Muscles and Exercises:")
    for question in questions_muscle_exercise[:5]:
        print(question)

    # Print the first five questions for Compensations and Muscles
    print("\nQuestions for Equipment and Exercises:")
    for question in questions_equipment_exercise[:5]:
        print(question)

    print("\nQuestions for Measurement and Exercises:")
    for question in questions_measurement_exercise[:5]:
        print(question)
    
    print("\nQuestions for Chain and Exercises:")
    for question in questions_chain_exercise[:5]:
        print(question)

    print("\nQuestions for Sides and Exercises:")
    for question in questions_sides_exercise[:5]:
        print(question)

    print("\nQuestions for Exercise Focus and Exercises:")
    for question in questions_exercise_focus[:5]:
        print(question)     

    print("\nQuestions for Exercise Characteristics and Exercises:")
    for question in questions_exercise_characteristics[:5]:
        print(question) 

    print("\nQuestions for Sports and Exercises:")  
    for question in questions_sports_exercise[:5]:
        print(question) 

    print("\n Questions for health conditions and exercise characteristics:")
    for question in questions_healthcondition_exercisecharacteristics[:5]:
        print(question)

#The next questions require the db to be populated from the last segment

#Generate questions for body position, support surface, and health conditions    
questions_bodyposition_supportsurface_healthcondition = generate_questions(data, (("body position", "support surface", "on"), "health condition"), insertrelationship="contraindicated", include_choices=True)

#Generate questions for body position, support surface, and exercise
questions_bodyposition_exercise = generate_questions(data, (("body position", "support surface", "on"), "exercise"), outputrange=(10,20))

#Generate questions for body position, support surface, and joint injury
questions_bodyposition_supportsurface_injury = generate_questions(data, (("body position", "support surface", "on"), ("joint","injury")), insertrelationship="contraindicated")

#Generate questions for joint injury and body position with support surface
questions_joint_injury_bodyposition_supportsurface = generate_questions(data, (("joint", "injury"), ("body position", "support surface", "on")), insertrelationship="contraindicated")

# Generate questions for injuries, joints and sports
questions_joint_injury_sports = generate_questions(data, (("joint", "injury"), "sports"), include_choices=True)

# Generate questions for injuries, muscles and sports
questions_muscle_injury_sports = generate_questions(data, (("muscle", "injury"), "sports"), include_choices=True)

# Print the questions
def print_dependent_questions():   


    # Print the first five questions for Compensations and Muscles
    print("\nQuestions for Body Position and Support Surface and Exercises:")
    for question in questions_bodyposition_exercise[:5]:
        print(question)

    print("\n Questions for body position, support surface, and joint injury:")
    for question in questions_bodyposition_supportsurface_injury[:5]:
        print(question)

    print("\n Questions for joint injury, body position, and support surface:")
    for question in questions_joint_injury_bodyposition_supportsurface[:5]:
        print(question)

    print("\n Questions for joint injury and sports:")
    for question in questions_joint_injury_sports[:5]:
        print(question)





#print_initial_questions()
#print_independent_questions()
#print_dependent_questions()

#write_questions_to_file(questions_supportsurface_bodyposition, 'supportsurface_bodyposition')
        #DONE
#write_questions_to_file(questions_bodyposition_supportsurface, 'bodyposition_supportsurface')
        #DONE
#write_questions_to_file(questions_joint_movement, 'joint_movement')


class QuestionGenerator:
    def __init__(self, usechatgptapi = False):
        self.load_data(json_file_path)
        if usechatgptapi:
            self.chatgpt = ChatGPT()
            self.use_chatgpt_api = usechatgptapi

    def load_data(self, json_file_path):
        with open(json_file_path, 'r') as file:
            self.data = json.load(file)
      
    
    def append_to_file(self, filename, content):
        with open(filename, 'a') as file:
            file.write(json.dumps(content) + '\n')

    def generate_question(self, role, element_pair: Tuple[Tuple[str, str], str], json_format=None, include_choices=False, insertrelationship='', outputrange=None):
        category_singular, element = element_pair[0]
        second_category_singular = element_pair[1]

        choices_str = ""
        if include_choices:
            # Assuming 'second_elements_list' is part of self.data for the second category
            second_elements_list = self.data[second_category_singular]
            choices_str = " The list must be a subset of (" + ", ".join([f"'{choice}'" for choice in second_elements_list]) + ")."
        elif outputrange is not None:
            lowerbound, upperbound = outputrange
            choices_str = f" (between {lowerbound} and {upperbound})"

        # Default JSON format with placeholders
        default_format = {
            category_singular: "<value>",
            second_category_singular: [{"name": "<value>", "confidence score": "<0-1>"}]
        }

        if json_format:
            default_format.update(json_format)

        # Convert the default_format dictionary to a compact JSON string without new lines
        formatted_json = json.dumps(default_format) # Escape double quotes for inline JSON


        # Replace placeholders with actual values but keep confidence score as a placeholder
     #   formatted_json = json.dumps(default_format, indent=2).replace('"<>', '"').replace('<>"', '"')

        system_message_role = f"You're a {role}."
        system_message_formatting = f"Respond in JSONL: {formatted_json}"
        user_message = f"For the {category_singular} '{element}', list only each applicable {insertrelationship} {second_category_singular} (omitting unlikely ones) along with a confidence score between 0 and 1.{choices_str}"

        return system_message_role, system_message_formatting, user_message
       
    '''    
    def ask_gpt_questions(self, role, pairings, json_format=None, include_choices=False, insertrelationship='', outputrange=None, hardstop = None):
        questions = []
        responses = []
        generated_count = 0 
        for pairing in pairings:
            category_singular, second_category_singular = pairing
            elements_list = data[category_singular]
            second_elements_list = data[second_category_singular] if include_choices else ["applicable elements"]


            for element in elements_list:
                 # If hardstop is set and the limit is reached, break the loop
                if hardstop is not None and generated_count >= hardstop:
                    break

                for second_element in second_elements_list:
                      # Same hardstop check inside the nested loop
                    if hardstop is not None and generated_count >= hardstop:
                        break

                    question_text = self.generate_question(
                        self.data,
                        role,
                        ((category_singular, element), (second_category_singular, second_element)),
                        json_format=json_format,
                        include_choices=include_choices,
                        insertrelationship=insertrelationship,
                        outputrange=outputrange
                    )
                    questions.append(question_text)
                    generated_count += 1 
                    if self.use_chatgpt_api:
                        response = self.chatgpt._get_chatgpt_response(question_text)
                          # Process and return the response
                        print(response)
                        if response.choices:
                            adjustment_details_raw = response.choices[0].text.strip()

                            # Clean the response and extract JSON
                            cleaned_details = self.chatgpt.clean_json_response(adjustment_details_raw)
                            if cleaned_details:
                                try:
                                    adjustment_json = json.loads(cleaned_details)
                                    responses.append(adjustment_json)
                                    self.append_to_file('gpt_answers.txt', adjustment_json)
                                except json.JSONDecodeError as je:
                                    print(f"JSON parsing error: {je}")  # Replace with appropriate logging
                            else:
                                print("No valid JSON found in the response after attempting to clean json")  # Replace with appropriate logging
                        else:
                            print("Adjustment details response is empty or invalid")  # Replace with appropriate logging
        

        return questions, responses
        '''

#questions = QuestionGenerator(usechatgptapi = True)
#questions.ask_gpt_questions(data, "personal trainer", [("support surface", "body position")], include_choices=True, hardstop=5)