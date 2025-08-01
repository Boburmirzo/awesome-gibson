"""
Streamlit Web Interface for CSV to SQL Agent
"""

import streamlit as st
import asyncio
import logging
import tempfile
import os
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

from csv_to_sql_agent import CSVToSQLAgent
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="CSV to SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and description
st.title("🤖 CSV to SQL Agent with GibsonAI")
st.markdown("""
Upload a CSV file and let the AI agent automatically:
- Analyze the CSV structure
- Create an optimized database schema
- Import your data into GibsonAI
- Enable natural language querying of your data
""")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Display current configuration
    config_errors = config.validate()
    if config_errors:
        st.error("❌ Configuration Issues:")
        for category, errors in config_errors.items():
            for error in errors:
                st.error(f"• {error}")
        st.info("Please check your .env file or environment variables")
    else:
        st.success("✅ Configuration OK")

    # Show configuration details
    with st.expander("View Configuration"):
        config_dict = config.to_dict()
        st.json(config_dict)

    st.markdown("---")

    # Advanced options
    st.header("🔧 Options")
    batch_size = st.slider("Import Batch Size", 50, 500, 100, 50)
    show_analysis = st.checkbox("Show Detailed Analysis", True)
    auto_query = st.text_input(
        "Auto-query after import", placeholder="e.g., Show me the first 10 rows"
    )

# Initialize agent for project info
if "agent" not in st.session_state:
    st.session_state.agent = CSVToSQLAgent()

# Project Information Section
st.markdown("### 📋 Current Project Information")

# Get current project info
project_info = st.session_state.agent.get_current_project_info()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Project Status",
        "Active" if project_info["project_uuid"] else "No Project",
        delta=None,
    )
with col2:
    st.metric(
        "Project UUID",
        project_info["project_uuid"][:8] + "..."
        if project_info["project_uuid"]
        else "None",
        delta=None,
    )
with col3:
    st.metric("Current Table", project_info["table_name"] or "None", delta=None)

# Show available projects
if st.expander("🔍 Available Projects", expanded=False):
    if st.button("🔄 Refresh Projects"):
        with st.spinner("Loading projects..."):
            try:
                projects = asyncio.run(st.session_state.agent.get_available_projects())
                print(f"Found {len(projects)} projects")
                st.session_state.available_projects = projects
            except Exception as e:
                st.error(f"Error loading projects: {str(e)}")

    if hasattr(st.session_state, "available_projects"):
        if st.session_state.available_projects:
            # Convert to DataFrame for table display
            if pd:  # pandas is available
                # Prepare data for table
                table_data = []
                for project in st.session_state.available_projects:
                    table_data.append(
                        {
                            "Project Name": project.get("name", "Unnamed Project"),
                            "UUID": project.get("uuid", "N/A")[:8] + "..."
                            if project.get("uuid")
                            else "N/A",
                            "Full UUID": project.get("uuid", "N/A"),
                            "Databases": ", ".join(project.get("databases", []))
                            if project.get("databases")
                            else "None",
                            "Modules": project.get("modules_count", 0),
                            "Functions": project.get("functions_count", 0),
                        }
                    )

                df = pd.DataFrame(table_data)

                # Display the table
                st.dataframe(
                    df[["Project Name", "UUID", "Databases"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Project Name": st.column_config.TextColumn(
                            "Project Name",
                            help="Name of the GibsonAI project",
                            width="medium",
                        ),
                        "UUID": st.column_config.TextColumn(
                            "UUID (Short)",
                            help="Shortened project UUID for display",
                            width="small",
                        ),
                        "Databases": st.column_config.TextColumn(
                            "Available Databases",
                            help="List of available databases in this project",
                            width="medium",
                        ),
                    },
                )

                # Show project count
                st.caption(
                    f"📊 Total Projects: {len(st.session_state.available_projects)}"
                )
            else:
                # Fallback display if pandas is not available
                st.warning("📊 Pandas not available - showing basic list format")
                for project in st.session_state.available_projects:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 2])
                        with col1:
                            st.write(f"**{project.get('name', 'Unnamed Project')}**")
                        with col2:
                            st.write(f"UUID: `{project.get('uuid', 'N/A')[:8]}...`")
                        with col3:
                            databases = project.get("databases", [])
                            st.write(f"DBs: {len(databases)}")
                        st.write("---")
        else:
            st.info("No projects found. Create one by uploading a CSV file!")

st.markdown("---")

# Main interface
tab1, tab2, tab3 = st.tabs(["📁 Upload & Process", "💬 Query Data", "📊 Results"])

with tab1:
    st.header("Upload CSV File")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV file with headers. Maximum size: 50MB",
    )

    if uploaded_file is not None:
        # Display file info
        st.info(
            f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)"
        )

        # Preview the data
        if pd:
            try:
                df_preview = pd.read_csv(uploaded_file, nrows=5)
                st.subheader("📋 Data Preview")
                st.dataframe(df_preview)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Columns", len(df_preview.columns))
                with col2:
                    # Get full row count
                    uploaded_file.seek(0)  # Reset file pointer
                    full_df = pd.read_csv(uploaded_file)
                    st.metric("Rows", len(full_df))
                    uploaded_file.seek(0)  # Reset again

            except Exception as e:
                st.error(f"Error previewing file: {str(e)}")

        # Process button
        if st.button("🚀 Process CSV", type="primary"):
            with st.spinner("Processing CSV file..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(
                        mode="wb", suffix=".csv", delete=False
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name

                    # Process the file using session state agent
                    result = asyncio.run(
                        st.session_state.agent.process_csv_file(tmp_path)
                    )

                    # Clean up temporary file
                    os.unlink(tmp_path)

                    # Store results in session state
                    st.session_state.processing_result = result
                    st.session_state.csv_filename = uploaded_file.name

                    if result["success"]:
                        st.success("✅ CSV processed successfully!")

                        # Show results
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"🆔 Project UUID: `{result['project_uuid']}`")
                        with col2:
                            st.info(f"🗃️ Table Name: `{result['table_name']}`")

                        # Refresh project info in UI
                        st.rerun()

                        # Show detailed analysis if requested
                        if show_analysis and "csv_analysis" in result:
                            with st.expander("📊 Detailed Analysis"):
                                analysis = result["csv_analysis"]

                                # File info
                                st.subheader("File Information")
                                file_info = analysis["file_info"]
                                st.json(file_info)

                                # Column analysis
                                st.subheader("Column Analysis")
                                data_types = analysis["structure"]["data_types"]

                                for col, info in data_types.items():
                                    with st.container():
                                        st.write(f"**{col}**")
                                        col_col1, col_col2, col_col3 = st.columns(3)
                                        with col_col1:
                                            st.write(
                                                f"Type: {info['recommended_sql_type']}"
                                            )
                                        with col_col2:
                                            st.write(
                                                f"Nulls: {info['null_percentage']:.1f}%"
                                            )
                                        with col_col3:
                                            st.write(f"Unique: {info['unique_count']}")

                                # Recommendations
                                st.subheader("Recommendations")
                                recs = analysis["recommendations"]
                                if recs["primary_key_candidates"]:
                                    st.write(
                                        f"🔑 Primary Key: {', '.join(recs['primary_key_candidates'])}"
                                    )
                                if recs["index_candidates"]:
                                    st.write(
                                        f"📇 Suggested Indexes: {', '.join(recs['index_candidates'])}"
                                    )

                        # Auto-query if specified
                        if auto_query:
                            with st.spinner(f"Running auto-query: {auto_query}"):
                                query_result = asyncio.run(
                                    st.session_state.agent.query_data(
                                        auto_query,
                                        result["project_uuid"],
                                        result["table_name"],
                                    )
                                )
                                st.session_state.last_query_result = query_result
                    else:
                        st.error(f"❌ Error processing CSV: {result['error']}")
                        if "csv_analysis" in result and result["csv_analysis"]:
                            st.info(
                                "💡 Partial analysis available in expandable section below"
                            )
                            with st.expander("Partial Analysis"):
                                st.json(result["csv_analysis"])

                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    logger.error(f"Processing error: {str(e)}")

with tab2:
    st.header("💬 Query Your Data")

    # Check if we have processed data
    if "processing_result" not in st.session_state:
        st.info("👆 Please upload and process a CSV file first")
    else:
        result = st.session_state.processing_result
        if not result["success"]:
            st.warning("⚠️ CSV processing failed. Please try processing again.")
        else:
            # Show current data info
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📄 Data: {st.session_state.get('csv_filename', 'Unknown')}")
            with col2:
                st.info(f"🗃️ Table: `{result['table_name']}`")

            # Query input
            query_text = st.text_area(
                "Enter your question about the data:",
                placeholder="e.g., Show me the top 10 records, What's the average of column X?, How many rows have null values?",
                height=100,
            )

            # Query execution
            if st.button("🔍 Execute Query", type="primary", disabled=not query_text):
                if query_text:
                    with st.spinner("Executing query..."):
                        try:
                            query_result = asyncio.run(
                                st.session_state.agent.query_data(
                                    query_text,
                                    result["project_uuid"],
                                    result["table_name"],
                                )
                            )

                            st.session_state.last_query_result = query_result
                            st.session_state.last_query_text = query_text

                            if query_result["success"]:
                                st.success("✅ Query executed successfully!")

                                # Display response
                                response = query_result["response"]
                                if "messages" in response:
                                    # Extract the final message
                                    messages = response["messages"]
                                    if messages:
                                        final_message = messages[-1]
                                        if "content" in final_message:
                                            st.markdown("### 📋 Results")
                                            st.markdown(final_message["content"])

                                # Show raw response in expander
                                with st.expander("🔍 Raw Response"):
                                    st.json(query_result)
                            else:
                                st.error(f"❌ Query failed: {query_result['error']}")

                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")
                            logger.error(f"Query error: {str(e)}")

with tab3:
    st.header("📊 Results & History")

    # Show last query result
    if "last_query_result" in st.session_state:
        result = st.session_state.last_query_result
        query_text = st.session_state.get("last_query_text", "Unknown query")

        st.subheader(f"Last Query: {query_text}")

        if result["success"]:
            # Show formatted response
            response = result["response"]
            if "messages" in response and response["messages"]:
                final_message = response["messages"][-1]
                if "content" in final_message:
                    st.markdown(final_message["content"])

            # Show execution details
            with st.expander("Execution Details"):
                st.json(result)
        else:
            st.error(f"Query failed: {result['error']}")
    else:
        st.info("No query results yet. Run a query in the Query Data tab.")

    # Processing results
    if "processing_result" in st.session_state:
        st.subheader("Processing Results")
        result = st.session_state.processing_result

        if result["success"]:
            st.success("✅ Data successfully imported to GibsonAI")

            # Show workflow details
            with st.expander("Workflow Details"):
                workflow = result.get("workflow_result", {})
                for step, response in workflow.items():
                    st.write(f"**{step.replace('_', ' ').title()}:**")
                    if isinstance(response, dict) and "messages" in response:
                        messages = response["messages"]
                        if messages:
                            final_msg = messages[-1]
                            if "content" in final_msg:
                                st.write(final_msg["content"])
                    else:
                        st.write(str(response))
                    st.write("---")
        else:
            st.error(f"❌ Processing failed: {result['error']}")

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center'>
    <p>🤖 CSV to SQL Agent powered by <strong>GibsonAI</strong> and <strong>LangChain</strong></p>
    <p><em>Upload CSV → Analyze → Create Schema → Import → Query with Natural Language</em></p>
</div>
""",
    unsafe_allow_html=True,
)
