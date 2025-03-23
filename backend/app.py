from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from aixplain.client import AIXplainClient

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Data storage paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
HISTORY_FILE = os.path.join(DATA_DIR, 'explanation_history.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize history file if it doesn't exist
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
                            "allow_headers": ["Content-Type", "Authorization"]}})

# Import blueprints
from routes import testing 
from routes import video_to_text
from routes import database_get_command
from routes import registration
from routes import login_app
from routes import chat_bot
from routes import question_ans
from routes import gov_data
from routes import message_send
from routes import email_send
from routes import trans_quiz
from routes import data_form_media
from routes import doc_db
from routes import infra

# Register blueprints
app.register_blueprint(testing.ts)
app.register_blueprint(video_to_text.vt)
app.register_blueprint(database_get_command.db)
app.register_blueprint(registration.rg)
app.register_blueprint(login_app.lg)
app.register_blueprint(chat_bot.ch)
app.register_blueprint(question_ans.qa)
app.register_blueprint(gov_data.gov_data)
app.register_blueprint(message_send.sms_blueprint)
app.register_blueprint(email_send.email_bp)
app.register_blueprint(trans_quiz.trans_quiz)
app.register_blueprint(data_form_media.data_form_media)
app.register_blueprint(doc_db.doc_db)
app.register_blueprint(infra.school_recommendation_bp)

def save_to_history(code, explanation):
    """Save code explanation to history"""
    try:
        # Read existing history
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        # Add new entry
        entry = {
            "id": len(history) + 1,
            "code": code,
            "explanation": explanation,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        history.append(entry)
        
        # Save updated history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
        return entry["id"]
    except Exception as e:
        print(f"Error saving to history: {e}")
        return None

@app.route('/', methods=['GET'])
def hello_world():
    return 'Server is running!'

@app.route('/api/explain', methods=['POST'])
def explain_code():
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
            
        # Generate explanation using aiXplain
        prompt = f"""
        Please analyze and explain the following {language} code:
        
        ```{language}
        {code}
        ```
        
        Provide a response in JSON format with the following fields:
        1. "summary": A brief 1-2 sentence overview of what the code does
        2. "details": A more detailed explanation of how the code works
        3. "complexity": An assessment of the code complexity (low, medium, high)
        4. "suggestions": Optional improvements or best practices
        
        Return only valid JSON.
        """
        
        try:
            response = client.run(
                model_id="aixplain-default-code-analysis",  # Replace with your actual model ID
                data=prompt,
                task="text-generation"
            )
            
            response_text = response.get("output", "")
            
            # Try to parse JSON from the response
            try:
                # Look for JSON pattern in response
                import re
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    explanation = json.loads(json_match.group(1))
                else:
                    explanation = json.loads(response_text)
            except:
                # Fallback if JSON parsing fails
                explanation = {
                    "summary": "Code analysis complete.",
                    "details": response_text,
                    "complexity": "medium",
                    "suggestions": "Unable to format specific suggestions."
                }
                
        except Exception as ai_error:
            print(f"Error with aiXplain: {ai_error}")
            # Fallback explanation
            explanation = {
                "summary": "This code was analyzed, but detailed explanation failed.",
                "details": f"The system encountered an error during analysis. Original code was {len(code)} characters long.",
                "complexity": "unknown",
                "suggestions": "Please try again with a different code sample."
            }
        
        # Save to history
        from datetime import datetime
        entry_id = save_to_history(code, explanation)
        
        return jsonify({
            "explanation": explanation,
            "history_id": entry_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        # Read history from file
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            
        # Limit code length in response to avoid large payloads
        for entry in history:
            if len(entry.get("code", "")) > 200:
                entry["code"] = entry["code"][:200] + "..."
                
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<int:history_id>', methods=['GET'])
def get_history_entry(history_id):
    try:
        # Read history from file
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            
        # Find entry with matching ID
        entry = next((e for e in history if e.get("id") == history_id), None)
        
        if not entry:
            return jsonify({"error": "History entry not found"}), 404
            
        return jsonify({"entry": entry})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)