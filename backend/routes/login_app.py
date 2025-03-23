from flask import Blueprint, request, jsonify
import os
import json
import hashlib
import uuid
from datetime import datetime
from aixplain.client import AIXplainClient

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

lg = Blueprint('login_app', __name__, url_prefix='/login')

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
USERS_DIR = os.path.join(DATA_DIR, 'users')
STUDENT_FILE = os.path.join(USERS_DIR, 'students.json')
TEACHER_FILE = os.path.join(USERS_DIR, 'teachers.json')
LOGIN_LOGS_FILE = os.path.join(USERS_DIR, 'login_logs.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)

def initialize_user_files():
    """Initialize the user data files if they don't exist"""
    if not os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(TEACHER_FILE):
        with open(TEACHER_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(LOGIN_LOGS_FILE):
        with open(LOGIN_LOGS_FILE, 'w') as f:
            json.dump([], f)

def get_users(role):
    """Get all users from the JSON file based on role"""
    initialize_user_files()
    
    file_path = STUDENT_FILE if role == 'student' else TEACHER_FILE
    
    try:
        with open(file_path, 'r') as f:
            users = json.load(f)
        return users
    except Exception as e:
        print(f"Error reading users data: {e}")
        return []

def add_login_log(user_id, role, email, status):
    """Add a login attempt to the logs"""
    try:
        # Read existing logs
        if os.path.exists(LOGIN_LOGS_FILE):
            with open(LOGIN_LOGS_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new log
        logs.append({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "role": role,
            "email": email,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save updated logs
        with open(LOGIN_LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"Error adding login log: {e}")

def analyze_login_pattern(user_id, role):
    """
    Use aiXplain to analyze login patterns for security insights
    """
    try:
        # Read login logs
        if os.path.exists(LOGIN_LOGS_FILE):
            with open(LOGIN_LOGS_FILE, 'r') as f:
                logs = json.load(f)
        else:
            return "No login history available for analysis."
        
        # Filter logs for the specific user
        user_logs = [log for log in logs if log.get('user_id') == user_id]
        
        if len(user_logs) < 2:
            return "Insufficient login history for pattern analysis."
        
        # Format the logs data for analysis
        logs_data = json.dumps(user_logs, indent=2)
        
        prompt = f"""
        Analyze the following login history for a {role} with ID {user_id}.
        
        LOGIN HISTORY:
        {logs_data}
        
        Please provide:
        1. A summary of login patterns (time of day, frequency)
        2. Any unusual or suspicious activity
        3. Security recommendations based on the observed patterns
        
        Keep the analysis concise and focused on security aspects.
        """
        
        # Call aiXplain API for analysis
        response = client.run(
            model_id="aixplain-default-text-analysis",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        return response.get("output", "Analysis could not be generated.")
    except Exception as e:
        print(f"Error analyzing login pattern: {e}")
        return "Error during login pattern analysis."

@lg.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        role = data.get('role')
        email = data.get('email')
        password = data.get('password')

        if not role or not email or not password:
            return jsonify({"error": "Role, email, and password are required"}), 400

        # Hash the password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        users = get_users(role)
        
        # Find the user
        user_found = None
        for user in users:
            if user.get('email') == email:
                user_found = user
                break
        
        if user_found:
            # In a production system, use a secure password hashing library
            if user_found.get('password') == password:  # Compare with stored password
                # Use aiXplain to analyze login patterns
                security_analysis = analyze_login_pattern(user_found.get('id'), role)
                
                # Log successful login
                add_login_log(user_found.get('id'), role, email, "success")
                
                return jsonify({
                    "message": f"{role.capitalize()} login successful",
                    "user_id": user_found.get('id'),
                    "security_analysis": security_analysis
                }), 200
            else:
                # Log failed login
                add_login_log(user_found.get('id'), role, email, "failed_password")
                return jsonify({"error": "Invalid password"}), 401
        else:
            # Log unknown user attempt
            add_login_log("unknown", role, email, "user_not_found")
            return jsonify({"error": f"{role.capitalize()} not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lg.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        role = data.get('role')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not role or not email or not password or not name:
            return jsonify({"error": "Role, email, password, and name are required"}), 400

        users = get_users(role)
        
        # Check if user already exists
        for user in users:
            if user.get('email') == email:
                return jsonify({"error": f"{role.capitalize()} with this email already exists"}), 400
        
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,  # In production, use proper password hashing
            "created_at": datetime.now().isoformat()
        }
        
        # Add user to the appropriate file
        users.append(new_user)
        
        file_path = STUDENT_FILE if role == 'student' else TEACHER_FILE
        with open(file_path, 'w') as f:
            json.dump(users, f, indent=2)
        
        return jsonify({"message": f"{role.capitalize()} registered successfully", "user_id": new_user["id"]}), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lg.route('/testing', methods=['GET'])
def testing():
    return 'Login service is running!'

@lg.route('/analyze_security', methods=['POST'])
def analyze_security():
    """
    Analyze login security for a user using aiXplain
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        role = data.get('role')
        
        if not user_id or not role:
            return jsonify({"error": "User ID and role are required"}), 400
            
        security_analysis = analyze_login_pattern(user_id, role)
        
        return jsonify({"security_analysis": security_analysis}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500