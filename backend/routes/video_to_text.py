from flask import Blueprint, request, jsonify
import os
import json
import re
import uuid
import time
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
import tempfile
from aixplain.client import AIXplainClient

# Initialize Blueprint
vt = Blueprint('video_to_text', __name__, url_prefix='/video_to_text')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Data storage paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
VIDEOS_DIR = os.path.join(DATA_DIR, 'videos')
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, 'transcripts')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')
PDFS_DIR = os.path.join(DATA_DIR, 'pdfs')
MINDMAPS_DIR = os.path.join(DATA_DIR, 'mindmaps')
METADATA_FILE = os.path.join(DATA_DIR, 'video_metadata.json')

# Ensure directories exist
for directory in [DATA_DIR, VIDEOS_DIR, TRANSCRIPTS_DIR, IMAGES_DIR, PDFS_DIR, MINDMAPS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize metadata file if it doesn't exist
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, 'w') as f:
        json.dump([], f)

class AdvancedMarkdownPDF(FPDF):
    """PDF generator for markdown-style notes"""
    def __init__(self):
        super().__init__()
        self.header_font_sizes = {
            '#': 20,   # H1
            '##': 18,  # H2
            '###': 16, # H3
        }
        self.header_colors = {
            '#': (44, 62, 80),   # Dark Blue
            '##': (39, 174, 96), # Green
            '###': (52, 152, 219), # Blue
        }
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_left_margin(20)
        self.set_right_margin(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def render_markdown(self, text):
        lines = text.split('\n')
        for line in lines:
            # Match headings
            header_match = re.match(r'^(#+)\s*(.+)$', line)
            if header_match:
                # Add a separator before each section
                self.add_separator()

                header_level = header_match.group(1)
                header_text = header_match.group(2)
                font_size = self.header_font_sizes.get(header_level, 12)
                color = self.header_colors.get(header_level, (0, 0, 0))
                
                # Add background highlight for headers
                self.set_fill_color(230, 230, 230)  # Light gray background
                self.set_text_color(*color)
                self.set_font('Arial', style='B', size=font_size)
                self.cell(0, 12, header_text, ln=True, align='L', fill=True)
                self.line(20, self.get_y(), 190, self.get_y())  # Full-width underline
                self.ln(10)
                continue

            # Handle regular text
            line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            line = re.sub(r'\*(.+?)\*', r'\1', line)
            self.set_font('Arial', size=12)
            self.set_text_color(0)  # Black for body text
            self.multi_cell(0, 10, line)

    def add_separator(self):
        """Add a horizontal separator line for better visual appeal"""
        self.ln(5)
        self.set_draw_color(192, 192, 192)  # Light Grey
        self.line(20, self.get_y(), 190, self.get_y())  # Full-width line
        self.ln(5)

def save_metadata(metadata):
    """Save metadata to the JSON file"""
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving metadata: {e}")
        return False

def get_metadata():
    """Get all video metadata from the JSON file"""
    try:
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading metadata: {e}")
        return []

def save_file(file, directory):
    """Save a file to the specified directory and return the file path"""
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(directory, filename)
    file.save(file_path)
    return file_path, filename

def transcribe_video(file_path):
    """Transcribe a video using aiXplain"""
    try:
        print("Transcribing video...")
        
        # For a real implementation, you would upload the video to aiXplain
        # and use their transcription service
        
        # Simulating with a direct text generation request for now
        prompt = "Generate a transcript for this educational video. Since I can't actually analyze the video, please create a detailed placeholder transcript about a common educational topic."
        
        response = client.run(
            model_id="aixplain-default-text-generation",
            data=prompt,
            task="text-generation"
        )
        
        transcript = response.get("output", "")
        
        # Save transcript to file
        transcript_id = str(uuid.uuid4())
        transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{transcript_id}.txt")
        with open(transcript_path, 'w') as f:
            f.write(transcript)
            
        return {
            "transcript_id": transcript_id,
            "transcript": transcript,
            "transcript_path": transcript_path
        }
    except Exception as e:
        print(f"Error transcribing video: {e}")
        return None

def generate_mcqs(transcript, difficulty):
    """Generate multiple-choice questions using aiXplain"""
    try:
        print(f"Generating {difficulty} MCQs...")
        
        # Create prompt based on difficulty
        prompt = f"""
        Generate 5 {difficulty}-level multiple-choice questions based on the following transcript:
        
        {transcript[:3000]}  # Limit transcript length
        
        The output must be a valid JSON array. Each object in the array should have:
        - "question": The question text as a string.
        - "options": A list of 4 strings as possible answers.
        - "answer": A single string indicating the correct answer.
        
        Return only the JSON output without any extra text or explanations.
        """
        
        response = client.run(
            model_id="aixplain-default-text-generation",
            data=prompt,
            task="text-generation"
        )
        
        raw_response = response.get("output", "")
        
        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            try:
                mcqs = json.loads(json_content)
                return mcqs
            except json.JSONDecodeError:
                print("Error: The extracted content is not valid JSON.")
                return generate_fallback_mcqs(difficulty)
        else:
            print("Error: No JSON array found in the response.")
            return generate_fallback_mcqs(difficulty)
            
    except Exception as e:
        print(f"Error generating MCQs: {e}")
        return generate_fallback_mcqs(difficulty)

def generate_fallback_mcqs(difficulty):
    """Generate fallback MCQs if the AI generation fails"""
    return [
        {
            "question": f"Sample {difficulty} question 1?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A"
        },
        {
            "question": f"Sample {difficulty} question 2?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option B"
        }
    ]

def generate_notes(transcript, title):
    """Generate educational notes in PDF format using aiXplain"""
    try:
        print("Generating notes...")
        
        prompt = f"""
        Create an extensive and deeply analytical set of notes with the following requirements:
        
        Comprehensive Note Structure Guidelines:
        - Create 5 substantive sections with rich, descriptive headers
        - Each section must include:
          * A clear, thought-provoking main concept
          * Detailed explanatory text (2-3 paragraphs per section)
          * Key insights that go beyond surface-level information
        
        Specific Content Guidelines:
        1. Analyze key themes and concepts
        2. Explore implications and applications
        3. Highlight important details and examples
        4. Connect ideas across different sections
        
        Text to analyze:
        {transcript[:3000]}  # Limit transcript length
        
        Format your response in markdown with # for main headings and ## for subheadings.
        """
        
        response = client.run(
            model_id="aixplain-default-text-generation",
            data=prompt,
            task="text-generation"
        )
        
        notes_content = response.get("output", "")
        
        # Generate PDF from the notes content
        pdf = AdvancedMarkdownPDF()
        pdf.set_title(title)
        
        # Add title page
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(52, 73, 94)  # Midnight Blue
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(15)
        
        # Render the Markdown content
        pdf.render_markdown(notes_content)
        
        # Save PDF to file
        pdf_id = str(uuid.uuid4())
        pdf_path = os.path.join(PDFS_DIR, f"{pdf_id}.pdf")
        pdf_output = pdf.output(dest='S').encode('latin1')
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_output)
            
        return {
            "pdf_id": pdf_id,
            "pdf_path": pdf_path
        }
    except Exception as e:
        print(f"Error generating notes: {e}")
        return None

def generate_mindmap(transcript):
    """Generate a simple mind map SVG using aiXplain"""
    try:
        print("Generating mindmap...")
        
        # First, extract key concepts
        concepts_prompt = """
        Create a concise hierarchical outline with:
        - One main topic (3-4 words max)
        - Two primary subtopics (2-3 words each)
        - Two secondary points per primary topic (2-3 words each)
        
        Format as:
        MAIN: [topic]
        P1: [primary1]
        P2: [primary2]
        S1: [secondary1]
        S2: [secondary2]
        S3: [secondary3]
        S4: [secondary4]
        """
        
        response = client.run(
            model_id="aixplain-default-text-generation",
            data=f"{concepts_prompt}\n\nText: {transcript[:2000]}",
            task="text-generation"
        )
        
        concept_output = response.get("output", "")
        
        # Parse the concepts
        concepts = {'main': '', 'primary': [], 'secondary': []}
        for line in concept_output.strip().split('\n'):
            if line.startswith('MAIN:'):
                concepts['main'] = line.replace('MAIN:', '').strip()[:40]
            elif line.startswith('P'):
                concepts['primary'].append(line.split(':', 1)[1].strip()[:30])
            elif line.startswith('S'):
                concepts['secondary'].append(line.split(':', 1)[1].strip()[:25])
        
        # Ensure we have enough concepts
        if len(concepts['primary']) < 2:
            concepts['primary'].extend(["Primary Topic"] * (2 - len(concepts['primary'])))
        if len(concepts['secondary']) < 4:
            concepts['secondary'].extend(["Secondary Point"] * (4 - len(concepts['secondary'])))
        
        # Generate SVG
        svg_id = str(uuid.uuid4())
        svg_path = os.path.join(MINDMAPS_DIR, f"{svg_id}.svg")
        
        # Generate simple SVG mindmap
        colors = {
            'main': {'fill': '#e3f2fd', 'stroke': '#1565c0'},
            'primary': [
                {'fill': '#e8f5e9', 'stroke': '#2e7d32'},
                {'fill': '#fff3e0', 'stroke': '#ef6c00'}
            ],
            'secondary': [
                {'fill': '#f1f8e9', 'stroke': '#558b2f'},
                {'fill': '#fff8e1', 'stroke': '#ff8f00'},
                {'fill': '#f3e5f5', 'stroke': '#6a1b9a'},
                {'fill': '#e1f5fe', 'stroke': '#0288d1'}
            ]
        }
        
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">
    <style>
        rect {{ rx: 10; stroke-width: 2; }}
        text {{ font-family: Arial; font-size: 14px; text-anchor: middle; }}
    </style>
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
        </marker>
    </defs>
    
    <!-- Main Topic -->
    <rect x="400" y="50" width="200" height="60" fill="{colors['main']['fill']}" stroke="{colors['main']['stroke']}"/>
    <text x="500" y="85" text-anchor="middle" font-family="Arial" font-size="14">{concepts['main']}</text>

    <!-- Primary Topics -->
    <rect x="150" y="200" width="200" height="60" fill="{colors['primary'][0]['fill']}" stroke="{colors['primary'][0]['stroke']}"/>
    <text x="250" y="235" text-anchor="middle" font-family="Arial" font-size="14">{concepts['primary'][0]}</text>

    <rect x="650" y="200" width="200" height="60" fill="{colors['primary'][1]['fill']}" stroke="{colors['primary'][1]['stroke']}"/>
    <text x="750" y="235" text-anchor="middle" font-family="Arial" font-size="14">{concepts['primary'][1]}</text>

    <!-- Secondary Topics -->
    <rect x="50" y="350" width="180" height="60" fill="{colors['secondary'][0]['fill']}" stroke="{colors['secondary'][0]['stroke']}"/>
    <text x="140" y="385" text-anchor="middle" font-family="Arial" font-size="14">{concepts['secondary'][0]}</text>

    <rect x="270" y="350" width="180" height="60" fill="{colors['secondary'][1]['fill']}" stroke="{colors['secondary'][1]['stroke']}"/>
    <text x="360" y="385" text-anchor="middle" font-family="Arial" font-size="14">{concepts['secondary'][1]}</text>

    <rect x="550" y="350" width="180" height="60" fill="{colors['secondary'][2]['fill']}" stroke="{colors['secondary'][2]['stroke']}"/>
    <text x="640" y="385" text-anchor="middle" font-family="Arial" font-size="14">{concepts['secondary'][2]}</text>

    <rect x="770" y="350" width="180" height="60" fill="{colors['secondary'][3]['fill']}" stroke="{colors['secondary'][3]['stroke']}"/>
    <text x="860" y="385" text-anchor="middle" font-family="Arial" font-size="14">{concepts['secondary'][3]}</text>

    <!-- Connections -->
    <line x1="500" y1="110" x2="250" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="500" y1="110" x2="750" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="250" y1="260" x2="140" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="250" y1="260" x2="360" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="750" y1="260" x2="640" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
    <line x1="750" y1="260" x2="860" y2="350" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
</svg>"""
        
        with open(svg_path, 'w') as f:
            f.write(svg_content)
            
        return {
            "mindmap_id": svg_id,
            "mindmap_path": svg_path,
            "concepts": concepts
        }
    except Exception as e:
        print(f"Error generating mindmap: {e}")
        return None

def generate_keyword_images(transcript, num_keywords=5):
    """Generate educational keywords and placeholder image paths"""
    try:
        print("Generating keywords and image suggestions...")
        
        prompt = f"""
        From the following transcription, extract {num_keywords} distinct, educational keywords 
        that capture the core educational concepts. These keywords should be precise, 
        meaningful, and suitable for image search.
        
        Transcription: {transcript[:2000]}
        
        Please provide the keywords as a comma-separated list without any additional text.
        """
        
        response = client.run(
            model_id="aixplain-default-text-generation",
            data=prompt,
            task="text-generation"
        )
        
        keywords_raw = response.get("output", "")
        keywords = [keyword.strip() for keyword in keywords_raw.split(',')]
        keywords = keywords[:num_keywords]
        
        # In a real implementation, you would use these keywords to search for images
        # For now, we'll create placeholder image paths
        image_links = {}
        for keyword in keywords:
            image_id = str(uuid.uuid4())
            image_links[keyword] = f"/images/placeholder_{image_id}.jpg"
            
        return image_links
    except Exception as e:
        print(f"Error generating keywords: {e}")
        return {}

def process_video(file, lecture, subject, time_str, date_str):
    """Process a video file to extract various educational content"""
    try:
        # Generate a unique ID for this video
        video_id = str(uuid.uuid4())
        
        # Save the video file
        video_path, video_filename = save_file(file, VIDEOS_DIR)
        
        # Transcribe the video
        transcription_result = transcribe_video(video_path)
        if not transcription_result:
            return {"error": "Failed to transcribe video."}
            
        transcript = transcription_result["transcript"]
        transcript_path = transcription_result["transcript_path"]
        
        # Generate MCQs at different difficulty levels
        mcqs_easy = generate_mcqs(transcript, "easy")
        mcqs_medium = generate_mcqs(transcript, "medium")
        mcqs_hard = generate_mcqs(transcript, "hard")
        
        # Generate educational keyword images
        image_links = generate_keyword_images(transcript)
        
        # Generate mindmap
        mindmap_result = generate_mindmap(transcript)
        mindmap_path = mindmap_result["mindmap_path"] if mindmap_result else None
        
        # Generate notes
        notes_result = generate_notes(transcript, f"Notes on {lecture}")
        pdf_path = notes_result["pdf_path"] if notes_result else None
        
        # Create metadata entry
        metadata = get_metadata()
        metadata_entry = {
            "video_id": video_id,
            "video_filename": video_filename,
            "video_path": video_path,
            "transcript_path": transcript_path,
            "mindmap_path": mindmap_path,
            "pdf_path": pdf_path,
            "lecture": lecture,
            "subject": subject,
            "time": time_str,
            "date": date_str,
            "created_at": datetime.now().isoformat()
        }
        
        metadata.append(metadata_entry)
        save_metadata(metadata)
        
        # Prepare the response
        result = {
            "video_id": video_id,
            "transcript": transcript[:500] + "...",  # Truncate for response
            "mcqs_easy": mcqs_easy,
            "mcqs_medium": mcqs_medium,
            "mcqs_hard": mcqs_hard,
            "image_links": image_links,
            "mindmap_url": f"/mindmaps/{os.path.basename(mindmap_path)}" if mindmap_path else None,
            "notes_url": f"/pdfs/{os.path.basename(pdf_path)}" if pdf_path else None,
            "video_url": f"/videos/{video_filename}",
            "lecture": lecture,
            "subject": subject,
            "time": time_str,
            "date": date_str
        }
        
        return result
    except Exception as e:
        print(f"Error processing video: {e}")
        return {"error": str(e)}

@vt.route('/process', methods=['POST'])
def process_video_endpoint():
    """Endpoint to process a video file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        
        # Check if file has a name
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Get form data
        lecture = request.form.get('lecture', 'Unnamed Lecture')
        subject = request.form.get('subject', 'General')
        time_str = request.form.get('time', datetime.now().strftime('%H:%M'))
        date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Process the video
        result = process_video(file, lecture, subject, time_str, date_str)
        
        if "error" in result:
            return jsonify(result), 500
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vt.route('/videos', methods=['GET'])
def get_videos():
    """Endpoint to get all processed videos"""
    try:
        metadata = get_metadata()
        return jsonify({"videos": metadata}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vt.route('/video/<video_id>', methods=['GET'])
def get_video(video_id):
    """Endpoint to get a specific video's data"""
    try:
        metadata = get_metadata()
        video = next((v for v in metadata if v.get('video_id') == video_id), None)
        
        if not video:
            return jsonify({"error": "Video not found"}), 404
            
        return jsonify(video), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500