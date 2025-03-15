import json
from aixplain.factories import ModelFactory

def generate_summary(text: str) -> dict:
    """
    Generates a concise bullet-point summary of the given text using the Gemini 1.5 Flash model.
    Returns the summary as a JSON dictionary.
    """
    model = ModelFactory.get("674b73f06eb563a748561d41")
    
    prompt = (
        "Generate a concise summary in bullet points format. "
        "Output it strictly in JSON format as follows: "
        "{\"summary\": [\"<bullet_point_1>\", \"<bullet_point_2>\", ...]}. "
        "Ensure there are no additional text, only valid JSON."
    )
    
    result = model.run({
        "text": text,
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 200
    })
    
    try:
        summary_json = json.loads(result.get("output", "{}"))
        return summary_json
    except json.JSONDecodeError:
        print("Invalid JSON format in model response.")
        print(f"Raw response: {result}")
        return {}

# Example Usage
if __name__ == "__main__":
    input_text = (
        "The mitochondrion is often referred to as the powerhouse of the cell. "
        "It is responsible for generating ATP, the energy currency of the cell, "
        "through a process called cellular respiration. This organelle is found "
        "in most eukaryotic cells and plays a crucial role in energy production and metabolism."
    )
    summary = generate_summary(input_text)
    print(json.dumps(summary, indent=4))
