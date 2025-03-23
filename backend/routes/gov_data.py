import uuid
import requests
import base64
import io
import os
import json
from flask import Blueprint, request, jsonify
from aixplain.client import AIXplainClient

gov_data = Blueprint('gov_data', __name__, url_prefix='/gov_data')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# UDISE Configuration
UDISE_BASE_URL = "https://src.udiseplus.gov.in/reportCardByApi/PdfReportUdiseCdApi"
CLIENT_ID = "gis"
CLIENT_KEY = "gis"

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def save_pdf_locally(udise_code, pdf_data):
    """Saves the PDF file locally."""
    file_path = os.path.join(REPORTS_DIR, f"{udise_code}.pdf")
    with open(file_path, 'wb') as file:
        file.write(pdf_data)
    return file_path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        return text
    except ImportError:
        return "PyMuPDF not installed. Please install with 'pip install pymupdf'"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_text_with_aixplain(text, analysis_type="enrollment"):
    """
    Analyze text with aiXplain based on analysis type.
    """
    try:
        if analysis_type == "enrollment":
            prompt = f"""
            Extract student enrollment information from the following text. 
            Focus on these categories: General (Gen), Scheduled Caste (SC), Scheduled Tribe (ST), 
            and Other Backward Class (OBC).
            
            For each category, provide the total number of students and the breakdown by boys (B) and girls (G).
            
            Format the response exactly like this:
            Gen: Total: [number], B: [number], G: [number]
            SC: Total: [number], B: [number], G: [number]
            ST: Total: [number], B: [number], G: [number]
            OBC: Total: [number], B: [number], G: [number]
            
            Here's the text:
            {text[:4000]}  # Limiting text length
            """
        elif analysis_type == "infrastructure":
            prompt = f"""
            Extract school infrastructure details from the following text. Focus on:
            
            1. Classrooms:
               - Total Classrooms
               - Classrooms in Good Condition
               - Classrooms Needing Minor Repair
               - Classrooms Needing Major Repair
            
            2. Toilets:
               - Total Toilets (for boys and girls)
               - Functional Toilets (for boys and girls)
               - CWSN Friendly Toilets (for boys and girls)
               - Urinals (for boys and girls)
            
            3. Other Rooms:
               - Library Availability
               - Separate Room for HM
            
            4. Digital Facilities:
               - ICT Lab
               - Laptops
               - Projectors
               - Internet
               - Desktops
               - DigiBoards
               - Printers
            
            Here's the text:
            {text[:4000]}  # Limiting text length
            """
        else:
            prompt = f"Provide a general analysis of this school report: {text[:3000]}"

        # Call aiXplain API
        response = client.run(
            model_id="aixplain-default-text-analysis",  # Replace with your actual model ID
            data=prompt,
            task="text-generation"
        )
        
        return response.get("output", "Analysis could not be generated.")
    except Exception as e:
        print(f"Error with aiXplain analysis: {e}")
        return f"Error during analysis: {str(e)}"

def parse_enrollment_data(analysis_text):
    """
    Parse enrollment data from the aiXplain analysis text.
    """
    import re
    
    enrollment_data = {}
    pattern = r"(\w+): Total: (\d+), B: (\d+), G: (\d+)"
    
    matches = re.findall(pattern, analysis_text)
    for match in matches:
        category = match[0]
        total = int(match[1])
        boys = int(match[2])
        girls = int(match[3])
        
        enrollment_data[category] = {
            "Total": total,
            "B": boys,
            "G": girls
        }
    
    return enrollment_data

def parse_infrastructure_data(analysis_text):
    """
    Parse infrastructure data from the aiXplain analysis text.
    """
    # Use simple line-by-line parsing as a backup to regex
    infrastructure_data = {
        "Classrooms": {},
        "Toilets": {},
        "OtherRooms": {},
        "DigitalFacilities": {}
    }
    
    # Process text line by line
    lines = analysis_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "Classrooms:" in line:
            current_section = "Classrooms"
        elif "Toilets:" in line:
            current_section = "Toilets"
        elif "Other Rooms:" in line or "Other Facilities:" in line:
            current_section = "OtherRooms"
        elif "Digital Facilities:" in line:
            current_section = "DigitalFacilities"
        elif current_section and ":" in line:
            # Parse key-value pairs
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip().strip('-').strip()
                value = parts[1].strip()
                
                if current_section == "Toilets" and ("B:" in value and "G:" in value):
                    # Handle toilet counts with B and G
                    b_match = re.search(r'B:\s*(\d+)', value)
                    g_match = re.search(r'G:\s*(\d+)', value)
                    
                    if b_match and g_match:
                        b_value = int(b_match.group(1))
                        g_value = int(g_match.group(1))
                        infrastructure_data[current_section][key] = {"B": b_value, "G": g_value}
                else:
                    # Try to convert to int if possible
                    try:
                        if value.isdigit():
                            value = int(value)
                    except:
                        pass
                    infrastructure_data[current_section][key] = value
    
    return infrastructure_data

@gov_data.route("/fetch_analyze", methods=["POST"])
def fetch_analyze():
    """
    Fetches UDISE data, saves PDF locally, and analyzes it with aiXplain.
    """
    try:
        # Step 1: Extract UDISE code from the request
        data = request.json
        udise_code = data.get("udiseCode")
        if not udise_code:
            return jsonify({"error": "UDISE code is required"}), 400

        # Step 2: Fetch UDISE PDF
        payload = {"udiseCode": udise_code, "clientId": CLIENT_ID, "clientKey": CLIENT_KEY}
        udise_response = requests.post(UDISE_BASE_URL, json=payload)
        if udise_response.status_code != 200:
            return jsonify({"error": f"Failed to fetch PDF. Status code: {udise_response.status_code}"}), 500

        udise_data = udise_response.json()
        if not udise_data.get("responseData"):
            return jsonify({"error": "No data in response from UDISE"}), 500

        pdf_data = base64.b64decode(udise_data["responseData"])

        # Step 3: Save PDF locally
        pdf_path = save_pdf_locally(udise_code, pdf_data)
        
        # Step 4: Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        
        # Step 5: Analyze the text using aiXplain
        enrollment_analysis = analyze_text_with_aixplain(pdf_text, "enrollment")
        infrastructure_analysis = analyze_text_with_aixplain(pdf_text, "infrastructure")
        
        # Step 6: Parse the analysis results
        enrollment_data = parse_enrollment_data(enrollment_analysis)
        infrastructure_data = parse_infrastructure_data(infrastructure_analysis)
        
        # Step 7: Save the analysis results
        analysis_data = {
            "udise_code": udise_code,
            "pdf_path": pdf_path,
            "enrollment_data": enrollment_data,
            "infrastructure_data": infrastructure_data,
            "raw_enrollment_analysis": enrollment_analysis,
            "raw_infrastructure_analysis": infrastructure_analysis
        }
        
        analysis_path = os.path.join(DATA_DIR, f"analysis_{udise_code}.json")
        with open(analysis_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        # Step 8: Return the results
        return jsonify({
            "udise_code": udise_code,
            "pdf_path": pdf_path,
            "enrollment_data": enrollment_data,
            "infrastructure_data": infrastructure_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gov_data.route("/get_analysis/<udise_code>", methods=["GET"])
def get_analysis(udise_code):
    """
    Retrieves previously saved analysis for a UDISE code.
    """
    try:
        analysis_path = os.path.join(DATA_DIR, f"analysis_{udise_code}.json")
        if not os.path.exists(analysis_path):
            return jsonify({"error": "Analysis not found for this UDISE code"}), 404
            
        with open(analysis_path, 'r') as f:
            analysis_data = json.load(f)
            
        return jsonify(analysis_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500