from aixplain.factories import AgentFactory
from flask import Flask, request, jsonify
import os
import json

# Create the model tool and agent
model_tool = AgentFactory.create_model_tool(
    model="674b73f06eb563a748561d41",  # Gemini 1.5 Flash model ID
    description="Tool for generating questions and feedback from transcripts."
)

question_agent = AgentFactory.create(
    name="AI Avatar Agent",
    description="Generates questions and feedback for educational content.",
    instructions="""
    This agent generates single questions or provides feedback based on input.
    For questions: Generate only one simple, unique question related to the input transcript.
    For feedback: Provide a single line of feedback for the given answer.
    """,
    tools=[model_tool]
)

def generate_questions(transcript):
    prompt = f"Generate only one simple question related to {transcript}. There should be variety in questions."
    
    result = question_agent.run({
        "query": prompt,
        "temperature": 0.7,
        "max_tokens": 500,
        "max_iterations": 3,
        "request_timeout": 60
    })
    
    return result["data"]["output"].strip()

def get_feedback_from_gemini(answer):
    prompt = f"Provide small feedback in one line on the following test answer: {answer}."
    
    result = question_agent.run({
        "query": prompt,
        "temperature": 0.7,
        "max_tokens": 500,
        "max_iterations": 3,
        "request_timeout": 60
    })
    
    return result["data"]["output"].strip()

generate_questions("C is a powerful, general-purpose programming language developed by Dennis Ritchie in 1972 at Bell Labs. It is widely used for system programming, embedded systems, and application development due to its efficiency and control over hardware. C provides low-level memory access, a simple syntax, and high performance, making it the foundation for many modern programming languages like C++, Java, and Python. The language follows a structured programming approach and supports functions, loops, and pointers, allowing developers to write efficient and portable code. C remains a fundamental language in computer science education and software development.")
get_feedback_from_gemini("I don't know the answer to this")
