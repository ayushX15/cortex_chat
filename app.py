from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import os
import time
import threading
import concurrent.futures
from functools import lru_cache

app = Flask(__name__)

@lru_cache(maxsize=100)
def cached_generate_response(user_message):
    """Cached version of generate_response to improve speed for repeat queries"""
    return generate_response(user_message)

def generate_response(user_message):
    """
    Send a request to the local Ollama server to generate a response.
    
    Args:
        user_message (str): The user's message
        
    Returns:
        str: The model's response
    """
    try:
        # Ollama API endpoint for completion
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": "llama3:latest",
            "prompt": user_message,
            "stream": False,
            "num_predict": 512, 
            "temperature": 0.7, 
        }
        
        # Send request to Ollama
        response = requests.post(url, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            return data["response"].strip()
        else:
            return f"Error: Unable to get response from Ollama. Status code: {response.status_code}"
    
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


def preload_model():
    """Preload the model by sending a simple request"""
    try:
        generate_response("Hello")
        print("Model preloaded successfully")
    except Exception as e:
        print(f"Failed to preload model: {e}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Process chat messages and return AI responses
    
    Returns:
        JSON response with the AI's message
    """
    try:
        # Get message from request
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        start_time = time.time()
        response_text = cached_generate_response(user_message)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f}s for message: '{user_message[:30]}...'")
        
        # Return the response
        return jsonify({'response': response_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_frontend_file():
    """Create the updated frontend HTML file"""
    with open("index.html", "r") as f:
        html_content = f.read()
    
    if not os.path.exists('index.html') or html_content != open('index.html', 'r').read():
        with open("index.html", "w") as f:
            f.write(html_content)
        print("Created/updated index.html file")

if __name__ == '__main__':
    try:
        create_frontend_file()
    except Exception as e:
        print(f"Note: Could not verify index.html: {e}")
    
    threading.Thread(target=preload_model, daemon=True).start()
    
    # Start the server
    print("Starting server on http://localhost:5000")
    print("Make sure Ollama is running with llama3:latest model loaded")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)