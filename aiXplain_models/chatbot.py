from groq import Groq
from collections import deque
from aixplain.factories import ModelFactory

class ChatbotManager:
    def __init__(self):
        self.context_history = deque(maxlen=10)  # Keep track of the conversation history
        self.transcription_text = ""  # Initialize transcription text
        self.client = None  # Will be initialized with API key
    
    def initialize_client(self, api_key):
        """
        Initialize the Groq client with the provided API key.
        
        Parameters:
        - api_key (str): API key for Groq authentication
        
        Returns:
        - bool: True if initialization succeeded, False otherwise
        """
        try:
            self.client = Groq(api_key=api_key)
            return True
        except Exception as e:
            print(f"Failed to initialize client: {str(e)}")
            return False
    
    def set_transcription(self, text):
        """
        Set the transcription text that the chatbot will refer to when answering questions.
        
        Parameters:
        - text (str): Transcription text to be used as context
        """
        self.transcription_text = text
    
    def is_relevant_query(self, query, context):
        """
        Check if the query is relevant to the provided context.
        
        Parameters:
        - query (str): User's query/question
        - context (str): Context text to check relevance against
        
        Returns:
        - bool: True if query is relevant, False otherwise
        """
        keywords = context.split()
        return any(keyword.lower() in query.lower() for keyword in keywords)
    
    def generate_response(self, query, model="llama3-8b-8192"):
        """
        Generate a chatbot response related to the given context.
        
        Parameters:
        - query (str): User's query/question
        - model (str, optional): LLM model to use. Defaults to "llama3-8b-8192"
        
        Returns:
        - str: Generated response to the query
        """
        if not self.client:
            return "Error: Groq client not initialized. Please provide an API key."
            
        context = self.transcription_text  # Use the full transcription text as context
        if self.context_history:
            context = " ".join(self.context_history) + " " + context  # Add past conversation context
    
        if not self.is_relevant_query(query, context):
            return "Sorry, I cannot respond to that as it seems unrelated or inappropriate."
    
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": f"Context: {context} Query: {query}"}],
                model=model,
                stream=False,
            )
            response_text = response.choices[0].message.content
            self.maintain_conversational_context(response_text)  # Update history
            return response_text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def maintain_conversational_context(self, response):
        """
        Maintain conversational context by keeping track of the conversation history.
        
        Parameters:
        - response (str): Current response to add to context
        """
        self.context_history.append(response)  # Add the new response to context
    
    def clear_context(self):
        """Clear the conversation history"""
        self.context_history.clear()

# Example usage:
"""
# Create chatbot instance
chatbot = ChatbotManager()

# Initialize with API key
chatbot.initialize_client("your_api_key_here")  

# Set transcription text
chatbot.set_transcription("Your transcription text here that provides context for the conversation.")

# Generate response to a query
response = chatbot.generate_response("What does the transcription talk about?")
print(response)

# Clear conversation history if needed
chatbot.clear_context()
"""