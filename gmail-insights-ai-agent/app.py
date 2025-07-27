import asyncio
import os
import streamlit as st
from datetime import datetime, timedelta
import json
from typing import Dict, Any

# Import the agent
from agent import run_gmail_insights_agent, setup_gibson_schema

# Page configuration
st.set_page_config(
    page_title="Gmail Insights AI Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .insight-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .action-item {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #ffc107;
        margin: 0.5rem 0;
    }
    .decision-item {
        background-color: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #17a2b8;
        margin: 0.5rem 0;
    }
    .sidebar-info {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = (
            f"gmail_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    if "schema_setup" not in st.session_state:
        st.session_state.schema_setup = False


async def setup_schema_if_needed():
    """Set up database schema if not already done"""
    if not st.session_state.schema_setup:
        with st.spinner("Setting up database schema..."):
            try:
                await setup_gibson_schema()
                st.session_state.schema_setup = True
                st.success("Database schema setup completed!")
            except Exception as e:
                st.error(f"Failed to set up database schema: {e}")
                return False
    return True


async def process_query(query: str) -> str:
    """Process user query through the Gmail Insights agent"""
    try:
        response = await run_gmail_insights_agent(
            message=query, session_id=st.session_state.session_id
        )
        return response.content
    except Exception as e:
        return f"Error processing query: {str(e)}"


def display_message(message: Dict[str, Any]):
    """Display a chat message"""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def main():
    """Main Streamlit application"""
    init_session_state()

    # Header
    st.markdown(
        '<h1 class="main-header">📧 Gmail Insights AI Agent</h1>',
        unsafe_allow_html=True,
    )
    st.markdown("**Intelligent partner communication memory powered by GibsonAI**")

    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")

        # Environment check
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.subheader("📋 Environment Status")

        # Check required environment variables
        env_checks = {
            "MODEL_API_KEY": os.getenv("MODEL_API_KEY") is not None,
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID") is not None,
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET") is not None,
            "GOOGLE_PROJECT_ID": os.getenv("GOOGLE_PROJECT_ID") is not None,
            "Gibson CLI": True,  # Assume available if agent loads
        }

        for env_var, status in env_checks.items():
            status_icon = "✅" if status else "❌"
            st.write(f"{status_icon} {env_var}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Settings
        st.subheader("⚙️ Settings")
        max_emails = st.slider("Max emails to process", 10, 100, 50)

        # Quick actions
        st.subheader("🚀 Quick Actions")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Setup Schema", use_container_width=True):
                asyncio.run(setup_schema_if_needed())

        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        # Sample queries
        st.subheader("💡 Sample Queries")
        sample_queries = [
            "Analyze my recent emails from the past week",
            "What did we last agree on with TechCorp?",
            "Show me all action items from business emails",
            "Summarize my relationship with john@example.com",
            "Find emails about Q1 project decisions",
        ]

        for i, query in enumerate(sample_queries):
            if st.button(
                f"📝 {query[:30]}...", key=f"sample_{i}", use_container_width=True
            ):
                st.session_state.query_input = query

    # Main chat interface
    st.subheader("💬 Chat with Gmail Insights Agent")

    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)

    # Chat input
    query_input = st.chat_input("Ask about your Gmail communications...")

    # Handle query input from sample queries
    if hasattr(st.session_state, "query_input"):
        query_input = st.session_state.query_input
        delattr(st.session_state, "query_input")

    if query_input:
        # Add user message to chat
        user_message = {"role": "user", "content": query_input}
        st.session_state.messages.append(user_message)
        display_message(user_message)

        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your Gmail communications..."):
                # Ensure schema is set up
                schema_ready = asyncio.run(setup_schema_if_needed())

                if schema_ready:
                    # Process the query
                    response = asyncio.run(process_query(query_input))

                    # Display response
                    st.markdown(response)

                    # Add assistant message to chat
                    assistant_message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(assistant_message)
                else:
                    st.error(
                        "Please set up the database schema first using the sidebar button."
                    )

    # Footer with instructions
    st.markdown("---")
    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
        ### Getting Started
        1. **Setup**: Ensure your environment variables are configured (see sidebar status)
        2. **Schema**: Click "Setup Schema" to initialize the GibsonAI database
        3. **Authenticate**: Make sure you're authenticated with Gibson CLI (`gibson auth login`)
        4. **Gmail**: Configure Gmail credentials for email access
        
        ### Sample Use Cases
        - **Recall Conversations**: "What did we discuss with [company/person] last month?"
        - **Track Commitments**: "Show me all pending action items from my emails"
        - **Relationship Summary**: "Summarize my communication history with [contact]"
        - **Decision Tracking**: "What decisions were made in emails about [project]?"
        - **Follow-up Reminders**: "What follow-ups do I need to do based on recent emails?"
        
        ### Features
        - 🧠 **Long-term Memory**: Conversations stored in GibsonAI for weeks/months of recall
        - 📊 **Intelligent Analysis**: Extracts decisions, action items, and key topics
        - 👥 **Relationship Tracking**: Maintains profiles and communication patterns
        - 🎯 **Context-Aware**: Provides relevant summaries and suggestions
        """)

    with st.expander("🔧 Configuration Help", expanded=False):
        st.markdown("""
        ### Required Environment Variables
        Create a `.env` file with:
        ```
        MODEL_API_KEY=your_llm_api_key
        MODEL_ID=llama-3.3-70b-versatile  # or your preferred model
        GOOGLE_CLIENT_ID=your_google_client_id
        GOOGLE_CLIENT_SECRET=your_google_client_secret
        GOOGLE_PROJECT_ID=your_google_project_id
        GOOGLE_REDIRECT_URI=http://localhost
        ```
        
        ### Gmail Setup
        1. Create a Google Cloud project
        2. Enable Gmail API
        3. Create OAuth 2.0 credentials (Desktop application)
        4. Copy Client ID, Client Secret, and Project ID to .env file
        
        ### Gibson CLI Setup
        ```bash
        # Install Gibson CLI
        pip install gibson-cli
        
        # Authenticate
        gibson auth login
        ```
        """)


if __name__ == "__main__":
    main()
