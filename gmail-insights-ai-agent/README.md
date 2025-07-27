# Gmail Insights AI Agent 📧🧠

An intelligent AI agent that connects to Gmail, stores key partner communication insights in a structured GibsonAI database, and helps users recall, summarize, and act on conversations with context-aware memory.

![Gmail Insights AI Agent Demo](assets/demo.gif)

## 🌟 Features

- **📧 Gmail Integration**: Seamlessly connect to your Gmail account to analyze communications
- **🧠 Long-term Memory**: Store insights in GibsonAI database for weeks/months of conversation recall
- **🎯 Intelligent Analysis**: Extract key decisions, action items, topics, and sentiment from emails
- **👥 Relationship Management**: Track communication patterns and partner profiles
- **🔍 Context-Aware Recall**: Ask questions like "What did we last agree on with the CEO of OpenCore?"
- **📊 Streamlit UI**: User-friendly web interface for easy interaction
- **🔗 Session Persistence**: Maintain conversation context across multiple interactions

## 🏗️ Architecture

The agent is built using:
- **[Agno Framework](https://docs.agno.com/)**: AI agent framework with Gmail toolkit integration
- **[GibsonAI MCP Server](https://gibson.ai/)**: Durable database storage for communication insights
- **[Streamlit](https://streamlit.io/)**: Web-based user interface
- **SQLite**: Session storage for conversation persistence

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **Gibson CLI** installed and authenticated
3. **Gmail API credentials** from Google Cloud Console

### One-Command Setup

```bash
# Navigate to project and set up everything
cd gmail-insights-ai-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux (use venv\Scripts\activate on Windows)

# Install dependencies
pip install -e .

# Copy environment template
cp env.example .env

# Edit .env file with your credentials, then:
gibson auth login
streamlit run app.py
```

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd gmail-insights-ai-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Authenticate with Gibson:**
   ```bash
   gibson auth login
   ```

6. **Set up Gmail API credentials** (see [Gmail Setup](#gmail-setup) below)

7. **Run the Streamlit app (ensure virtual environment is active):**
   ```bash
   streamlit run app.py
   ```

## 📧 Gmail Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

### Step 2: Configure OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Note down your Client ID, Client Secret, and Project ID

### Step 3: Configure Environment

Update your `.env` file:
```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_PROJECT_ID=your_google_project_id_here
GOOGLE_REDIRECT_URI=http://localhost
```

### Step 4: First-time Authentication

The first time you run the agent, it will automatically handle Gmail authentication using the Agno Gmail toolkit.

## 🎯 Usage Examples

### Basic Queries

```python
# Analyze recent communications
"Analyze my recent emails from the past week and extract key business insights"

# Recall specific conversations
"What did we last agree on with the CEO of TechCorp?"

# Track action items
"Show me all pending action items from my business communications"

# Relationship summaries
"Summarize my communication history with john@example.com"

# Project-specific insights
"Find all emails discussing the Q1 project and summarize key decisions"
```

### Advanced Use Cases

#### 1. Partner Relationship Management
```python
"How often do I communicate with contacts from InnovateLabs? What's our relationship status?"
```

#### 2. Decision Tracking
```python
"What decisions were made in emails about the product launch timeline?"
```

#### 3. Follow-up Management
```python
"What follow-ups do I need to do based on emails from this month?"
```

#### 4. Communication Pattern Analysis
```python
"Show me communication trends with my top 5 business contacts"
```

## 🗄️ Data Models

The agent stores structured insights using these models:

### CommunicationInsight
- Email metadata (ID, thread, subject, participants)
- Content analysis (key topics, decisions, action items)
- Relationship context (company, role, importance)
- Temporal information (date, follow-up needs)

### PartnerProfile
- Contact information (email, name, company, role)
- Relationship status and interaction history
- Communication patterns and preferences
- Historical context and notes

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MODEL_API_KEY` | API key for your LLM provider | Yes |
| `MODEL_ID` | Model identifier (default: llama-3.3-70b-versatile) | No |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret | Yes |
| `GOOGLE_PROJECT_ID` | Google Cloud Project ID | Yes |
| `GOOGLE_REDIRECT_URI` | OAuth redirect URI (default: http://localhost) | No |

### Model Providers

The agent supports multiple LLM providers:
- **Groq** (default): Fast inference for Llama models
- **OpenAI**: GPT models and o1 series
- **Anthropic**: Claude models

## 🏃‍♂️ Running the Agent

**Note**: Always ensure your virtual environment is activated before running the agent:
```bash
# Activate virtual environment first
source venv/bin/activate  # On macOS/Linux
# or venv\Scripts\activate on Windows

# When done working, deactivate the environment:
# deactivate
```

### Streamlit Web Interface (Recommended)
```bash
streamlit run app.py
```

### Command Line Interface
```python
from agent import run_gmail_insights_agent

# Process a query
response = await run_gmail_insights_agent(
    "What did we discuss with TechCorp last week?"
)
print(response.content)
```

### Programmatic Usage
```python
import asyncio
from agent import run_gmail_insights_agent, setup_gibson_schema

async def main():
    # Set up database schema (run once)
    await setup_gibson_schema()
    
    # Process queries
    response = await run_gmail_insights_agent(
        message="Analyze my recent business emails",
        session_id="my_session_001"
    )
    
    print(response.content)

asyncio.run(main())
```

## 🛠️ Development

### Project Structure
```
gmail-insights-ai-agent/
├── agent.py              # Main agent implementation
├── app.py                # Streamlit web interface
├── llm_model.py          # Model provider configuration
├── pyproject.toml        # Project dependencies
├── env.example           # Environment template
├── README.md             # This file
└── tmp/                  # Session storage directory
```

### Key Components

1. **Agent Core** (`agent.py`):
   - Gmail toolkit integration
   - GibsonAI MCP server connection
   - Intelligent email analysis
   - Structured data extraction

2. **Web Interface** (`app.py`):
   - Streamlit-based UI
   - Real-time chat interface
   - Configuration management
   - Sample query suggestions

3. **Model Abstraction** (`llm_model.py`):
   - Multi-provider support
   - Automatic model selection
   - API key management

### Adding New Features

To extend the agent:

1. **Modify the agent instructions** in `agent.py`
2. **Add new data models** for additional insight types
3. **Extend the Streamlit UI** for new functionality
4. **Update the GibsonAI schema** for new data structures

## 🔍 Troubleshooting

### Common Issues

#### 0. Virtual Environment Issues
```
Error: Module not found or command not recognized
```
**Solution**: 
- Ensure virtual environment is activated: `source venv/bin/activate`
- Verify packages are installed in the virtual environment: `pip list`
- Reinstall dependencies if needed: `pip install -e .`

#### 1. Gmail Authentication Errors
```
Error: Gmail toolkit initialization failed
```
**Solution**: Ensure Gmail credentials are valid and token.json exists.

#### 2. GibsonAI Connection Issues
```
Error: MCP server timeout
```
**Solution**: 
- Run `gibson auth login` to authenticate
- Check internet connectivity
- Verify Gibson CLI installation

#### 3. Model API Errors
```
Error: MODEL_API_KEY environment variable is not set
```
**Solution**: Set your LLM provider API key in the `.env` file.

### Debug Mode

Enable detailed logging:
```env
LOG_LEVEL=DEBUG
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the [Agno documentation](https://docs.agno.com/)
- Review [GibsonAI documentation](https://gibson.ai/docs)

## 🙏 Acknowledgments

- [Agno Framework](https://docs.agno.com/) for the AI agent toolkit
- [GibsonAI](https://gibson.ai/) for durable database storage
- [Streamlit](https://streamlit.io/) for the web interface
- Gmail API for email integration
