import os
import openai
from flask import Flask, render_template, request
from api import Api

class CodeProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    def split_code(self, code, max_length):
        chunks = []
        current_chunk = ''
        lines = code.split('\n')
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= max_length:
                current_chunk += line + '\n'
            else:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
        chunks.append(current_chunk)
        return chunks

    def process_code_folder(self, folder_path, break_lines=1000):
            code = ''
            line_count = 0

            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.py'):
                        with open(os.path.join(root, file), 'r') as f:
                            for line in f:
                                code += line
                                line_count += 1

                                if break_lines and line_count >= break_lines:
                                    break

                            if break_lines and line_count >= break_lines:
                                break

                if break_lines and line_count >= break_lines:
                    break

            code_chunks = self.split_code(code, max_length=4096)  # Specify your desired chunk length

            for chunk in code_chunks:
                response = openai.Completion.create(
                    engine='text-davinci-003',  # Choose the appropriate engine
                    prompt=chunk,
                    max_tokens=256,  # Set a suitable value for your use case
                    temperature=0.7,  # Adjust the temperature as needed
                    n=1,  # Set the number of completions you want to receive
                    stop=None,  # Add custom stop sequences if desired
                    timeout=60  # Set a timeout value if necessary
                )

                # Process the response from the API, if needed
                # You can store the relevant information, perform analysis, etc.


    def chatbot_generate_response(self, user_input):
            response = openai.Completion.create(
                engine='text-davinci-003',  # Choose the appropriate engine
                prompt=user_input,
                max_tokens=256,  # Set a suitable value for your use case
                temperature=0.7,  # Adjust the temperature as needed
                n=1,  # Set the number of completions you want to receive
                stop=None,  # Add custom stop sequences if desired
                timeout=60  # Set a timeout value if necessary
            )

            # Process the response from the API, if needed
            # You can extract the generated completion and return it
            completion = response.choices[0].text.strip()
            return completion


class WebInterface:
    def __init__(self, code_processor):
        self.app = Flask(__name__)
        self.code_processor = code_processor

        @self.app.route('/', methods=['GET', 'POST'])
        def home():
            if request.method == 'POST':
                user_input = request.form['user_input']
                response = self.code_processor.chatbot_generate_response(user_input)
                return render_template('index.html', response=response)
            else:
                return render_template('index.html')

    def run(self):
        self.app.run(debug=True, port=8000)

if __name__ == '__main__':
    api_key=Api().chat_gpt_api
    code_processor = CodeProcessor(api_key)
    code_processor.process_code_folder('Users/christieentwistle/PyCharmprojects/mealie')

    web_interface = WebInterface(code_processor)
    web_interface.run()
