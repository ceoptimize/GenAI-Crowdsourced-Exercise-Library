class ModelPricing:
    def __init__(self):
        # Hardcoded model pricing information
        self.model_costs = {
            "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
            "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
            "gpt-4-1106-vision-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-32k": {"input": 0.06, "output": 0.12},
            "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
            "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo": {"training": 0.008, "input": 0.003, "output": 0.006},
            "davinci-002": {"training": 0.006, "input": 0.012, "output": 0.012},
            "babbage-002": {"training": 0.0004, "input": 0.0016, "output": 0.0016},
            "text-embedding-3-small": {"usage": 0.00002},
            "text-embedding-3-large": {"usage": 0.00013},
            "ada v2": {"usage": 0.00010},
            # Base models
            "davinci-002-base": {"usage": 0.002},
            "babbage-002-base": {"usage": 0.0004},
            # Older models
            "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002},
            "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-16k-0613": {"input": 0.003, "output": 0.004},
            "gpt-3.5-turbo-0301": {"input": 0.0015, "output": 0.002},
            # Note: Image and Audio models have different pricing structures not based on tokens
        }

        self.token_basis = 1000  # Basis for token calculation

    def get_model_cost(self, model_name):
            if model_name in self.model_costs:
                model_cost = self.model_costs[model_name]
                input_cost = model_cost.get("input", None)
                output_cost = model_cost.get("output", None)
                return input_cost, output_cost, self.token_basis
            else:
                return None, None, None  # Or handle the error as preferred

    def print_models_output_cost_ranked(self):
        # Extract models and output costs, filter out models without an output cost
        models_output_costs = [(model, details.get("output", float('inf'))) for model, details in self.model_costs.items() if "output" in details]

        # Sort models by their output costs in ascending order
        models_sorted_by_output_cost = sorted(models_output_costs, key=lambda x: x[1])

        # Print the sorted models and their output costs
        for model, cost in models_sorted_by_output_cost:
            print(f"{model}: ${cost} per 1K tokens")


'''
# Example usage
model_pricing = ModelPricing()

# Get the input and output costs for a model
input_cost, output_cost, token_basis = model_pricing.get_model_cost("gpt-3.5-turbo")
print(f"Input cost: ${input_cost} per 1K tokens, Output cost: ${output_cost} per 1K tokens, Token basis: {token_basis}")
model_pricing.print_models_output_cost_ranked()
'''