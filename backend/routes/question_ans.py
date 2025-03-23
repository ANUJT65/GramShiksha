from flask import Blueprint, request, jsonify
import os
import json
import uuid
from datetime import datetime
from aixplain.client import AIXplainClient

qa = Blueprint('question_ans', __name__, url_prefix='/qa')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
STUDENTS_DIR = os.path.join(DATA_DIR, 'students')
STUDENTS_FILE = os.path.join(STUDENTS_DIR, 'students.json')
TESTS_FILE = os.path.join(STUDENTS_DIR, 'tests.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STUDENTS_DIR, exist_ok=True)

def initialize_data_files():
    """Initialize data files if they don't exist"""
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(TESTS_FILE):
        with open(TESTS_FILE, 'w') as f:
            json.dump([], f)

def get_students():
    """Get all students from the JSON file"""
    initialize_data_files()
    try:
        with open(STUDENTS_FILE, 'r') as f:
            students = json.load(f)
        return students
    except Exception as e:
        print(f"Error reading students: {e}")
        return []

def get_student_by_email(email):
    """Get a student by email"""
    students = get_students()
    for student in students:
        if student.get('email') == email:
            return student
    return None

def save_students(students):
    """Save the list of students to the JSON file"""
    try:
        with open(STUDENTS_FILE, 'w') as f:
            json.dump(students, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving students: {e}")
        return False

def get_tests():
    """Get all tests from the JSON file"""
    initialize_data_files()
    try:
        with open(TESTS_FILE, 'r') as f:
            tests = json.load(f)
        return tests
    except Exception as e:
        print(f"Error reading tests: {e}")
        return []

def save_tests(tests):
    """Save the list of tests to the JSON file"""
    try:
        with open(TESTS_FILE, 'w') as f:
            json.dump(tests, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving tests: {e}")
        return False

def get_student_tests(student_id):
    """Get all tests for a specific student"""
    tests = get_tests()
    return [test for test in tests if test.get('student_id') == student_id]

def analyze_test_performance(student_id, video_id=None):
    """
    Use aiXplain to analyze test performance for a student
    """
    try:
        # Get student info
        students = get_students()
        student = next((s for s in students if s.get('student_id') == student_id), None)
        if not student:
            return "Student not found."
        
        # Get student tests
        tests = get_student_tests(student_id)
        
        # Filter tests by video_id if provided
        if video_id:
            tests = [test for test in tests if test.get('video_id') == video_id]
        
        if not tests:
            return "No test data available for analysis."
            
        # Calculate performance metrics
        total_questions = sum(test.get('correct_questions', 0) + test.get('wrong_questions', 0) for test in tests)
        correct_questions = sum(test.get('correct_questions', 0) for test in tests)
        
        if total_questions == 0:
            accuracy = 0
        else:
            accuracy = (correct_questions / total_questions) * 100
            
        # Format test data for analysis
        test_details = []
        for test in tests:
            test_details.append({
                "video_id": test.get('video_id'),
                "correct": test.get('correct_questions', 0),
                "wrong": test.get('wrong_questions', 0)
            })
            
        # Prepare data for aiXplain
        analysis_data = {
            "student_name": student.get('student_name', 'Unknown'),
            "grade": student.get('grade', 'Unknown'),
            "total_questions": total_questions,
            "correct_questions": correct_questions,
            "accuracy": accuracy,
            "test_details": test_details
        }
        
        # Create prompt for aiXplain
        prompt = f"""
        Analyze the following test performance data for a student:
        
        {json.dumps(analysis_data, indent=2)}
        
        Please provide:
        1. A summary of overall performance
        2. Strengths and areas for improvement
        3. Personalized recommendations for improving test scores
        
        Keep the analysis concise, constructive and encouraging.
        """
        
        # Call aiXplain API for analysis
        response = client.run(
            model_id="aixplain-default-text-analysis",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        return response.get("output", "Analysis could not be generated.")
    except Exception as e:
        print(f"Error analyzing test performance: {e}")
        return "Error occurred during analysis."

@qa.route('/testing', methods=['GET'])
def testing():
    return 'Testing Server is running!'

@qa.route('/add_test_result', methods=['POST'])
def add_test_result():
    data = request.get_json()
    email = data.get('email')
    video_id = data.get('video_id')
    correct_questions = data.get('correct_questions', 0)
    wrong_questions = data.get('wrong_questions', 0)

    if not email or not video_id:
        return jsonify({'error': 'email and video_id are required'}), 400

    try:
        # Get student by email
        student = get_student_by_email(email)
        if not student:
            return jsonify({'error': 'Email not found'}), 404
            
        student_id = student.get('student_id')
        
        # Get all tests
        tests = get_tests()
        
        # Find or create the test for this student and video
        test_exists = False
        for test in tests:
            if test.get('student_id') == student_id and test.get('video_id') == video_id:
                test['correct_questions'] = test.get('correct_questions', 0) + correct_questions
                test['wrong_questions'] = test.get('wrong_questions', 0) + wrong_questions
                test['updated_at'] = datetime.now().isoformat()
                test_exists = True
                current_test = test
                break
                
        if not test_exists:
            current_test = {
                'id': str(uuid.uuid4()),
                'student_id': student_id,
                'video_id': video_id,
                'correct_questions': correct_questions,
                'wrong_questions': wrong_questions,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tests.append(current_test)
            
        # Save tests
        save_tests(tests)
        
        # Get analysis
        analysis = analyze_test_performance(student_id, video_id)
        
        return jsonify({
            'message': 'Test results updated successfully',
            'video_results': {
                'correct_questions': current_test.get('correct_questions'),
                'wrong_questions': current_test.get('wrong_questions')
            },
            'analysis': analysis
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/get_results', methods=['GET'])
def get_results():
    email = request.args.get('email')
    video_id = request.args.get('video_id')
    
    if not email:
        return jsonify({'error': 'email is required'}), 400
        
    try:
        # Get student by email
        student = get_student_by_email(email)
        if not student:
            return jsonify({'error': 'Email not found'}), 404
            
        student_id = student.get('student_id')
        
        # Get student tests
        student_tests = get_student_tests(student_id)
        
        if video_id:
            # Find test for this video
            video_test = next((test for test in student_tests if test.get('video_id') == video_id), None)
            if not video_test:
                return jsonify({'error': 'Video ID not found'}), 404
            
            # Get analysis
            analysis = analyze_test_performance(student_id, video_id)
            
            return jsonify({
                'correct_questions': video_test.get('correct_questions', 0),
                'wrong_questions': video_test.get('wrong_questions', 0),
                'analysis': analysis
            }), 200
            
        # Calculate totals
        total_correct = sum(test.get('correct_questions', 0) for test in student_tests)
        total_wrong = sum(test.get('wrong_questions', 0) for test in student_tests)
        
        # Format tests for response
        formatted_tests = {}
        for test in student_tests:
            formatted_tests[test.get('video_id')] = {
                'correct_questions': test.get('correct_questions', 0),
                'wrong_questions': test.get('wrong_questions', 0)
            }
            
        # Get overall analysis
        analysis = analyze_test_performance(student_id)
        
        return jsonify({
            'total_results': {
                'correct_questions': total_correct,
                'wrong_questions': total_wrong
            },
            'tests': formatted_tests,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/reset_results', methods=['POST'])
def reset_results():
    data = request.get_json()
    email = data.get('email')
    video_id = data.get('video_id')
    
    if not email:
        return jsonify({'error': 'email is required'}), 400
        
    try:
        # Get student by email
        student = get_student_by_email(email)
        if not student:
            return jsonify({'error': 'Email not found'}), 404
            
        student_id = student.get('student_id')
        
        # Get all tests
        tests = get_tests()
        
        if video_id:
            # Remove or reset test for this video
            for i, test in enumerate(tests):
                if test.get('student_id') == student_id and test.get('video_id') == video_id:
                    tests[i] = {
                        'id': test.get('id'),
                        'student_id': student_id,
                        'video_id': video_id,
                        'correct_questions': 0,
                        'wrong_questions': 0,
                        'created_at': test.get('created_at'),
                        'updated_at': datetime.now().isoformat()
                    }
                    break
        else:
            # Remove all tests for this student
            tests = [test for test in tests if test.get('student_id') != student_id]
            
        # Save tests
        save_tests(tests)
        
        return jsonify({'message': 'Test results reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/initialize_test', methods=['POST'])
def initialize_test():
    data = request.get_json()
    email = data.get('email')
    video_id = data.get('video_id')
    
    if not email or not video_id:
        return jsonify({'error': 'email and video_id are required'}), 400
        
    try:
        # Get student by email
        student = get_student_by_email(email)
        if not student:
            return jsonify({'error': 'Email not found'}), 404
            
        student_id = student.get('student_id')
        
        # Get all tests
        tests = get_tests()
        
        # Check if test already exists
        for test in tests:
            if test.get('student_id') == student_id and test.get('video_id') == video_id:
                return jsonify({
                    'message': 'Test already initialized',
                    'video_results': {
                        'correct_questions': test.get('correct_questions', 0),
                        'wrong_questions': test.get('wrong_questions', 0)
                    }
                }), 200
                
        # Create new test
        new_test = {
            'id': str(uuid.uuid4()),
            'student_id': student_id,
            'video_id': video_id,
            'correct_questions': 0,
            'wrong_questions': 0,
            'questions': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        tests.append(new_test)
        
        # Save tests
        save_tests(tests)
        
        return jsonify({
            'message': 'Test initialized successfully',
            'video_results': {
                'correct_questions': 0,
                'wrong_questions': 0
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/get_all_students_results', methods=['GET'])
def get_all_students_results():
    try:
        # Get all students and tests
        students = get_students()
        tests = get_tests()
        
        students_results = []
        for student in students:
            student_id = student.get('student_id')
            
            # Get tests for this student
            student_tests = [test for test in tests if test.get('student_id') == student_id]
            
            # Calculate totals
            total_correct = sum(test.get('correct_questions', 0) for test in student_tests)
            total_wrong = sum(test.get('wrong_questions', 0) for test in student_tests)
            
            # Format tests
            formatted_tests = {}
            for test in student_tests:
                formatted_tests[test.get('video_id')] = {
                    'correct_questions': test.get('correct_questions', 0),
                    'wrong_questions': test.get('wrong_questions', 0)
                }
                
            # Create student data object
            student_data = {
                'student_id': student_id,
                'student_name': student.get('student_name', 'Unknown'),
                'email': student.get('email'),
                'total_results': {
                    'correct_questions': total_correct,
                    'wrong_questions': total_wrong
                },
                'tests': formatted_tests
            }
            
            students_results.append(student_data)
            
        return jsonify({
            'count': len(students_results),
            'students': students_results
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/update_question_result', methods=['POST'])
def update_question_result():
    data = request.get_json()
    email = data.get('email')
    video_id = data.get('video_id')
    question_serial = str(data.get('question_serial'))
    is_correct = data.get('is_correct')

    if not email or not video_id or question_serial is None or is_correct is None:
        return jsonify({'error': 'email, video_id, question_serial, and is_correct are required'}), 400

    try:
        # Get student by email
        student = get_student_by_email(email)
        if not student:
            return jsonify({'error': 'Email not found'}), 404
            
        student_id = student.get('student_id')
        
        # Get all tests
        tests = get_tests()
        
        # Find or create the test for this student and video
        test_exists = False
        for i, test in enumerate(tests):
            if test.get('student_id') == student_id and test.get('video_id') == video_id:
                if 'questions' not in test:
                    test['questions'] = {}
                    
                # Check if this question was already answered
                if question_serial in test['questions']:
                    old_answer = test['questions'][question_serial]
                    # If the old answer was correct, decrement correct count
                    if old_answer == '1':
                        test['correct_questions'] = max(0, test.get('correct_questions', 0) - 1)
                    # If the old answer was incorrect, decrement wrong count
                    elif old_answer == '0':
                        test['wrong_questions'] = max(0, test.get('wrong_questions', 0) - 1)
                        
                # Update question and counts
                test['questions'][question_serial] = '1' if is_correct else '0'
                if is_correct:
                    test['correct_questions'] = test.get('correct_questions', 0) + 1
                else:
                    test['wrong_questions'] = test.get('wrong_questions', 0) + 1
                    
                test['updated_at'] = datetime.now().isoformat()
                tests[i] = test
                current_test = test
                test_exists = True
                break
                
        if not test_exists:
            # Create new test with this question
            new_test = {
                'id': str(uuid.uuid4()),
                'student_id': student_id,
                'video_id': video_id,
                'correct_questions': 1 if is_correct else 0,
                'wrong_questions': 0 if is_correct else 1,
                'questions': {
                    question_serial: '1' if is_correct else '0'
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tests.append(new_test)
            current_test = new_test
            
        # Save tests
        save_tests(tests)
        
        # Get analysis with aiXplain
        analysis = analyze_test_performance(student_id, video_id)
        
        return jsonify({
            'message': 'Question result updated successfully',
            'video_results': {
                'questions': current_test.get('questions', {}),
                'correct_questions': current_test.get('correct_questions', 0),
                'wrong_questions': current_test.get('wrong_questions', 0)
            },
            'analysis': analysis
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/register_student', methods=['POST'])
def register_student():
    data = request.get_json()
    
    # Generate UUID if not provided
    if not data.get('student_id'):
        data['student_id'] = str(uuid.uuid4())
        
    required_fields = ['student_id', 'age', 'current_school', 'email', 
                      'family_income', 'grade', 'location', 'student_name', 'password']
                      
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # Get all students
        students = get_students()
        
        # Check if email already exists
        for student in students:
            if student.get('email') == data.get('email'):
                return jsonify({'error': 'Email already registered'}), 400
                
        # Create new student
        new_student = {
            'student_id': data.get('student_id'),
            'age': data.get('age'),
            'current_school': data.get('current_school'),
            'email': data.get('email'),
            'family_income': data.get('family_income'),
            'grade': data.get('grade'),
            'location': data.get('location'),
            'student_name': data.get('student_name'),
            'password': data.get('password'),  # In production, hash the password
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to students list
        students.append(new_student)
        
        # Save students
        save_students(students)
        
        return jsonify({'message': 'Student registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa.route('/get_student_details', methods=['GET'])
def get_student_details():
    email = request.args.get('email')
    
    if not email:
        return jsonify({'error': 'email is required'}), 400

    try:
        # Get student by email
        student = get_student_by_email(email)
        if not student:
            return jsonify({'error': 'Email not found'}), 404
            
        # Create response object (excluding password)
        student_data = {
            'student_id': student.get('student_id'),
            'age': student.get('age', 'Unknown'),
            'current_school': student.get('current_school', 'Unknown'),
            'email': student.get('email'),
            'family_income': student.get('family_income', 'Unknown'),
            'grade': student.get('grade', 'Unknown'),
            'location': student.get('location', 'Unknown'),
            'student_name': student.get('student_name', 'Unknown')
        }

        return jsonify(student_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500