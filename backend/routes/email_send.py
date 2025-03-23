from flask import Blueprint, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from aixplain.client import AIXplainClient

email_bp = Blueprint('email', __name__, url_prefix='/email')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

def generate_enhanced_content(original_content, content_type="email"):
    """
    Use aiXplain to enhance the content of the email
    """
    try:
        prompt = f"""
        Please improve the following {content_type} content:
        
        {original_content}
        
        Make it more professional and engaging while keeping the original message intent.
        """
        
        response = client.run(
            model_id="aixplain-default-text-generation",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        enhanced_content = response.get("output", original_content)
        return enhanced_content
    except Exception as e:
        print(f"Error with aiXplain content enhancement: {e}")
        return original_content

def send_email(recipient_emails, subject, content):
    # Get email credentials from environment variables for security
    sender_email = os.environ.get("EMAIL_SENDER", "")
    sender_password = os.environ.get("EMAIL_PASSWORD", "")
    
    if not sender_email or not sender_password:
        print("Email credentials not configured")
        return False

    try:
        # Enhance the email content using aiXplain
        enhanced_content = generate_enhanced_content(content)
        
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender_email, sender_password)

        for recipient_email in recipient_emails:
            email_message = MIMEMultipart()
            email_message['From'] = sender_email
            email_message['To'] = recipient_email
            email_message['Subject'] = subject
            email_message.attach(MIMEText(enhanced_content, 'plain'))

            smtp_server.send_message(email_message)

        smtp_server.quit()
        print("Email sent successfully to all recipients")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@email_bp.route('/send', methods=['POST'])
def send_email_route():
    try:
        data = request.json
        recipient_emails = data.get('recipients', [])
        subject = data.get('subject', '')
        content = data.get('content', '')
        
        if not recipient_emails or not subject or not content:
            return jsonify({"error": "Missing required fields"}), 400
            
        success = send_email(recipient_emails, subject, content)
        
        if success:
            return jsonify({"message": "Email sent successfully"})
        else:
            return jsonify({"error": "Failed to send email"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_bp.route('/generate_content', methods=['POST'])
def generate_content():
    """
    Generate email content using aiXplain
    """
    try:
        data = request.json
        topic = data.get('topic', '')
        purpose = data.get('purpose', '')
        
        if not topic or not purpose:
            return jsonify({"error": "Missing required fields"}), 400
        
        prompt = f"""
        Generate an email with the following specifications:
        Topic: {topic}
        Purpose: {purpose}
        
        Please create a professional email that effectively communicates this information.
        """
        
        response = client.run(
            model_id="aixplain-default-text-generation",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        generated_content = response.get("output", "Unable to generate content")
        return jsonify({"content": generated_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_bp.route('/reminder', methods=['POST'])
def send_reminder():
    """Send reminders to students about upcoming classes"""
    try:
        data = request.json
        recipients = data.get('recipients', [])
        class_name = data.get('class_name', '')
        start_time = data.get('start_time', '')
        
        if not recipients or not class_name or not start_time:
            return jsonify({"error": "Missing required fields"}), 400
            
        reminder_content = f"Reminder: Your {class_name} class starts in {start_time}. Please be prepared and join on time."
        subject = f"Reminder: {class_name} class"
        
        # Use aiXplain to enhance the reminder
        enhanced_reminder = generate_enhanced_content(reminder_content, "reminder")
        
        success = send_email(recipients, subject, enhanced_reminder)
        
        if success:
            return jsonify({"message": "Reminder sent successfully"})
        else:
            return jsonify({"error": "Failed to send reminder"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500