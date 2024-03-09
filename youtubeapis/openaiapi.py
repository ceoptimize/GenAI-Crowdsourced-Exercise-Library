import json

class OpenaiApi:
    def __init__(self):
        with open('config/config.json') as config_file:
            config = json.load(config_file)
            self.chat_gpt_api  = config['openai']['api_key']