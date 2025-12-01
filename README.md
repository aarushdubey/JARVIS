# JARVIS - AI-Powered Personal Assistant

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-2.3%2B-lightblue)](https://flask.palletsprojects.com/) [![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple)](https://ai.google.dev/) [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🤖 Overview

JARVIS is an intelligent personal assistant web application that combines **Flask**, **Google's Gemini AI**, and **persistent memory systems** to create a powerful conversational AI experience. Named after the AI assistant from Marvel's Iron Man universe, JARVIS brings advanced natural language processing to your browser with a sleek, responsive interface.

**Live Demo**: [jarvis-4aqq.onrender.com](https://jarvis-4aqq.onrender.com)

## ✨ Features

### Core Capabilities
- 🧠 **Advanced AI Conversations** - Powered by Google's Gemini API for intelligent, context-aware responses
- 💾 **Persistent Memory** - Maintains conversation history across sessions using SQLite database
- 🎨 **Responsive UI** - Modern, clean interface built with HTML5 and CSS3 for all devices
- ⚡ **Real-time Processing** - Fast API responses with optimized data handling
- 🔐 **Secure Operations** - Environment variable configuration for sensitive data
- 🌍 **Multi-platform** - Works seamlessly across desktop, tablet, and mobile browsers

### Technical Features
- RESTful API endpoints for clean data communication
- Session management and user state persistence
- Error handling and graceful degradation
- Optimized performance with caching strategies
- Comprehensive logging for debugging

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| **Backend** | Flask 2.3+ |
| **AI/ML** | Google Gemini API |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Deployment** | Render |
| **Language** | Python 3.9+ |
| **API Communication** | REST, JSON |

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.9 or higher** installed
- **pip** (Python package manager)
- **Git** for version control
- **Google Gemini API Key** ([Get it here](https://ai.google.dev/))
- A modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/aarushdubey/JARVIS.git
cd JARVIS
```

### 2. Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### 5. Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## 📖 Usage Guide

### Starting a Conversation
1. Navigate to `http://localhost:5000` in your web browser
2. Type your message in the input field
3. Press **Enter** or click **Send**
4. Wait for JARVIS to process and respond
5. Continue the conversation naturally

### Example Queries
```
- "What's the weather like?"
- "Tell me a joke"
- "Explain quantum computing"
- "Write a Python function to sort a list"
- "What are the top 5 machine learning algorithms?"
```

### Clearing History
- Click the **Clear History** button to start fresh
- Your conversation will begin anew

## 📁 Project Structure

```
JARVIS/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guidelines
├── CODE_OF_CONDUCT.md    # Community standards
├── LICENSE               # MIT License
├── templates/
│   ├── index.html        # Main UI template
│   └── base.html         # Base template (if used)
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Frontend logic
├── database/
│   └── jarvis.db         # SQLite database (auto-created)
└── logs/
    └── app.log           # Application logs
```

## 🔑 API Endpoints

### POST `/chat`
Send a message and receive a response
```json
Request:
{
  "message": "Your question or message"
}

Response:
{
  "response": "JARVIS's reply",
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET `/history`
Retrieve conversation history
```json
Response:
{
  "history": [
    {"role": "user", "content": "message", "timestamp": "..."},
    {"role": "assistant", "content": "response", "timestamp": "..."}
  ]
}
```

### POST `/clear`
Clear conversation history
```json
Response:
{
  "status": "success",
  "message": "History cleared"
}
```

## 🎯 Key Features Explained

### Persistent Memory System
- Stores all conversations in SQLite database
- Automatically retrieves context from previous sessions
- Maintains user preferences and settings

### Gemini AI Integration
- Leverages Google's state-of-the-art language model
- Supports diverse query types (creative, technical, analytical)
- Real-time token management for optimal performance

### Responsive Design
- Mobile-first approach
- Touch-friendly interface
- Adaptive layout for all screen sizes

## 🧪 Testing

```bash
# Run with debug mode enabled
python app.py --debug

# Check logs
tail -f logs/app.log
```

## 🚀 Deployment

### Deploy to Render

1. Push to GitHub repository
2. Create new Web Service on [Render.com](https://render.com)
3. Connect your GitHub repository
4. Set environment variables in Render dashboard
5. Deploy!

### Environment Variables Required
- `GEMINI_API_KEY` - Your Google Gemini API key
- `FLASK_ENV` - Set to "production"
- `SECRET_KEY` - A strong secret key for sessions

## 📈 Performance Optimization

- Request caching to reduce API calls
- Database indexing for faster queries
- CSS and JavaScript minification
- Lazy loading for image assets
- Efficient token management for AI API

## 🐛 Troubleshooting

### Common Issues

**Issue: "API Key not found"**
- Ensure `.env` file exists in project root
- Verify `GEMINI_API_KEY` is correctly set
- Restart the application

**Issue: "Database locked"**
- Close any other instances of the app
- Delete `database/jarvis.db` and restart

**Issue: Slow responses**
- Check internet connection
- Verify API quota hasn't been exceeded
- Review server logs for bottlenecks

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Arush Dubey**
- GitHub: [@aarushdubey](https://github.com/aarushdubey)
- Project: [JARVIS on GitHub](https://github.com/aarushdubey/JARVIS)

## 🙏 Acknowledgments

- Google Gemini API for powerful AI capabilities
- Flask framework for web development
- Render for reliable hosting
- The open-source community for inspiration and support

## 🗺️ Roadmap

### v1.1 (Upcoming)
- [ ] Voice input/output support
- [ ] User authentication system
- [ ] Conversation export (PDF/JSON)
- [ ] Dark mode toggle
- [ ] Multi-language support

### v1.2 (Future)
- [ ] Integration with additional APIs
- [ ] Advanced analytics dashboard
- [ ] Customizable AI personality
- [ ] Plugin/extension system

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/aarushdubey/JARVIS/issues)
- Start a [Discussion](https://github.com/aarushdubey/JARVIS/discussions)
- Contact via email (if available)

---

**⭐ If you find this project helpful, please consider giving it a star!**
