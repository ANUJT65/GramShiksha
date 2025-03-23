from flask import Blueprint, request, jsonify
import os
import json
import uuid
from datetime import datetime
from aixplain.client import AIXplainClient

rg = Blueprint('registration', __name__, url_prefix='/registration')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
USERS_DIR = os.path.join(DATA_DIR, 'users')
STUDENT_FILE = os.path.join(USERS_DIR, 'students.json')
TEACHER_FILE = os.path.join(USERS_DIR, 'teachers.json')

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

def get_users(role):
    """Get all users for a specific role"""
    initialize_user_files()
    file_path = STUDENT_FILE if role == 'student' else TEACHER_FILE
    
    try:
        with open(file_path, 'r') as f:
            users = json.load(f)
        return users
    except Exception as e:
        print(f"Error reading users: {e}")
        return []

def save_users(users, role):
    """Save users for a specific role"""
    file_path = STUDENT_FILE if role == 'student' else TEACHER_FILE
    
    try:
        with open(file_path, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def generate_profile_recommendations(user_data, role):
    """Generate profile recommendations using aiXplain"""
    try:
        user_json = json.dumps(user_data)
        
        if role == 'student':
            prompt = f"""
            Based on this student profile:
            {user_json}
            
            Please provide:
            1. Learning style recommendations
            2. Suggested study techniques
            3. One personalized tip for academic success
            
            Keep it brief and encouraging.
            """
        else:  # teacher
            prompt = f"""
            Based on this teacher profile:
            {user_json}
            
            Please provide:
            1. Teaching style recommendations
            2. Classroom management tips
            3. One personalized suggestion for effective teaching
            
            Keep it brief and practical.
            """
        
        # Call aiXplain API
        response = client.run(
            model_id="aixplain-default-text-generation",
            data=prompt,
            task="text-generation"
        )
        
        return response.get("output", "Unable to generate recommendations at this time.")
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return "Error generating recommendations."

@rg.route('/register', methods=['POST'])
def register():
    data = request.json
    role = data.get('role')
    email = data.get('email')
    password = data.get('password')

    if not role or not email or not password:
        return jsonify({"error": "Role, email, and password are required"}), 400

    users = get_users(role)
    
    # Check if user with this email already exists
    if any(user.get('email') == email for user in users):
        return jsonify({"error": f"{role.capitalize()} with this email already exists"}), 400

    # Create new user with unique ID
    user_id = str(uuid.uuid4())
    
    if role == 'student':
        student_name = data.get('student_name')
        if not student_name:
            return jsonify({"error": "Student name is required"}), 400
            
        new_user = {
            'student_id': user_id,
            'student_name': student_name,
            'email': email,
            'password': password,  # In production, use password hashing
            'grade': data.get('grade', ''),
            'age': data.get('age', ''),
            'created_at': datetime.now().isoformat()
        }
    elif role == 'teacher':
        teacher_name = data.get('teacher_name')
        if not teacher_name:
            return jsonify({"error": "Teacher name is required"}), 400
            
        new_user = {
            'teacher_id': user_id,
            'teacher_name': teacher_name,
            'email': email,
            'password': password,  # In production, use password hashing
            'subject': data.get('subject', ''),
            'created_at': datetime.now().isoformat()
        }
    else:
        return jsonify({"error": "Invalid role"}), 400
    
    # Add new user to the list
    users.append(new_user)
    
    # Save updated users list
    if save_users(users, role):
        # Generate personalized recommendations
        recommendations = generate_profile_recommendations(new_user, role)
        
        return jsonify({
            "message": f"{role.capitalize()} registered successfully",
            "user_id": user_id,
            "recommendations": recommendations
        }), 201
    else:
        return jsonify({"error": "Failed to register user"}), 500

@rg.route('/testing', methods=['GET'])
def testing():
    return 'Registration service is running!'