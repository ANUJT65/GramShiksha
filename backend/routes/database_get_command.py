from flask import Blueprint, jsonify
import os
import json
from aixplain.client import AIXplainClient

db = Blueprint('database_get_command', __name__, url_prefix='/db')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
VIDEOS_FILE = os.path.join(DATA_DIR, 'videos.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def initialize_data_file():
    """Initialize the videos data file if it doesn't exist"""
    if not os.path.exists(VIDEOS_FILE):
        with open(VIDEOS_FILE, 'w') as f:
            json.dump([], f)

def get_all_data():
    """Get all video data from the JSON file"""
    initialize_data_file()
    try:
        with open(VIDEOS_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading data: {e}")
        return []

def get_video_by_id(video_id):
    """Get a specific video by ID"""
    all_data = get_all_data()
    for video in all_data:
        if video.get('video_id') == video_id:
            return video
    return None

def get_field_by_video_id(video_id, field_name):
    """Get a specific field from a video by ID"""
    video = get_video_by_id(video_id)
    if video and field_name in video:
        return {field_name: video[field_name]}
    return {"error": "Item or field not found"}

def get_multiple_fields_by_video_id(video_id, fields):
    """Get multiple fields from a video by ID"""
    video = get_video_by_id(video_id)
    if not video:
        return {"error": "Item not found"}
    
    result = {}
    for field in fields:
        if field in video:
            result[field] = video[field]
    
    return result

def get_all_videos_basic_details():
    """Get basic details of all videos"""
    all_data = get_all_data()
    basic_details = []
    
    for video in all_data:
        basic_details.append({
            "video_id": video.get("video_id", ""),
            "lecture": video.get("lecture", ""),
            "subject": video.get("subject", ""),
            "time": video.get("time", ""),
            "video_url": video.get("video_url", "")
        })
    
    return basic_details

def analyze_with_aixplain(text, task_type="summarization"):
    """
    Use aiXplain to analyze text based on task type
    """
    try:
        response = client.run(
            model_id="aixplain-default-text-analysis",  # Replace with your actual model ID
            data=text,
            task=task_type
        )
        return response.get("output", "Analysis could not be generated.")
    except Exception as e:
        print(f"Error with aiXplain analysis: {e}")
        return "Error during analysis"

@db.route('/testing', methods=['GET'])
def testing():
    return 'Testing DB service!'

@db.route('/get_data', methods=['GET'])
def get_data():
    data = get_all_data()
    return jsonify(data)

@db.route('/get_mcqs_easy/<video_id>', methods=['GET'])
def get_mcqs_easy(video_id):
    data = get_field_by_video_id(video_id, "mcqs_easy")
    return jsonify(data)

@db.route('/get_mcqs_medium/<video_id>', methods=['GET'])
def get_mcqs_medium(video_id):
    data = get_field_by_video_id(video_id, "mcqs_medium")
    return jsonify(data)

@db.route('/get_mcqs_hard/<video_id>', methods=['GET'])
def get_mcqs_hard(video_id):
    data = get_field_by_video_id(video_id, "mcqs_hard")
    return jsonify(data)

@db.route('/get_video_details/<video_id>', methods=['GET'])
def get_video_details(video_id):
    data = get_multiple_fields_by_video_id(video_id, ["image_links", "mind_map", "notes", "video_url"])
    return jsonify(data)

@db.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    data = get_field_by_video_id(video_id, "transcript")
    return jsonify(data)

@db.route('/get_video_ids_and_urls', methods=['GET'])
def get_video_ids_and_urls():
    all_data = get_all_data()
    result = []
    for video in all_data:
        if "video_id" in video and "video_url" in video:
            result.append({
                "video_id": video["video_id"],
                "video_url": video["video_url"]
            })
    return jsonify(result)

@db.route('/get_all_videos_basic_details', methods=['GET'])
def all_videos_basic_details():
    data = get_all_videos_basic_details()
    return jsonify(data)

@db.route('/analyze/<video_id>/<analysis_type>', methods=['GET'])
def analyze_video_content(video_id, analysis_type):
    """
    Analyze video content using aiXplain
    analysis_type can be: summary, questions, concepts
    """
    video = get_video_by_id(video_id)
    
    if not video or "transcript" not in video:
        return jsonify({"error": "Video or transcript not found"}), 404
    
    transcript = video["transcript"]
    
    if analysis_type == "summary":
        result = analyze_with_aixplain(transcript, "summarization")
    elif analysis_type == "questions":
        prompt = f"Generate 5 quiz questions with answers based on this transcript:\n\n{transcript[:2000]}"
        result = analyze_with_aixplain(prompt, "text-generation")
    elif analysis_type == "concepts":
        prompt = f"Extract the key concepts from this transcript:\n\n{transcript[:2000]}"
        result = analyze_with_aixplain(prompt, "text-generation")
    else:
        return jsonify({"error": "Invalid analysis type"}), 400
    
    return jsonify({"result": result})