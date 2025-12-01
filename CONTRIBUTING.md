# Contributing to JARVIS

First off, thank you for considering contributing to JARVIS! It's people like you that make JARVIS such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your environment details** (OS, Python version, Flask version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the styleguides
* End all files with a newline
* Avoid platform-dependent code

## Styleguides

### Python Code Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
* Use meaningful variable and function names
* Add docstrings to functions and classes
* Keep lines under 88 characters (Black formatter style)
* Use type hints where possible

Example:
```python
def get_ai_response(user_message: str, max_tokens: int = 500) -> str:
    """
    Get response from Gemini AI API.
    
    Args:
        user_message: The user's input message
        max_tokens: Maximum tokens for the response
        
    Returns:
        The AI-generated response string
    """
    # Implementation here
    pass
```

### JavaScript Code Style

* Use ES6+ syntax
* Use camelCase for variable and function names
* Add comments for complex logic
* Avoid global variables
* Keep functions focused and single-purpose

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` for improvements to the format/structure of code
    * 🐛 `:bug:` for bug fixes
    * ✨ `:sparkles:` for new features
    * 📚 `:books:` for documentation
    * 🚀 `:rocket:` for performance improvements
    * 🧪 `:test_tube:` for tests
    * 🔧 `:wrench:` for configuration

### Markdown Style

* Use `#` for headings (not underlines)
* Use backticks for inline code
* Use triple backticks for code blocks
* Include a language identifier for syntax highlighting
* Leave blank lines between sections

## Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/JARVIS.git
cd JARVIS
```

3. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

4. Install development dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if available
```

5. Create a branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

6. Make your changes and test them

7. Commit your changes:
```bash
git add .
git commit -m "Your commit message"
```

8. Push to your fork:
```bash
git push origin feature/your-feature-name
```

9. Create a Pull Request

## Testing

* Test your changes locally before submitting a PR
* Ensure the application runs without errors
* Test the specific feature you've modified
* Consider edge cases and error scenarios

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good-first-issue` - Good for newcomers
* `help-wanted` - Extra attention is needed
* `question` - Further information is requested
* `wontfix` - This will not be worked on

## Community

* Discussions can happen on the [GitHub Discussions](https://github.com/aarushdubey/JARVIS/discussions)
* Issues are tracked on [GitHub Issues](https://github.com/aarushdubey/JARVIS/issues)

## Recognition

Contributors will be recognized in:
* The README.md file
* Release notes
* GitHub contributors page

## Questions?

Feel free to open an issue with the label `question` or start a discussion in the GitHub Discussions forum.

Thank you for contributing to JARVIS! 🎉
