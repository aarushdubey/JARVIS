# app.py
from flask import Flask, request, jsonify, send_from_directory
import os
import google.generativeai as genai

# --- IMPORTANT ---
# Copy your Memory class and any other helper functions (like fetch_weather) here.
# Make sure to remove any functions that won't work on a server,
# like open_application, close_application, toggle_bluetooth, etc.
# Example:
# class Memory:
#     # ... your full Memory class code ...

# Initialize Flask App
# This tells Flask where to find static files like your index.html
app = Flask(__name__, static_folder='static')


# --- AI and Memory Initialization ---
# It's best to initialize these once when the app starts.
# memory = Memory() 
# try:
#     api_key = os.getenv("GEMINI_API_KEY") # Make sure to set this in Render
#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel('gemini-1.5-flash-latest')
#     chat_session = model.start_chat(history=[]) # You can load history from memory here
#     print("Gemini Model Initialized.")
# except Exception as e:
#     print(f"ERROR: Could not initialize Gemini Model: {e}")
#     model = None
# ------------------------------------


## --- Frontend Route ---
# This function serves your main webpage (the user interface)
@app.route('/')
def serve_index():
    """Serves the index.html file from the static folder."""
    return send_from_directory(app.static_folder, 'index.html')


## --- Backend API Route ---
# This is the endpoint your JavaScript will send messages to
@app.route('/chat', methods=['POST'])
def chat():
    """Handles the chat logic by receiving a message and returning a response."""
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # --- This is where your core Jarvis logic goes ---
        # 1. Add user message to memory
        # memory.add_to_history("user", user_message)

        # 2. Check for local commands (like "weather") before calling the AI
        response_text = None
        if "weather" in user_message.lower():
            # response_text = fetch_weather() # If you implemented this
            pass # Placeholder
        
        # 3. If no local command, get a response from Gemini AI
        if response_text is None:
            # if model:
            #     response = chat_session.send_message(user_message)
            #     response_text = response.text
            # else:
            #     response_text = "Sorry, the AI model is not available right now."
            
            # For now, let's use a simple echo for testing
            response_text = f"Jarvis received: '{user_message}'"


        # 4. Add AI response to memory
        # memory.add_to_history("assistant", response_text)

        return jsonify({"reply": response_text})

    except Exception as e:
        print(f"An error occurred in the chat endpoint: {e}")
        return jsonify({"error": "Sorry, an internal error occurred."}), 500


# This allows you to run the app locally for testing
if __name__ == '__main__':
    app.run(debug=True, port=5001)
