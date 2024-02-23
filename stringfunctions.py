

import psycopg2
import re
import sqlparse
import json
import traceback


def sanitize_string(value):
        sanitized_value = re.sub(r"'", "''", value)
        return sanitized_value.strip().lower()

def to_singular(word):
    # Handle special irregular cases
    irregulars = {
        'feet': 'foot',
        'teeth': 'tooth',
        'geese': 'goose',
        # Add more irregular plural forms as needed
    }
    if word in irregulars:
        return irregulars[word]

    # Handle regular cases
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word.endswith('es') and len(word) > 2:
        # Handles cases like "pushes" to "push"
        if word[-3] in 'sxz' or word[-4:-2] in ['sh', 'ch']:
            return word[:-2]
        # Special cases where 'es' is not a plural marker
        elif word.lower() in ['series', 'species']:
            return word
    elif word.endswith('s') and not word.endswith('ss'):
        # Check for vowel before 's' or specific words
        if word[-2] in 'aeiou' or word.lower() in ['plus', 'bias', 'corps']:
            return word
        return word[:-1]

    return word



def clean_json_response(response_text):
    start_index = response_text.find('{')
    end_index = response_text.rfind('}') + 1  # +1 to include the '}' in the substring
    if start_index == -1 or end_index == 0:
        return None  # Indicates no valid JSON found
    return response_text[start_index:end_index]


def preprocess_response_content_keys(response_content):
    """Transform all keys in a nested dictionary to singular and lowercase."""
    if isinstance(response_content, dict):
        return {
            to_singular(key).lower(): preprocess_response_content_keys(value) 
            for key, value in response_content.items()
        }
    elif isinstance(response_content, list):
        return [preprocess_response_content_keys(item) for item in response_content]
    else:
        return response_content