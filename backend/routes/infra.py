from flask import Blueprint, request, jsonify
import os
import json
from aixplain.client import AIXplainClient

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Path to school data
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SCHOOLS_FILE = os.path.join(DATA_DIR, 'schools.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize the school recommendation blueprint
school_recommendation_bp = Blueprint('school_recommendation', __name__, url_prefix='/school_recommendation')

class School:
    def __init__(self, name, area, location, fees, classes, admission, type_, medium, facilities, transport):
        self.name = name
        self.area = area
        self.location = location
        self.fees = fees
        self.classes = classes
        self.admission = admission
        self.type = type_
        self.medium = medium
        self.facilities = facilities
        self.transport = transport
    
    def to_dict(self):
        return {
            "name": self.name,
            "area": self.area,
            "location": self.location,
            "fees": self.fees,
            "classes": self.classes,
            "admission": self.admission,
            "type": self.type,
            "medium": self.medium,
            "facilities": self.facilities,
            "transport": self.transport
        }

def initialize_schools_data():
    """Initialize the schools data file if it doesn't exist"""
    if not os.path.exists(SCHOOLS_FILE):
        # Define some default schools
        default_schools = [
            School("Little Flower High School", "Hadapsar", "Pune", 10000, "1st–10th", "Walk-in", "Private", "English", ["Sports", "Arts"], True),
            School("Hadapsar Government School", "Hadapsar", "Pune", 1000, "1st–8th", "Walk-in", "Government", "Marathi", ["Basic Facilities"], False),
            School("Blossoms International School", "Hadapsar", "Pune", 35000, "1st–12th", "Online/Walk-in", "Private", "English", ["Sports", "Labs", "Arts"], True),
            School("Sinhgad Academy", "Sinhagad Road", "Pune", 40000, "1st–12th", "Online/Walk-in", "Private", "English", ["Arts", "Labs", "Robotics"], True),
            School("Sinhgad Public School", "Sinhagad Road", "Pune", 5000, "1st–10th", "Walk-in", "Government", "Marathi", ["Basic Facilities"], False),
            School("Kothrud High School", "Kothrud", "Pune", 15000, "1st–8th", "Walk-in", "Private", "Marathi", ["Sports", "Arts"], False),
            School("Vidya Valley School", "Kothrud", "Pune", 50000, "1st–12th", "Online/Walk-in", "Private", "English", ["Labs", "Sports", "Arts"], True),
            School("Katraj English Medium School", "Katraj", "Pune", 25000, "1st–10th", "Walk-in", "Private", "English", ["Sports", "Labs"], True),
            School("New Horizon Public School", "Katraj", "Pune", 30000, "1st–12th", "Online/Walk-in", "Private", "English", ["Robotics", "Arts", "Labs"], True),
            School("Kondhwa Government School", "Kondhwa", "Pune", 1500, "1st–8th", "Walk-in", "Government", "Marathi", ["Basic Facilities"], False),
            School("St. Anne's High School", "Bibwewadi", "Pune", 20000, "1st–10th", "Walk-in", "Private", "English", ["Sports", "Arts"], True),
            School("Bibwewadi Government School", "Bibwewadi", "Pune", 1000, "1st–8th", "Walk-in", "Government", "Marathi", ["Basic Facilities"], False)
        ]
        
        # Convert to dictionaries
        schools_data = [school.to_dict() for school in default_schools]
        
        # Save to file
        with open(SCHOOLS_FILE, 'w') as f:
            json.dump(schools_data, f, indent=2)

def get_schools():
    """Get all schools from the JSON file"""
    initialize_schools_data()
    try:
        with open(SCHOOLS_FILE, 'r') as f:
            schools_data = json.load(f)
        return schools_data
    except Exception as e:
        print(f"Error reading schools data: {e}")
        return []

def recommend_schools_with_aixplain(user_preferences):
    """
    Use aiXplain to recommend schools based on user preferences
    """
    try:
        # Get the available schools
        schools_data = get_schools()
        
        # Format the user preferences and schools data for the AI
        preferences_str = json.dumps(user_preferences, indent=2)
        schools_str = json.dumps(schools_data, indent=2)
        
        prompt = f"""
        Given a user's preferences for a school and a list of available schools, recommend the top 2 schools that best match the user's criteria.

        USER PREFERENCES:
        {preferences_str}

        AVAILABLE SCHOOLS:
        {schools_str}

        For each recommended school, calculate a match percentage based on how well it fits the user's criteria.
        Consider these factors in your matching:
        1. Medium of instruction (perfect match gives higher score)
        2. Fees (school fees should be less than or equal to user's budget)
        3. Class/Grade availability
        4. Facilities (more matching facilities give higher score)
        5. Area proximity (closer areas give higher score)

        Provide your recommendations in this JSON format:
        [
          {{
            "name": "School Name",
            "area": "Area",
            "location": "Location",
            "fees": fee_amount,
            "classes": "Classes",
            "admission": "Admission Process",
            "type": "School Type",
            "medium": "Medium",
            "facilities": ["Facility1", "Facility2"],
            "transport": true_or_false,
            "match_percentage": percentage,
            "reasoning": "Brief explanation of why this school matches"
          }},
          {{
            "name": "Second School Name",
            ...
          }}
        ]

        Return only the JSON - no other text.
        """
        
        # Call aiXplain API for recommendation
        response = client.run(
            model_id="aixplain-default-text-generation",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        # Extract and parse the recommendations
        recommendation_text = response.get("output", "[]")
        # Clean the text to ensure it's valid JSON
        recommendation_text = recommendation_text.strip()
        if recommendation_text.startswith("```json"):
            recommendation_text = recommendation_text[7:]
        if recommendation_text.endswith("```"):
            recommendation_text = recommendation_text[:-3]
            
        recommendation_text = recommendation_text.strip()
        
        # Parse the JSON response
        try:
            recommendations = json.loads(recommendation_text)
            return recommendations
        except json.JSONDecodeError as e:
            print(f"Error parsing recommendations: {e}")
            print(f"Raw text: {recommendation_text}")
            return []
            
    except Exception as e:
        print(f"Error with aiXplain recommendation: {e}")
        return []

@school_recommendation_bp.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.get_json()
        
        if not user_input or 'current_area' not in user_input:
            return jsonify({"error": "Invalid or incomplete user preferences"}), 400
            
        recommendations = recommend_schools_with_aixplain(user_input)
        
        if recommendations:
            return jsonify(recommendations), 200
        else:
            # Fallback to simple filtering if AI recommendation fails
            schools_data = get_schools()
            filtered_schools = []
            
            for school in schools_data:
                if (school['location'].lower() == "pune" and
                    (not user_input.get('medium') or school['medium'].lower() == user_input['medium'].lower()) and
                    (not user_input.get('fees') or school['fees'] <= user_input['fees'])):
                    filtered_schools.append(school)
            
            if filtered_schools:
                return jsonify(filtered_schools[:2]), 200
            else:
                return jsonify({"error": "No matching schools found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@school_recommendation_bp.route('/schools', methods=['GET'])
def get_all_schools():
    """Get all available schools"""
    schools_data = get_schools()
    return jsonify(schools_data), 200

@school_recommendation_bp.route('/add_school', methods=['POST'])
def add_school():
    """Add a new school to the database"""
    try:
        school_data = request.get_json()
        
        required_fields = ['name', 'area', 'location', 'fees', 'classes', 
                          'admission', 'type', 'medium', 'facilities', 'transport']
        
        # Validate required fields
        for field in required_fields:
            if field not in school_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get existing schools
        schools_data = get_schools()
        
        # Add new school
        schools_data.append(school_data)
        
        # Save updated schools data
        with open(SCHOOLS_FILE, 'w') as f:
            json.dump(schools_data, f, indent=2)
            
        return jsonify({"message": "School added successfully", "school": school_data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500