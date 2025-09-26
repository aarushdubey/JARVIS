# --- The Final, Fully-Featured Jarvis Web Backend (Corrected) ---

from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import json
import datetime
import geocoder
import requests
from urllib.parse import quote_plus

# --- MEMORY CLASS (Upgraded with RAG) ---
class Memory:
    def __init__(
        self,
        memory_file="jarvis_memory.json",
        facts_file="jarvis_facts.json",
        knowledge_file="local_knowledge.json",
        biography_file="jarvis_biography.json",
    ):
        self.memory_file = memory_file
        self.facts_file = facts_file
        self.knowledge_file = knowledge_file
        self.biography_file = biography_file

        # Ensure files exist with sensible defaults
        self.conversation_history = self.load_json(self.memory_file, default=[])
        self.facts = self.load_json(self.facts_file, default={})
        self.local_knowledge = self.load_json(self.knowledge_file, default={})
        self.biography = self.load_json(self.biography_file, default={})

        # Build derived structures
        self.unified_knowledge = self._build_unified_knowledge()
        self.qa_cache = self._build_qa_cache()

    def load_json(self, file_path, default):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return default
        return default

    def save(self):
        """
        Save conversation history, facts, local knowledge and biography.
        Non-fatal: prints a warning on error but does not crash.
        """
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            with open(self.facts_file, "w", encoding="utf-8") as f:
                json.dump(self.facts, f, indent=2, ensure_ascii=False)
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump(self.local_knowledge, f, indent=2, ensure_ascii=False)
            with open(self.biography_file, "w", encoding="utf-8") as f:
                json.dump(self.biography, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save memory files. {e}")

    def add_to_history(self, role, content):
        """
        role: 'user' or 'model'
        content: text content
        """
        if content is None:
            content = ""
        if role == "assistant":  # normalize invalid role
            role = "model"
        entry = {"role": role, "content": content}
        self.conversation_history.append(entry)

        # Update QA cache for repeated questions
        if role == "model" and len(self.conversation_history) > 1:
            prev = self.conversation_history[-2]
            if prev.get("role") == "user":
                user_question = prev.get("content", "").strip().lower()
                if user_question:
                    self.qa_cache[user_question] = content

        self.save()

    def _build_unified_knowledge(self):
        knowledge = []
        for key, value in self.facts.items():
            knowledge.append(f"A known fact about '{key}' is '{value}'.")
        for key, value in self.local_knowledge.items():
            knowledge.append(f"Local knowledge: when asked '{key}', Jarvis should reply '{value}'.")
        self._flatten_biography(self.biography, "biography", knowledge)
        print(f"Built unified knowledge base with {len(knowledge)} items.")
        return knowledge

    def _build_qa_cache(self):
        cache = {}
        for i in range(len(self.conversation_history) - 1):
            current_message = self.conversation_history[i]
            next_message = self.conversation_history[i + 1]
            if current_message.get("role") == "user" and next_message.get("role") in ["model", "assistant"]:
                question = current_message.get("content", "").strip().lower()
                answer = next_message.get("content", "")
                if question:
                    cache[question] = answer
        print(f"Built QA cache with {len(cache)} items.")
        return cache

    def _flatten_biography(self, data, path, knowledge_list):
        if isinstance(data, dict):
            for key, value in data.items():
                self._flatten_biography(value, f"{path}.{key}", knowledge_list)
        elif isinstance(data, list):
            if data:
                knowledge_list.append(f"The value for '{path}' is '{', '.join(map(str, data))}'.")
        elif data is not None:
            knowledge_list.append(f"The value for '{path}' is '{data}'.")

    def find_relevant_knowledge(self, query, top_k=3):
        if not query or not isinstance(query, str):
            return []
        query_words = set([w.strip() for w in query.lower().split() if w.strip()])
        if not query_words:
            return []
        scored_knowledge = []
        for snippet in self.unified_knowledge:
            snippet_words = set([w.strip() for w in snippet.lower().split() if w.strip()])
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
            "You are Jarvis, a helpful AI assistant for Aarush. "
            "Answer the user's current query concisely. Use the following "
            "contextually relevant information from your memory if it helps.\n\n"
            f"--- Relevant Context ---\n{knowledge_context}\n--------------------"
        )

        messages = []
        for item in self.conversation_history[-6:]:
            role = item.get("role")
            if role == "assistant":  # normalize invalid role
                role = "model"
            messages.append({"role": role, "parts": [item.get("content", "")]})

        final_context = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["Understood. I will act as Jarvis and use the provided context."]},
        ] + messages

        return final_context


# --- Flask App and Memory Initialization ---
app = Flask(__name__, template_folder="templates", static_folder="static")
memory = Memory()

# --- Gemini Model Initialization ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-pro-latest")
    print("Gemini model initialized successfully.")
except Exception as e:
    print(f"FATAL: Error initializing Gemini: {e}")
    model = None

# --- Web-Compatible Helper Functions ---
def fetch_weather():
    try:
        location = geocoder.ip("me").latlng
    except Exception as e:
        print(f"geocoder error: {e}")
        location = None

    if location and isinstance(location, (list, tuple)) and len(location) >= 2:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return "Sorry, the weather service is not configured."
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location[0]},{location[1]}&aqi=no"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            temp_c = data.get("current", {}).get("temp_c")
            condition = data.get("current", {}).get("condition", {}).get("text")
            if temp_c is not None and condition:
                return f"The weather is {temp_c}°C with {condition}."
            return "Couldn't parse weather data."
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {e}")
            return "Sorry, I couldn't get the weather."
    return "Sorry, I couldn't detect the location."

# --- Main API Endpoints ---
@app.route("/")
def serve_index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_command = payload.get("message", "")
    if not user_command:
        return jsonify({"reply": "I didn't receive a command."})

    memory.add_to_history("user", user_command)
    cmd_lower = user_command.strip().lower()
    response_text = None

    if cmd_lower in memory.local_knowledge:
        response_text = memory.local_knowledge[cmd_lower]
        if response_text == "get_time":
            response_text = f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."
        elif response_text == "get_date":
            response_text = f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}."
    elif cmd_lower in memory.qa_cache:
        response_text = memory.qa_cache[cmd_lower]

    if response_text is None:
        if "weather" in cmd_lower:
            response_text = fetch_weather()
        elif cmd_lower.startswith("search for"):
            query = user_command[len("search for"):].strip()
            if query:
                search_url = f"https://www.google.com/search?q={quote_plus(query)}"
                response_text = f"Here is a search link for '{query}': {search_url}"
            else:
                response_text = "Please provide a search query."

    if response_text is None:
        if not model:
            print("DEBUG: AI model is NOT initialized.")
            response_text = "The AI model is not initialized. Please check the server logs."
        else:
            try:
                messages = memory.get_context(user_command)
                print(f"DEBUG: Messages sent to Gemini: {messages}")
                response = model.generate_content(messages)
                response_text = getattr(response, "text", None) or getattr(response, "result", None) or str(response)
                if isinstance(response_text, (dict, list)):
                    response_text = json.dumps(response_text, ensure_ascii=False)
                response_text = str(response_text).strip()
                print(f"DEBUG: Gemini response received: {response_text}")
            except Exception as e:
                print(f"ERROR: Error communicating with Gemini API: {e}")
                response_text = "I'm sorry, I encountered an error with the AI."

    memory.add_to_history("model", response_text)
    return jsonify({"reply": response_text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
