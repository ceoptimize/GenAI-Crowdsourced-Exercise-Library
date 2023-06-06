
import openai
import requests
import json



# set the API endpoint
endpoint = "https://api.chatgpt.com/v1/chat"
openai.api_key = "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"
model_engine = "text-davinci-003"
#prompt = "Give me a json of 10 exercises and the body parts worked"
prompt = "Give me a json with properties 'Exercise' and 'Body parts worked' with 10 entries"

completion = openai.Completion.create(
    engine = model_engine,
    prompt = prompt,
    max_tokens = 1024,
    n = 1, 
    stop = None, 
    temperature = .5
)

response = completion.choices[0].text
print(response)

with open("jsonoutput.json", "w") as file:
    file.write(response)


