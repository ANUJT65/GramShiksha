from collections import deque
from flask import Blueprint, request, jsonify
from aixplain.client import AIXplainClient
import os

ch = Blueprint('chat_bot', __name__, url_prefix='/chat_bot')

@ch.route('/testing', methods=['GET'])
def testing():
    return 'Testing Serve in running!'

# Set up aiXplain client
# You should set your aiXplain credentials in environment variables for security
AIXPLAIN_API_KEY = os.environ.get("AIXPLAIN_API_KEY")
client = AIXplainClient(api_key=AIXPLAIN_API_KEY)

context_history = deque()  # Keep track of the conversation history
transcription_text = ""  # Initialize transcription text

def set_transcription(text):
    """
    Set the transcription text that the chatbot will refer to when answering questions.
    """
    global transcription_text
    transcription_text = text

def is_relevant_query(query, context):
    """
    Check if the query is relevant to the provided context.
    """
    keywords = context.split()
    return any(keyword.lower() in query.lower() for keyword in keywords)

def generate_response(query, context_history=None, model_id="aixplain-default-chat-model"):
    """
    Generate a chatbot response related to the given paragraph using aiXplain.
    """
    context = transcription_text  # Use the full transcription text as context
    if context_history:
        context = " ".join(context_history) + " " + context  # Add past conversation context if available

    if not is_relevant_query(query, context):
        return "Sorry, I cannot respond to that as it seems unrelated or inappropriate."

    # Format the prompt for aiXplain
    prompt = f"Context: {context}\nQuery: {query}\nPlease respond based on the given context."
    
    # Call aiXplain API for text generation
    response = client.run(
        model_id=model_id,
        data=prompt,
        task="text-generation"
    )
    
    # Extract the response text from aiXplain's response format
    return response.get("output", "Sorry, I couldn't generate a response.")

def maintain_conversational_context(response, context_history, max_context_length=10):
    """
    Maintain conversational context by keeping track of the conversation history.
    """
    if len(context_history) >= max_context_length:
        context_history.popleft()  # Remove the oldest context if limit is reached
    context_history.append(response)  # Add the new response to context
    return context_history

@ch.route('/set_transcription', methods=['POST'])
def set_transcription_route():
    global transcription_text
    data = request.json
    transcription_text = data.get('transcription_text', "")
    if not transcription_text:
        return jsonify({"error": "No transcription text provided"}), 400
    return jsonify({"message": "Transcription text set successfully"})

@ch.route('/chat', methods=['POST'])
def chat():
    global context_history
    data = request.json
    user_input = data.get('query')
    
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Get the aiXplain response
    response = generate_response(user_input, context_history)
    context_history = maintain_conversational_context(response, context_history)  # Update history

    return jsonify({"response": response})