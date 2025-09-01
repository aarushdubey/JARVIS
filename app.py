# --- The Final, Fully-Featured Jarvis Web Backend ---

from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import json
import datetime
import geocoder
import requests

# --- MEMORY CLASS (From your desktop application) ---
class Memory:
    def __init__(self, memory_file="jarvis_memory.json", facts_file="jarvis_facts.json", knowledge_file="local_knowledge.json", biography_file="jarvis_biography.json"):
        self.memory_file = memory_file
        self.facts_file = facts_file
        self.knowledge_file = knowledge_file
        self.biography_file = biography_file
        
        self.conversation_history = self.load_json(self.memory_file, default=[])
        self.facts = self.load_json(self.facts_file, default={})
        self.local_knowledge = self.load_json(self.knowledge_file, default={})
        self.biography = self.load_json(self.biography_file, default={})
        self.qa_cache = self._build_qa_cache()

    def load_json(self, file_path, default):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try: return json.load(f)
                except json.JSONDecodeError: return default
        return default

    def save(self):
        # On a server, saving files might be temporary depending on the host (Render's free tier has a temporary filesystem)
        try:
            with open(self.memory_file, 'w') as f: json.dump(self.conversation_history, f, indent=2)
            with open(self.facts_file, 'w') as f: json.dump(self.facts, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory files. {e}")


    def add_to_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
        if role == 'model' and len(self.conversation_history) > 1:
            self.qa_cache[self.conversation_history[-2]['content'].lower()] = content
        self.save()

    def _build_qa_cache(self):
        cache = {}
        for i in range(len(self.conversation_history) - 1):
            if self.conversation_history[i]['role'] == 'user' and self.conversation_history[i+1]['role'] == 'model':
                cache[self.conversation_history[i]['content'].lower()] = self.conversation_history[i+1]['content']
        return cache

    def remember_fact(self, key, value):
        self.facts[key] = value
        self.save()

    def get_fact(self, key):
        return self.facts.get(key)

    def get_context(self):
        system_prompt = (
            f"You are Jarvis, a helpful AI assistant for a user named Aarush. "
            f"Use the following information to answer his questions directly and naturally. "
            f"Do not be overly formal or talk about privacy unless asked.\n\n"
            f"--- Static Biography ---\n{json.dumps(self.biography, indent=2)}\n"
            f"--- Facts You Have Learned ---\n{json.dumps(self.facts, indent=2)}"
        )
        messages = [{"role": "system", "content": system_prompt}]
        for item in self.conversation_history[-6:]: # Get the last 3 user/assistant turns
            role = 'model' if item.get('role') == 'assistant' else 'user'
            messages.append({"role": role, "parts": [item.get('content', '')]})
        return messages
    def get_gemini_history(self):
        """Converts local history to Gemini's format."""
        gemini_history = []
        for item in self.conversation_history[-10:]: # Limit history size
            # Gemini uses 'model' for the assistant role
            role = 'model' if item.get('role') == 'assistant' else 'user'
            gemini_history.append({'role': role, 'parts': [item.get('content', '')]})
        return gemini_history

# --- Flask App and Memory Initialization ---
app = Flask(__name__, template_folder='templates')
memory = Memory()

# --- Gemini Model Initialization ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not found.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
    chat_session = model.start_chat(history=memory.get_gemini_history())
    print("Gemini model initialized successfully.")
except Exception as e:
    print(f"FATAL: Error initializing Gemini: {e}")
    chat_session = None

# --- Web-Compatible Helper Functions ---
def fetch_weather():
    # Note: This gets the server's location (e.g., a Render data center)
    location = geocoder.ip("me").latlng
    if location:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key: return "Sorry, the weather service is not configured."
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location[0]},{location[1]}&aqi=no"
        try:
            data = requests.get(url, timeout=10).json()
            return f"The weather is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."
        except: return "Sorry, I couldn't get the weather."
    return "Sorry, I couldn't detect the location."

# --- Main API Endpoints ---
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_command = request.json.get("message", "")
    if not user_command:
        return jsonify({"reply": "I didn't receive a command."})

    memory.add_to_history("user", user_command)
    cmd_lower = user_command.lower()
    response_text = None

    # PRIORITY 1: Check for instant replies
    if cmd_lower in memory.local_knowledge:
        response_text = memory.local_knowledge[cmd_lower]
        if response_text == "get_time": response_text = f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."
        elif response_text == "get_date": response_text = f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}."
    elif cmd_lower in memory.qa_cache:
        response_text = memory.qa_cache[cmd_lower]

    # PRIORITY 2: Check for hard-coded web commands
    if response_text is None:
        if "weather" in cmd_lower:
            response_text = fetch_weather()
        elif cmd_lower.startswith("search for"):
            query = user_command[len("search for"):].strip()
            # We can't open a browser, but we can provide the link
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            response_text = f"Here is a search link for '{query}': {search_url}"
        # All other local commands (open app, bluetooth, etc.) are ignored on the web server.

    # PRIORITY 3: Fallback to Gemini API
    if response_text is None:
        if not chat_session:
            response_text = "The AI model is not initialized. Please check the server logs."
        else:
            try:
                # The history is already part of the session, just send the new message
                response = chat_session.send_message(user_command)
                response_text = response.text.strip()
            except Exception as e:
                print(f"Error communicating with Gemini API: {e}")
                response_text = "I'm sorry, I encountered an error with the AI."
    
    memory.add_to_history("model", response_text)
    return jsonify({"reply": response_text})

if __name__ == '__main__':
    # This runs the app locally for testing
    app.run(debug=True, port=5000)