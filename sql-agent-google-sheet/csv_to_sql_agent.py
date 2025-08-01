"""
CSV to SQL Agent using GibsonAI MCP Server
This module creates an AI agent that connects directly to the GibsonAI MCP server
"""

import logging
from typing import Dict, Any, List

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from langchain_mcp_adapters.tools import load_mcp_tools
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI
except ImportError as e:
    raise ImportError(
        f"Required MCP packages not installed: {e}. Please run: pip install mcp langchain-mcp-adapters"
    )

from csv_analyzer import CSVAnalyzer
from config import config

logger = logging.getLogger(__name__)


class CSVToSQLAgent:
    """Main agent that uses GibsonAI MCP server for CSV to SQL conversion"""

    def __init__(self):
        self.model = ChatOpenAI(
            api_key=config.agent.openai_api_key,
            model=config.agent.model,
            temperature=config.agent.temperature,
        )

        # GibsonAI MCP server parameters
        self.server_params = StdioServerParameters(
            command="uvx", args=["--from", "gibson-cli@latest", "gibson", "mcp", "run"]
        )

        self.csv_analyzer = CSVAnalyzer(
            max_size_mb=config.csv.max_size_mb,
            supported_encodings=config.csv.supported_encodings,
        )

        # Dynamic project management - no fixed project UUID
        self.current_project_uuid = None
        self.current_table_name = None

    async def get_available_projects(self) -> List[Dict[str, Any]]:
        """Get list of available GibsonAI projects"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)
                    agent = create_react_agent(self.model, tools)

                    result = await agent.ainvoke(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": "List all available projects using get_projects GibsonAI MCP tool",
                                }
                            ]
                        }
                    )

                    # Parse the actual project data from the tool response
                    projects = []
                    for message in result.get("messages", []):
                        # Look for ToolMessage containing the project data
                        if hasattr(message, "name") and message.name == "get_projects":
                            import json

                            try:
                                # The content is a JSON array of project strings
                                project_strings = json.loads(message.content)
                                for project_str in project_strings:
                                    project_data = json.loads(project_str)

                                    # Extract key information for Streamlit display
                                    project_info = {
                                        "uuid": project_data.get("uuid"),
                                        "name": project_data.get("name")
                                        or "Unnamed Project",
                                        "databases": [
                                            db.get("name")
                                            for db in project_data.get("databases", [])
                                        ],
                                        "modules_count": len(
                                            project_data.get("modules", [])
                                        ),
                                        "functions_count": len(
                                            project_data.get("functions", [])
                                        ),
                                    }
                                    projects.append(project_info)
                            except (json.JSONDecodeError, AttributeError) as e:
                                logger.error(f"Error parsing project data: {str(e)}")
                                continue

                    return projects

        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            return []

    async def create_project(self, table_name: str) -> str:
        """Create a new project for the table"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)
                    agent = create_react_agent(self.model, tools)

                    # Always create new project for each CSV import
                    create_result = await agent.ainvoke(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"Create a new project using create_project Gibson MCP tool for table '{table_name}'",
                                }
                            ]
                        }
                    )

                    # Extract UUID from create result - we need to parse the response
                    for message in create_result.get("messages", []):
                        if hasattr(message, "content") and isinstance(
                            message.content, str
                        ):
                            # Look for UUID pattern in the response
                            import re

                            uuid_pattern = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
                            match = re.search(uuid_pattern, message.content)
                            if match:
                                project_uuid = match.group(0)
                                self.current_project_uuid = project_uuid
                                logger.info(f"Created new project: {project_uuid}")
                                return project_uuid

                    raise Exception(
                        "Failed to create project - no UUID found in response"
                    )

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

    def get_current_project_info(self) -> Dict[str, Any]:
        """Get current project information"""
        return {
            "project_uuid": self.current_project_uuid,
            "table_name": self.current_table_name,
            "status": "active" if self.current_project_uuid else "no_project",
        }

    async def process_csv_file(self, csv_file_path: str) -> Dict[str, Any]:
        """Process CSV file through the complete workflow using MCP tools"""
        try:
            # Step 1: Analyze CSV file locally
            logger.info(f"Analyzing CSV file: {csv_file_path}")
            csv_analysis = self.csv_analyzer.analyze_file(csv_file_path)

            # Step 2: Connect to GibsonAI MCP server and process
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()

                    # Get tools from MCP server
                    tools = await load_mcp_tools(session)

                    # Create agent with MCP tools
                    agent = create_react_agent(self.model, tools)

                    # Generate workflow prompts
                    workflow_result = await self._run_workflow(
                        agent, csv_analysis, csv_file_path
                    )

                    return {
                        "success": True,
                        "csv_analysis": csv_analysis,
                        "workflow_result": workflow_result,
                        "project_uuid": self.current_project_uuid,
                        "table_name": self.current_table_name,
                    }

        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "csv_analysis": csv_analysis if "csv_analysis" in locals() else None,
            }

    async def query_data(
        self, user_query: str, project_uuid: str = None, table_name: str = None
    ) -> Dict[str, Any]:
        """Query the imported data using natural language"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()

                    # Get tools from MCP server
                    tools = await load_mcp_tools(session)

                    # Create agent with MCP tools
                    agent = create_react_agent(self.model, tools)

                    # Use provided UUIDs or fall back to current ones
                    project_uuid = project_uuid or self.current_project_uuid
                    table_name = table_name or self.current_table_name

                    # Create query prompt
                    query_prompt = f"""
                    User wants to query data from their database. 
                    
                    User question: {user_query}
                    Project UUID: {project_uuid}
                    Table name: {table_name}
                    
                    Please:
                    1. First get the deployed schema for the project to understand the table structure
                    2. Generate appropriate SQL query based on user's question and schema
                    3. Execute the query using the GibsonAI MCP query_database tool
                    4. Format the results in a user-friendly way
                    
                    Be conversational and helpful in your response.
                    """

                    response = await agent.ainvoke(
                        {"messages": [{"role": "user", "content": query_prompt}]}
                    )

                    return {
                        "success": True,
                        "user_query": user_query,
                        "response": response,
                        "project_uuid": project_uuid,
                        "table_name": table_name,
                    }

        except Exception as e:
            logger.error(f"Error querying data: {str(e)}")
            return {"success": False, "error": str(e), "user_query": user_query}

    async def _run_workflow(
        self, agent, csv_analysis: Dict[str, Any], csv_file_path: str
    ) -> Dict[str, Any]:
        """Run the complete CSV to SQL workflow using the MCP agent"""

        # Get table name from CSV analysis
        self.current_table_name = csv_analysis["file_info"]["filename"]
        logger.info(f"Using table name from analysis: {self.current_table_name}")

        # Step 1: Find or create project dynamically
        try:
            project_uuid = await self.find_or_create_project(self.current_table_name)
            logger.info(f"Using project: {project_uuid}")
        except Exception as e:
            logger.error(f"Failed to get/create project: {str(e)}")
            return {"error": f"Project management failed: {str(e)}"}

        # Step 2: Create schema from CSV analysis
        modeling_request = self._generate_modeling_request(
            csv_analysis, self.current_table_name
        )

        schema_prompt = f"""
        I need to create a database schema for importing CSV data.
        
        Project UUID: {project_uuid}
        
        Please submit this data modeling request:
        
        {modeling_request}
        
        This will create the table structure needed for the CSV data.
        """

        schema_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": schema_prompt}]}
        )

        # Step 3: Deploy schema
        deploy_prompt = f"""
        Now I need to deploy the schema to the Production database.
        
        Project UUID: {self.current_project_uuid or "Use the project UUID from the previous steps"}
        
        Please deploy the project to the "Production" database so we can start importing data.
        """

        deploy_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": deploy_prompt}]}
        )

        # Step 4: Import data
        import_prompt = f"""
        Now I need to import the CSV data into the deployed table.
        
        Project UUID: {self.current_project_uuid or "Use the project UUID from the previous steps"}
        Table name: {self.current_table_name}
        CSV file: {csv_file_path}
        
        I need to:
        1. Get the project's hosted database details
        2. Read the CSV data and convert it to INSERT statements
        3. Execute the INSERT statements using the GibsonAI MCP server query_database tool
        
        The CSV has {csv_analysis["file_info"]["estimated_rows"]} rows and {csv_analysis["structure"]["column_count"]} columns.
        
        Please help me import this data efficiently (you may want to batch the inserts).
        """

        import_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": import_prompt}]}
        )

        return {
            "project_uuid": project_uuid,
            "table_name": self.current_table_name,
            "schema_creation": schema_response,
            "schema_deployment": deploy_response,
            "data_import": import_response,
        }

    def _generate_modeling_request(
        self, csv_analysis: Dict[str, Any], table_name: str
    ) -> str:
        """Generate data modeling request from CSV analysis"""
        structure = csv_analysis["structure"]
        # Build modeling request
        request_parts = [
            "Create a database table with the following structure:",
            "",
            "Columns:",
        ]

        for column, type_info in structure["data_types"].items():
            sql_type = type_info["recommended_sql_type"]
            nullable = "NULL" if column in structure["nullable_columns"] else "NOT NULL"

            request_parts.append(f"- {column}: {sql_type} {nullable}")

            # Add comments for context
            if type_info["sample_values"]:
                sample_str = ", ".join(str(v) for v in type_info["sample_values"][:3])
                request_parts.append(f"  # Sample values: {sample_str}")

        # Add metadata
        request_parts.extend(
            [
                "",
                f"Source: CSV file with {structure['column_count']} columns",
            ]
        )

        return "\n Do not ask other clarification questions. Decide on your own".join(
            request_parts
        )
