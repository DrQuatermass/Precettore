# Precettore - AI Prompt Tutor

> *"Precettore"* (Italian for "Tutor") - An educational web application that teaches users how to write effective prompts for Large Language Models.

## 🎯 Overview

Precettore is not just another LLM chat interface. It's an **interactive learning environment** designed to help users master the art of prompt engineering through hands-on practice and expert guidance.

### What Makes Precettore Different?

Unlike traditional chatbots that simply execute your prompts, Precettore:
- **Analyzes** your prompts for common mistakes and anti-patterns
- **Engages** in a Socratic dialogue to understand your true goals
- **Teaches** you prompt engineering principles through practical examples
- **Refines** your prompts iteratively, explaining each improvement
- **Delivers** production-ready, optimized prompts for ChatGPT and other LLMs

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Precettore
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install django openai
```

4. **Setup database**
```bash
cd ai_tutor
python manage.py migrate
python manage.py createsuperuser  # Create admin account
```

5. **Configure API Key**
Edit `populate_data.py` and replace `SAMPLE_API_KEY` with your OpenAI API key:
```python
SAMPLE_API_KEY = "sk-your-actual-api-key-here"
```

6. **Populate initial data**
```bash
python populate_data.py
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main interface: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## 📚 How It Works

### The Tutoring Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER SUBMITS INITIAL PROMPT                             │
│    "Write me a story"                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TUTOR ANALYZES & IDENTIFIES ISSUES                      │
│    • Too vague (what kind of story?)                       │
│    • Missing constraints (length, style, audience)         │
│    • No clear objective                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TUTOR ASKS CLARIFYING QUESTIONS                         │
│    "What genre interests you? Who is the target audience?" │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. USER PROVIDES CONTEXT                                    │
│    "Sci-fi, teenagers, about 500 words"                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. TUTOR REFINES ITERATIVELY WITH EXPLANATIONS            │
│    • Adding role definition                                 │
│    • Specifying constraints                                 │
│    • Defining output format                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. FINAL OPTIMIZED PROMPT                                   │
│    "You are a creative sci-fi author specializing in YA... │
│     Write a 500-word story about..."                       │
└─────────────────────────────────────────────────────────────┘
```

### Educational Principles

#### 🎓 Non-Assertive Teaching
The tutor doesn't judge or criticize. Instead, it **highlights opportunities for improvement** and explains the reasoning behind each suggestion.

#### 💡 Socratic Method
Rather than giving immediate answers, the tutor **asks questions** to help you discover the best approach yourself.

#### 📖 Structured Learning
Every refinement follows established prompt engineering best practices:
1. **Role**: Define who the AI should act as
2. **Context**: Provide necessary background information
3. **Task**: State clear, specific objectives
4. **Constraints**: Set boundaries (length, format, style)
5. **Output Format**: Specify how results should be structured

#### 🔧 Tool Awareness
When appropriate, the tutor will suggest **alternative tools** that might be better suited to your task than an LLM.

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 5.x
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **LLM Integration**: OpenAI API (compatible with OpenAI-compatible endpoints)
- **Frontend**: Vanilla JavaScript with Server-Sent Events (SSE)

### Core Components

```
Precettore/
├── ai_tutor/              # Django project root
│   ├── ai_tutor/          # Project configuration
│   │   ├── settings.py    # Django settings
│   │   └── urls.py        # URL routing
│   ├── home/              # Main application
│   │   ├── models.py      # Data models (LLMConfiguration, ChatSession, ChatMessage)
│   │   ├── views.py       # API endpoints and logic
│   │   └── admin.py       # Django admin interface
│   ├── templates/         # HTML templates
│   │   └── homepage.html  # Main chat interface
│   ├── static/            # CSS and assets
│   │   └── style.css      # Application styles
│   └── populate_data.py   # Database initialization script
├── venv/                  # Virtual environment (not in repo)
├── CLAUDE.md              # Developer documentation
└── README.md              # This file
```

### Data Model

**LLMConfiguration**: Unified model containing provider, model, API key, system prompt, and parameters
- Supports multiple LLM providers (OpenAI, Anthropic, Google, custom)
- Configurable parameters (temperature, max_tokens, penalties)
- Specialized system_prompt for prompt tutoring

**ChatSession**: Tracks conversation sessions with UUID identifiers

**ChatMessage**: Stores message history with roles (user/assistant/system)

## 🎨 Customization

### Creating Custom Tutor Configurations

Access the Django admin panel at http://127.0.0.1:8000/admin/ to:
1. Create new LLM configurations with different teaching styles
2. Adjust temperature and other parameters for varied tutoring approaches
3. Modify the system_prompt to focus on specific prompt engineering aspects
4. Add additional context or guidelines

### Example: Creating a Technical Writing Tutor
```python
# In Django admin, create a new LLMConfiguration with:
name = "Technical Writing Tutor"
system_prompt = """You are an expert in technical documentation and API prompt design.
When users submit prompts for technical tasks, analyze them for:
- Specificity of technical requirements
- Proper use of technical constraints
- Format specifications for code/data
Guide them to create prompts that generate precise, actionable technical content."""
```

## 🔒 Security & Production

### Before Deploying to Production
1. **Change SECRET_KEY** in `settings.py`
2. **Set DEBUG = False** in `settings.py`
3. **Configure ALLOWED_HOSTS** with your domain
4. **Use environment variables** for API keys (not database storage)
5. **Consider encrypting** the `api_key` field in LLMConfiguration model
6. **Switch to PostgreSQL** or another production database
7. **Setup HTTPS** with proper certificates
8. **Configure CORS** if using frontend separately

## 📝 API Documentation

### POST `/api/llm`
Stream LLM responses with tutoring capabilities

**Request Body:**
```json
{
  "prompt": "Your initial prompt here",
  "configuration_id": 1,  // optional
  "session_id": "uuid-here"  // optional
}
```

**Response:** Server-Sent Events stream
```
data: {"content": "token"}

data: [DONE]
```

### GET `/api/configurations`
List available tutor configurations

### GET `/api/session/<session_id>/history`
Retrieve conversation history for a session

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional prompt engineering patterns and anti-patterns
- Support for more LLM providers
- Enhanced UI with prompt comparison views
- Export functionality for refined prompts
- User progress tracking and analytics

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with Django and powered by OpenAI's language models for educational purposes.

---

**Note**: This is an educational tool. Always review and test LLM-generated prompts before using them in production environments.
