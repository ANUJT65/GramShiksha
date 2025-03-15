import json
from aixplain.factories import ModelFactory

def generate_true_false_questions(input_text, model_id="674b73f06eb563a748561d41", temperature=0.7, max_tokens=300):
    """
    Generates True/False questions from the given input text using the specified AI model.

    Parameters:
    - input_text (str): The text from which True/False questions should be generated.
    - model_id (str): The AI model ID to use for question generation.
    - temperature (float): Controls the randomness of the output.
    - max_tokens (int): The maximum number of tokens to generate.

    Returns:
    - dict: A dictionary containing the generated True/False questions in JSON format.
    """
    try:
        model = ModelFactory.get(model_id)

        prompt = (
            "Generate true or false questions in the following JSON format: "
            "{\"questions\": [{\"question\": \"<question_text>\", \"answer\": \"True/False\"}]}. "
            "Ensure the entire output is valid JSON and enclosed within curly braces {}."
        )

        result = model.run({
            "text": input_text,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        })

        json_result = json.loads(result["output"])
        return json_result

    except (json.JSONDecodeError, KeyError):
        print("Invalid JSON format in model response.")
        print(f"Raw response: {result}")
        return None

# Example usage
input_text = """
The mitochondrion is often referred to as the powerhouse of the cell. It is responsible for generating ATP, 
the energy currency of the cell, through a process called cellular respiration. This organelle is found in 
most eukaryotic cells and plays a crucial role in energy production and metabolism.
"""

tf_questions = generate_true_false_questions(input_text)
if tf_questions:
    print(json.dumps(tf_questions, indent=4))
