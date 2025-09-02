# --- The Final, Fully-Featured Jarvis Web Backend ---

from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import json
import datetime
import geocoder
import requests

# --- MEMORY CLASS (Upgraded with RAG) ---
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
        
        self.unified_knowledge = self._build_unified_knowledge()
        self.qa_cache = self._build_qa_cache() # This line will now work correctly

    def load_json(self, file_path, default):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try: return json.load(f)
                except json.JSONDecodeError: return default
        return default

    def save(self):
        try:
            with open(self.memory_file, 'w') as f: json.dump(self.conversation_history, f, indent=2)
            with open(self.facts_file, 'w') as f: json.dump(self.facts, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory files. {e}")

    def add_to_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
        # Update the live cache when a new model response is generated
        if role == 'model' and len(self.conversation_history) > 1:
            # The previous entry should be the user's question
            user_question = self.conversation_history[-2]['content'].lower()
            self.qa_cache[user_question] = content
        self.save()

    def _build_unified_knowledge(self):
        knowledge = []
        for key, value in self.facts.items():
            knowledge.append(f"A known fact about '{key}' is '{value}'.")
        self._flatten_biography(self.biography, "biography", knowledge)
        print(f"Built unified knowledge base with {len(knowledge)} items.")
        return knowledge
    
    # --- FIXED CODE: ADD THIS METHOD ---
    def _build_qa_cache(self):
        """
        Builds a question-answer cache from the conversation history
        to provide instant answers to repeated questions.
        """
        cache = {}
        # Iterate through the history to find consecutive user-model pairs
        for i in range(len(self.conversation_history) - 1):
            # Check if current message is from user and the next is from the model
            current_message = self.conversation_history[i]
            next_message = self.conversation_history[i+1]
            if current_message.get('role') == 'user' and next_message.get('role') == 'model':
                question = current_message.get('content', '').lower()
                answer = next_message.get('content', '')
                if question: # Ensure the question is not empty
                    cache[question] = answer
        print(f"Built QA cache with {len(cache)} items.")
        return cache
    # ------------------------------------

    def _flatten_biography(self, data, path, knowledge_list):
        if isinstance(data, dict):
            for key, value in data.items():
                self._flatten_biography(value, f"{path}.{key}", knowledge_list)
        elif isinstance(data, list):
            knowledge_list.append(f"The value for '{path}' is '{', '.join(map(str, data))}'.")
        else:
            knowledge_list.append(f"The value for '{path}' is '{data}'.")

    def find_relevant_knowledge(self, query, top_k=3):
        query_words = set(query.lower().split())
        if not query_words: return []
        
        scored_knowledge = []
        for snippet in self.unified_knowledge:
            snippet_words = set(snippet.lower().split())
            common_words = query_words.intersection(snippet_words)
            if common_words:
                score = len(common_words)
                scored_knowledge.append((score, snippet))
        
        scored_knowledge.sort(key=lambda x: x[0], reverse=True)
        return [snippet for score, snippet in scored_knowledge[:top_k]]

    def get_context(self, current_command):
        relevant_knowledge = self.find_relevant_knowledge(current_command)
        knowledge_context = "\n".join(relevant_knowledge) if relevant_knowledge else "No specific context found in memory."

        system_prompt = (
            f"You are Jarvis, a helpful AI assistant for Aarush. "
            f"Answer the user's current query concisely. Use the following "
            f"contextually relevant information from your memory if it helps.\n\n"
            f"--- Relevant Context ---\n{knowledge_context}\n--------------------"
        )
        
        # Prepare messages for the Gemini API
        messages = []
        for item in self.conversation_history[-6:]: # Use last 6 items for recent context
            # The Gemini API expects 'parts' to be a list containing the content
            messages.append({"role": item.get('role'), "parts": [item.get('content', '')]})

        # Create a final context structure with the system prompt and history
        final_context = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["Understood. I will act as Jarvis and use the provided context."]}
        ] + messages

        return final_context

# --- Flask App and Memory Initialization ---
app = Flask(__name__, template_folder='templates', static_folder='static')
memory = Memory()

# --- Gemini Model Initialization ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
    print("Gemini model initialized successfully.")
except Exception as e:
    print(f"FATAL: Error initializing Gemini: {e}")
    model = None

# --- Web-Compatible Helper Functions ---
def fetch_weather():
    location = geocoder.ip("me").latlng
    if location:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key: return "Sorry, the weather service is not configured."
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location[0]},{location[1]}&aqi=no"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            return f"The weather is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {e}")
            return "Sorry, I couldn't get the weather."
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

    # PRIORITY 1: Instant replies from knowledge or cache
    if cmd_lower in memory.local_knowledge:
        response_text = memory.local_knowledge[cmd_lower]
        if response_text == "get_time": response_text = f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."
        elif response_text == "get_date": response_text = f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}."
    elif cmd_lower in memory.qa_cache:
        response_text = memory.qa_cache[cmd_lower]

    # PRIORITY 2: Hard-coded web commands
    if response_text is None:
        if "weather" in cmd_lower:
            response_text = fetch_weather()
        elif cmd_lower.startswith("search for"):
            query = user_command[len("search for"):].strip()
            # Basic URL encoding for the query
            from urllib.parse import quote_plus
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            response_text = f"Here is a search link for '{query}': {search_url}"
    
    # PRIORITY 3: Fallback to Gemini API with RAG context
    if response_text is None:
        if not model:
            response_text = "The AI model is not initialized. Please check the server logs."
        else:
            try:
                # Get the rich, relevant context for this specific command
                messages = memory.get_context(user_command)
                # Pass the history directly to the generate_content method
                response = model.generate_content(messages)
                response_text = response.text.strip()
            except Exception as e:
                print(f"Error communicating with Gemini API: {e}")
                response_text = "I'm sorry, I encountered an error with the AI."
    
    memory.add_to_history("model", response_text)
    return jsonify({"reply": response_text})

if __name__ == '__main__':
    # Use environment variable for port, defaulting to 5000 for local dev
    port = int(os.environ.get('PORT', 5000))
    # For production, use a proper WSGI server like Gunicorn, not app.run()
    # Gunicorn will be specified in your Render start command (e.g., gunicorn app:app)
    # The debug=True flag should be False in production
    app.run(host='0.0.0.0', port=port)