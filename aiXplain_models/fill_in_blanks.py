import json
from aixplain.factories import ModelFactory

def generate_fill_in_the_blanks(input_text, model_id="674b73f06eb563a748561d41", temperature=0.7, max_tokens=300):
    """
    Generates fill-in-the-blank multiple-choice questions from the given input text using the specified AI model.

    Parameters:
    - input_text (str): The text from which FITB questions should be generated.
    - model_id (str): The AI model ID to use for question generation.
    - temperature (float): Controls the randomness of the output.
    - max_tokens (int): The maximum number of tokens to generate.

    Returns:
    - dict: A dictionary containing the generated FITB questions in JSON format.
    """
    try:
        model = ModelFactory.get(model_id)

        prompt = (
            "Generate fill-in-the-blanks questions with multiple-choice options based on the following text. "
            "Each question should have a blank space for a key term and four options labeled (a), (b), (c), and (d), "
            "with the correct answer indicated in JSON format like this: "
            "{\"questions\": [{\"question\": \"<sentence with blank>\", \"options\": [\"(a) <option1>\", \"(b) <option2>\", \"(c) <option3>\", \"(d) <option4>\"], \"answer\": \"<correct_option>\"}]}"
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

fitb_questions = generate_fill_in_the_blanks(input_text)
if fitb_questions:
    print(json.dumps(fitb_questions, indent=4))
