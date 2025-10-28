# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Precettore** (Italian for "Tutor") is a Django-based educational web application that helps users learn to write better prompts for Large Language Models.

### Core Mission
The application provides an **interactive, didactic experience** where an AI tutor:
1. Receives an initial prompt from the user
2. Analyzes the prompt for common mistakes (vagueness, lack of structure, unclear objectives)
3. Engages in a Socratic dialogue to understand the user's true intent and goals
4. Iteratively refines the prompt while explaining each improvement
5. Delivers a final, optimized prompt structured for ChatGPT/LLMs
6. Suggests alternative tools when LLMs are not the appropriate solution

### Educational Approach
- **Non-assertive**: Points out errors without being judgmental
- **Explanatory**: Each modification is explained with reasoning
- **Interactive**: Asks clarifying questions rather than making assumptions
- **Structured output**: Final prompts follow best practices (role, context, task, constraints, output format)

### Typical Workflow
1. **User submits initial prompt** → "Write me a story"
2. **Tutor analyzes issues** → Identifies vagueness (what kind of story? genre? length? audience?)
3. **Tutor asks clarifying questions** → Opens dialogue to understand intent
4. **User provides context** → "A sci-fi story for teenagers, about 500 words"
5. **Tutor refines iteratively** → Explains each improvement (adding role, specifying constraints, defining output format)
6. **Tutor delivers final prompt** → Optimized, structured prompt ready to use with ChatGPT

## Key Commands

### Environment Setup
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (if requirements.txt exists)
pip install django openai
```

### Database Operations
```bash
# Navigate to Django project
cd ai_tutor

# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Populate database with sample data
python populate_data.py
```

### Development Server
```bash
# Start development server (from ai_tutor directory)
python manage.py runserver

# Access:
# - Main interface: http://127.0.0.1:8000/
# - Admin panel: http://127.0.0.1:8000/admin/
```

### Django Management
```bash
# Create migrations after model changes
python manage.py makemigrations

# Open Django shell for testing
python manage.py shell

# Collect static files for production
python manage.py collectstatic
```

## Architecture

### Django Project Structure
- **Project root**: `ai_tutor/ai_tutor/` - Main Django configuration (settings, URLs)
- **App**: `ai_tutor/home/` - Core application logic
- **Templates**: `ai_tutor/templates/` - HTML templates
- **Static files**: `ai_tutor/static/` - CSS and client-side assets
- **Database**: SQLite (`db.sqlite3`) - Development database

### Data Model Architecture

The application uses a **simplified unified configuration system** with only 3 models:

1. **LLMConfiguration** → All-in-one: provider, model, API key, context, and parameters
2. **ChatSession** → User conversation sessions linked to a configuration
3. **ChatMessage** → Individual messages in sessions

### Key Models ([home/models.py](ai_tutor/home/models.py))

**LLMConfiguration** - Unified configuration containing everything needed for LLM requests:
- **Provider & Model**:
  - `provider` - Choice field: openai/anthropic/google/custom
  - `model_name` - Model identifier (e.g., gpt-4, claude-3-opus)
  - `api_key` - API key for authentication
  - `base_url` - Optional custom API endpoint
- **Context**:
  - `system_prompt` - Defines AI behavior
  - `additional_context` - Extra information, data, or knowledge
- **Common Parameters**:
  - `temperature` (0.0-2.0) - Creativity control
  - `max_tokens` (1-128000) - Response length limit
  - `top_p` (0.0-1.0) - Nucleus sampling
  - `frequency_penalty` (-2.0-2.0) - Repetition penalty (OpenAI)
  - `presence_penalty` (-2.0-2.0) - Topic introduction penalty (OpenAI)
- **Advanced**:
  - `model_parameters` - JSON field for provider-specific params (e.g., top_k, stop_sequences)
  - `stream`, `timeout`, `retry_attempts`
- **Key Methods**:
  - `get_full_context()` - Returns combined system_prompt + additional_context
  - `get_api_parameters()` - Returns dict of all API parameters (model-specific)
  - `get_client_config()` - Returns client configuration (api_key, base_url, timeout)
- **Flags**:
  - `is_active` - Enable/disable configuration
  - `is_default` - Only one can be default (enforced in save method)

**ChatSession**: Tracks conversations with `session_id` (UUID), links to `LLMConfiguration`

**ChatMessage**: Stores message history with `role` (user/assistant/system), `content`, `timestamp`, optional `tokens_used`

### API Endpoints ([ai_tutor/urls.py](ai_tutor/ai_tutor/urls.py))

- `GET /` - Main chat interface with configuration selector
- `POST /api/llm` - Streaming LLM API endpoint
  - Parameters: `prompt`, `configuration_id` (optional), `session_id` (optional)
  - Returns: Server-Sent Events (SSE) stream
- `GET /api/configurations` - List active configurations
- `GET /api/session/<session_id>/history` - Get conversation history

### Views Logic ([home/views.py](ai_tutor/home/views.py))

**LLM Request Flow**:
1. Receives POST with prompt, optional configuration_id and session_id
2. Selects configuration (specified, default, or first active)
3. Gets or creates ChatSession
4. Builds message array: system context (via `get_full_context()`) → conversation history → new user message
5. Gets API parameters via `get_api_parameters()` and client config via `get_client_config()`
6. Creates OpenAI client with configuration (supports custom base_url for compatible APIs)
7. Calls LLM API with streaming enabled
8. Saves both user message and assistant response to database
9. Returns SSE stream to client

**Important**: API keys are now stored in the database per configuration. For production, consider encrypting the `api_key` field or using environment variables.

### Frontend Architecture

The chat interface ([templates/homepage.html](ai_tutor/templates/homepage.html)) is a single-page application with vanilla JavaScript:
- Configuration selector dropdown (populated from Django context)
- Real-time streaming response handling via Fetch API
- Automatic session management (session_id tracked in JavaScript)
- Server-Sent Events (SSE) parsing for streaming responses
- CSRF token handling for Django security

### Admin Panel ([home/admin.py](ai_tutor/home/admin.py))

Comprehensive Django admin interface with organized fieldsets:
- **Informazioni Base**: name, description, is_active, is_default
- **Configurazione LLM e API**: provider, model_name, api_key, base_url
- **Contesto e Prompt**: system_prompt, additional_context
- **Parametri del Modello**: temperature, max_tokens, top_p, penalties
- **Parametri Avanzati**: model_parameters (JSON), stream, timeout, retry_attempts
- **Metadati**: created_by, created_at, updated_at
- Custom list displays with filters by provider, is_default, is_active
- Inline editing for ChatMessages within ChatSession
- Automatic created_by tracking for configurations

### Data Population

The [populate_data.py](ai_tutor/populate_data.py) script creates the specialized **Prompt Tutor** configuration with a system_prompt that:
- Analyzes user prompts for common issues (vagueness, lack of structure, unclear goals)
- Engages in Socratic dialogue to understand user intent
- Explains each refinement step with educational reasoning
- Identifies when LLMs are not the appropriate tool
- Delivers structured final prompts following best practices:
  - **Role**: Define who the AI should be
  - **Context**: Background information needed
  - **Task**: Clear, specific objective
  - **Constraints**: Limitations, format, length
  - **Output Format**: How the response should be structured

**Important**:
- Update the `SAMPLE_API_KEY` in populate_data.py before running
- The default configuration uses a specialized system_prompt for prompt optimization teaching
- Additional configurations can be created in the admin panel for different tutoring styles

## Important Implementation Notes

### Security Considerations
- **API Keys**: Stored in database per configuration - consider encrypting the `api_key` field for production
- **SECRET_KEY**: Development key in settings.py - must be changed for production
- **DEBUG**: Set to True in settings.py - must be False for production
- **ALLOWED_HOSTS**: Empty list - must be configured for production

### Unified Configuration System
- Only one configuration can have `is_default=True` (enforced in model save method with `exclude(pk=self.pk)`)
- Context is built via `get_full_context()` which combines `system_prompt` + `additional_context`
- Provider-specific parameters (e.g., `frequency_penalty` for OpenAI) are conditionally added in `get_api_parameters()`
- Custom parameters can be added via `model_parameters` JSON field (e.g., top_k, stop_sequences)
- All configurations are self-contained - no separate Provider, Model, or Context tables
- The `provider` field is informational; actual API compatibility is determined by the client library used (currently OpenAI SDK, which supports OpenAI-compatible APIs)

### Session Management
- Sessions are created with UUID4 identifiers
- Session ID is maintained client-side in JavaScript
- Message history is automatically included in context for each request
- Full conversation history is stored in database

### Streaming Implementation
- Uses Django's `StreamingHttpResponse` with Server-Sent Events
- Format: `data: {"content": "token"}\n\n`
- Ends with: `data: [DONE]\n\n`
- Client-side parsing handles incomplete chunks and JSON parsing errors
