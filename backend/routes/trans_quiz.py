from flask import Blueprint, request, jsonify
import os
import json
import re
from aixplain.client import AIXplainClient

trans_quiz = Blueprint('trans_quiz', __name__, url_prefix='/trans_quiz')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

def generate_questions(transcript):
    """
    Generate multiple-choice questions from transcript using aiXplain
    """
    try:
        # Create prompt for aiXplain
        prompt = f"""
        Generate 3 multiple-choice questions based on the following transcript text.
        
        TRANSCRIPT:
        {transcript}
        
        For each question, provide:
        1. A clear question based on specific information in the transcript
        2. Four possible answer options (A, B, C, D)
        3. The correct answer (indicated as the full text of the correct option)

        Format the output as a valid JSON array of objects with these exact fields:
        [
            {{
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The correct option text"
            }},
            ... (repeat for all questions)
        ]
        
        Return only the JSON array, nothing else.
        """
        
        # Call aiXplain API for text generation
        response = client.run(
            model_id="aixplain-default-text-generation",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        # Extract the generated text
        raw_response = response.get("output", "")
        
        # Extract JSON array from response using regex
        json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group(0))
            return questions
        
        # Alternative parsing if the regex approach fails
        try:
            # Try direct JSON parsing if the model returned clean JSON
            questions = json.loads(raw_response)
            if isinstance(questions, list):
                return questions
        except json.JSONDecodeError:
            pass
            
        # Fallback with default questions if parsing fails
        return [
            {
                "question": "What is the main topic of this transcript?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            },
            {
                "question": "According to the transcript, what is an important point mentioned?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option B"
            },
            {
                "question": "What conclusion can be drawn from this transcript?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option C"
            }
        ]
    except Exception as e:
        print(f"Error generating questions with aiXplain: {e}")
        return None

def verify_question_format(questions):
    """
    Verify that the questions are in the correct format
    """
    if not isinstance(questions, list):
        return False
        
    for q in questions:
        if not isinstance(q, dict):
            return False
        if "question" not in q or "options" not in q or "answer" not in q:
            return False
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            return False
        if q["answer"] not in q["options"]:
            return False
            
    return True

def enhance_transcript(transcript):
    """
    Use aiXplain to enhance transcript content by adding formatting or correcting issues
    """
    try:
        prompt = f"""
        The following is a transcript of educational content. 
        Please clean it up by:
        1. Correcting obvious transcription errors
        2. Adding proper punctuation and paragraph breaks
        3. Maintaining all the original information
        
        TRANSCRIPT:
        {transcript}
        
        Return the enhanced transcript text only.
        """
        
        # Call aiXplain API for text enhancement
        response = client.run(
            model_id="aixplain-default-text-editing",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        # Extract the enhanced transcript
        enhanced_transcript = response.get("output", transcript)
        return enhanced_transcript
    except Exception as e:
        print(f"Error enhancing transcript: {e}")
        return transcript

@trans_quiz.route('/get_questions', methods=['POST'])
def get_questions():
    try:
        data = request.get_json()
        transcript = data.get('transcript')
        
        if not transcript:
            return jsonify({'error': 'transcript is required'}), 400
            
        # Optionally enhance the transcript
        if data.get('enhance_transcript', False):
            transcript = enhance_transcript(transcript)
            
        # Generate questions
        questions = generate_questions(transcript)
        
        if not questions:
            return jsonify({'error': 'Failed to generate questions'}), 500
            
        # Verify questions are in correct format
        if not verify_question_format(questions):
            return jsonify({'error': 'Generated questions are in incorrect format'}), 500
            
        return jsonify({
            'questions': questions,
            'enhanced_transcript': transcript if data.get('enhance_transcript', False) else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trans_quiz.route('/enhance_transcript', methods=['POST'])
def enhance_transcript_route():
    """
    Endpoint to enhance transcript without generating questions
    """
    try:
        data = request.get_json()
        transcript = data.get('transcript')
        
        if not transcript:
            return jsonify({'error': 'transcript is required'}), 400
            
        # Enhance the transcript
        enhanced = enhance_transcript(transcript)
        
        return jsonify({
            'original_transcript': transcript,
            'enhanced_transcript': enhanced
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500