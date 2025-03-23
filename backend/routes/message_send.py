from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime
from aixplain.client import AIXplainClient

sms_blueprint = Blueprint('sms_blueprint', __name__, url_prefix='/sms')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Path to messages directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
MESSAGES_DIR = os.path.join(DATA_DIR, 'messages')
MESSAGES_FILE = os.path.join(MESSAGES_DIR, 'sent_messages.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MESSAGES_DIR, exist_ok=True)

def initialize_messages_file():
    """Initialize the messages file if it doesn't exist"""
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)

def generate_message_with_aixplain(message_type, context=None):
    """
    Generate a message using aiXplain based on the message type
    """
    try:
        if message_type == "class_reminder":
            prompt = """
            Generate a friendly SMS reminder for students about an upcoming class.
            The message should be concise (under 160 characters), friendly, and include:
            1. A reminder that class starts in 10 minutes
            2. An encouragement to join promptly
            3. A brief motivational note
            """
        elif message_type == "assignment_due":
            prompt = """
            Generate a brief SMS reminder for students about an assignment due soon.
            Keep it under 160 characters, friendly but clear, and include:
            1. A reminder about the assignment due date
            2. A brief encouragement to complete it on time
            3. Where they can submit the assignment
            """
        elif message_type == "exam_reminder":
            prompt = """
            Generate a brief SMS alert for students about an upcoming exam.
            Keep it under 160 characters, supportive but clear, and include:
            1. A reminder about the exam date and time
            2. What to bring (if applicable)
            3. A brief encouragement or good luck message
            """
        elif message_type == "custom":
            if not context:
                return "Please provide context for custom message generation."
            prompt = f"""
            Generate a brief SMS message based on the following context:
            {context}
            
            Keep it under 160 characters and make it professional but friendly.
            """
        else:
            prompt = "Generate a brief, friendly SMS notification for students. Keep it under 160 characters."

        # Call aiXplain API for text generation
        response = client.run(
            model_id="aixplain-default-text-generation",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        # Extract the generated text
        generated_message = response.get("output", "Class reminder: Your class starts in 10 minutes. Please join promptly!")
        
        # Ensure the message is not too long for SMS
        if len(generated_message) > 160:
            generated_message = generated_message[:157] + "..."
            
        return generated_message
    except Exception as e:
        print(f"Error generating message with aiXplain: {e}")
        return "Class reminder: Your class starts in 10 minutes. Please join promptly!"

def log_message(recipient, message, status="simulated"):
    """Log the message in the local file system"""
    try:
        initialize_messages_file()
        
        # Read existing messages
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
        
        # Add new message log
        messages.append({
            "id": len(messages) + 1,
            "recipient": recipient,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save updated messages
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error logging message: {e}")
        return False

def simulate_send_text_message(recipient, message):
    """
    Simulate sending a text message (no actual SMS is sent)
    In a production environment, replace this with an actual SMS service
    """
    try:
        # Log the simulated message
        log_success = log_message(recipient, message)
        
        if log_success:
            print(f"Simulated message to {recipient}: {message}")
            return True
        else:
            print("Failed to log the message")
            return False
    except Exception as e:
        print(f"Error in message simulation: {e}")
        return False

@sms_blueprint.route('/send', methods=['GET', 'POST'])
def send_sms():
    """
    Simulate sending an SMS with a default class reminder
    No actual SMS is sent - this is just a simulation
    """
    # Generate message using aiXplain
    message_to_send = generate_message_with_aixplain("class_reminder")
    
    # Simulate sending to a default recipient
    recipient = "+1234567890"  # Placeholder
    success = simulate_send_text_message(recipient, message_to_send)
    
    if success:
        return jsonify({"message": "Message simulated successfully!", "content": message_to_send}), 200
    else:
        return jsonify({"error": "Failed to simulate message"}), 500

@sms_blueprint.route('/custom', methods=['POST'])
def send_custom_sms():
    """
    Simulate sending a custom SMS based on provided data
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get recipient and message_type from request
        recipient = data.get('recipient', '+1234567890')  # Default placeholder
        message_type = data.get('message_type', 'custom')
        context = data.get('context', None)
        
        # Generate message using aiXplain
        message_to_send = generate_message_with_aixplain(message_type, context)
        
        # Simulate sending
        success = simulate_send_text_message(recipient, message_to_send)
        
        if success:
            return jsonify({"message": "Custom message simulated successfully!", "content": message_to_send}), 200
        else:
            return jsonify({"error": "Failed to simulate custom message"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sms_blueprint.route('/history', methods=['GET'])
def get_message_history():
    """Get history of sent messages"""
    try:
        initialize_messages_file()
        
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
            
        return jsonify({"messages": messages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500