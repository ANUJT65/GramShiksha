from flask import Blueprint, jsonify, request
import os
import json
from aixplain.client import AIXplainClient

doc_db = Blueprint('doc_db', __name__, url_prefix='/doc_db')

# Initialize aiXplain client
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
DOCUMENTS_FILE = os.path.join(DATA_DIR, 'documents.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def initialize_data_file():
    """Initialize the documents data file if it doesn't exist"""
    if not os.path.exists(DOCUMENTS_FILE):
        with open(DOCUMENTS_FILE, 'w') as f:
            json.dump([], f)

def get_all_documents():
    """Get all documents from the JSON file"""
    initialize_data_file()
    try:
        with open(DOCUMENTS_FILE, 'r') as f:
            documents = json.load(f)
        return documents
    except Exception as e:
        print(f"Error reading documents: {e}")
        return []

def get_document_by_id(document_id):
    """Get a specific document by ID"""
    all_documents = get_all_documents()
    for document in all_documents:
        if document.get('document_id') == document_id:
            return document
    return None

def analyze_with_aixplain(text, task_type="summarization"):
    """
    Use aiXplain to analyze document text
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

@doc_db.route('/documents', methods=['GET'])
def get_documents():
    """Get all documents with basic information"""
    try:
        documents = get_all_documents()
        result = []
        
        for doc in documents:
            result.append({
                'document_id': doc.get('document_id'),
                'file_name': doc.get('file_name'),
                'subject': doc.get('subject', ''),
                'lecture': doc.get('lecture', ''),
                'date': doc.get('date', ''),
                'created_at': doc.get('created_at', '')
            })
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@doc_db.route('/document/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID"""
    document = get_document_by_id(document_id)
    if document:
        return jsonify(document)
    return jsonify({"error": "Document not found"}), 404

@doc_db.route('/analyze/<document_id>/<analysis_type>', methods=['GET'])
def analyze_document(document_id, analysis_type):
    """
    Analyze document content using aiXplain
    analysis_type can be: summary, keywords, concepts
    """
    document = get_document_by_id(document_id)
    
    if not document or "transcript" not in document:
        return jsonify({"error": "Document or transcript not found"}), 404
    
    transcript = document["transcript"]
    
    if analysis_type == "summary":
        result = analyze_with_aixplain(transcript, "summarization")
    elif analysis_type == "keywords":
        prompt = f"Extract the key words and phrases from this document:\n\n{transcript[:2000]}"
        result = analyze_with_aixplain(prompt, "text-generation")
    elif analysis_type == "concepts":
        prompt = f"Extract and explain the main concepts from this document:\n\n{transcript[:2000]}"
        result = analyze_with_aixplain(prompt, "text-generation")
    else:
        return jsonify({"error": "Invalid analysis type"}), 400
    
    return jsonify({"result": result})

@doc_db.route('/search', methods=['POST'])
def search_documents():
    """Search documents based on content"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
            
        documents = get_all_documents()
        results = []
        
        for doc in documents:
            transcript = doc.get('transcript', '')
            if query.lower() in transcript.lower():
                results.append({
                    'document_id': doc.get('document_id'),
                    'file_name': doc.get('file_name'),
                    'subject': doc.get('subject', ''),
                    'lecture': doc.get('lecture', ''),
                    'date': doc.get('date', ''),
                    'created_at': doc.get('created_at', '')
                })
                
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500