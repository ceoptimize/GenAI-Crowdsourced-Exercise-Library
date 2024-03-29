from openai import OpenAI
import tiktoken

class OpenAICommunication:
    """Manages interactions with the OpenAI API."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)


    def chat_completion_request(self, messages, model="gpt-3.5-turbo", max_tokens=180, temperature=0):
        """
        Requests a chat completion from the OpenAI API.

        Parameters:
            messages (list): A list of message dictionaries.
            model (str): The model to be used for the chat completion.
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): The temperature for the chat completion.

        Returns:
            The response from the OpenAI API or an exception.
        """
        try:
            response = self.client.chat.completions.create(
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

class TikTokenCommunication:
    """Manages interactions with the TikToken API."""
    

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """
        Calculates the number of tokens from a list of messages.

        Parameters:
            messages (list): A list of message dictionaries.
            model (str): The model to be used for token calculation.

        Returns:
            int: The number of tokens.
        """
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
            # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_message = 4
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print(
                "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
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

