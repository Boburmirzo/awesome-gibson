# CSV to SQL Agent with GibsonAI

🤖 An intelligent AI agent solution that converts CSV files into SQL databases using GibsonAI MCP server and enables natural language querying of the data.

## 🌟 Features

- **🔍 Smart CSV Analysis**: Automatically analyzes CSV structure, data types, and quality
- **🗄️ Schema Generation**: Uses GibsonAI to create optimized database schemas with proper constraints
- **📊 Data Import**: Seamlessly imports CSV data into GibsonAI hosted databases
- **💬 Natural Language Chat**: Query your data using plain English questions
- **🤖 Multi-Agent Architecture**: Built with LangChain and LangGraph for robust AI workflows
- **🌐 Multiple Interfaces**: Command-line, web interface, and Python API
- **⚡ MCP Integration**: Direct connection to GibsonAI MCP server for real-time data operations

## 🏗️ Architecture

The solution uses a multi-agent architecture with direct MCP server integration:

```
CSV File → CSV Analyzer Agent → Schema Designer → Data Importer → Query Agent
    ↓              ↓                    ↓              ↓           ↓
Local Analysis → GibsonAI MCP → Schema Creation → Data Import → SQL Queries
```

### Agent Workflow:
1. **CSV Analyzer Agent**: Analyzes CSV structure, data types, and recommends optimizations
2. **Schema Designer Agent**: Creates optimal database schema using GibsonAI MCP tools
3. **Data Importer Agent**: Handles efficient data import with batching
4. **Query Agent**: Processes natural language queries and generates SQL

### MCP Server Integration:
- Direct connection to GibsonAI MCP server using `uvx --from gibson-cli@latest gibson mcp run`
- Real-time schema creation and deployment
- Efficient data querying with hosted database APIs
- Automatic project and database management

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd sql-agent-google-sheet

# Run setup script (recommended)
python setup.py

# Or install manually:
pip install -r requirements.txt
pip install mcp langchain-mcp-adapters
```

### 2. Configuration

Create your `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your API key:

```env
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Custom settings
MAX_CSV_SIZE_MB=50
SUPPORTED_CSV_ENCODINGS=utf-8,latin-1,cp1252
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000
CSV_CHUNK_SIZE=1000
```

### 3. Usage Options

#### Command Line Interface

```bash
# Process a CSV file
python main.py --csv examples/employees.csv

# Process and query immediately
python main.py --csv examples/employees.csv --auto-query "Show me the first 10 employees"

# Query existing data
python main.py --query "What's the average salary by department?" --project-uuid YOUR_UUID --table-name employees

# Show help
python main.py --help
```

#### Web Interface (Streamlit)

```bash
# Start the web interface
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501` and upload CSV files through the intuitive interface.

**Features:**
- 📋 **Project Dashboard**: View current project information and available projects
- 📁 **File Upload**: Drag and drop CSV files with real-time preview
- 🔄 **Auto Processing**: Automatic project creation and schema deployment
- 💬 **Interactive Queries**: Natural language query interface with results display

#### Python API

```python
import asyncio
from csv_to_sql_agent import process_csv, query_csv_data

async def main():
    # Process CSV
    result = await process_csv("path/to/your/file.csv")
    
    if result['success']:
        project_uuid = result['project_uuid']
        table_name = result['table_name']
        
        # Query the data
        query_result = await query_csv_data(
            "Show me records where salary > 70000",
            project_uuid,
            table_name
        )
        print(query_result['response'])

asyncio.run(main())
```

## 📋 Examples

The `examples/` directory contains sample CSV files:

### employees.csv
Sample employee data with columns: id, name, email, age, department, salary, hire_date, is_active

**Try these queries:**
- "Show me all employees"
- "What's the average salary by department?"
- "How many employees were hired in 2022?"
- "Show me employees older than 35"

### products.csv
Sample product inventory with columns: product_id, product_name, category, price, stock_quantity, supplier, last_updated

**Try these queries:**
- "Show me products under $100"
- "What's the total inventory value by category?"
- "Which products are low in stock?"
- "Who are our suppliers?"

## 🛠️ Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM functionality | - | Yes |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4 | No |
| `OPENAI_TEMPERATURE` | Model temperature | 0.1 | No |
| `OPENAI_MAX_TOKENS` | Maximum tokens per request | 2000 | No |
| `MAX_CSV_SIZE_MB` | Maximum CSV file size | 50 | No |
| `SUPPORTED_CSV_ENCODINGS` | Supported file encodings | utf-8,latin-1,cp1252 | No |
| `CSV_CHUNK_SIZE` | Data import batch size | 1000 | No |

### Command Line Options

```
--csv CSV_FILE          Process a CSV file
--query QUERY           Execute a natural language query
--project-uuid UUID     Specify project UUID for queries
--table-name TABLE      Specify table name for queries
--auto-query QUERY      Query to run after CSV processing
--verbose, -v           Enable verbose output
--config                Show current configuration
--list-projects         List available projects
```

## 🔧 Advanced Usage

### Custom Schema Requests

The agent automatically generates schema requests, but you can customize the process by modifying the CSV analysis or providing hints:

```python
# Custom modeling request
modeling_request = """
Create a table 'sales_data' with:
- id: PRIMARY KEY AUTO_INCREMENT
- customer_name: VARCHAR(255) NOT NULL
- purchase_date: DATE NOT NULL
- amount: DECIMAL(10,2) NOT NULL
- INDEX on customer_name
- INDEX on purchase_date
"""
```

### Batch Processing

For large CSV files, the agent automatically handles batching:

```python
# The agent splits large imports into batches
# Default batch size is 100 rows, configurable via CSV_CHUNK_SIZE
```

### Error Handling

The agent provides comprehensive error handling:

```python
result = await process_csv("file.csv")
if not result['success']:
    print(f"Error: {result['error']}")
    # Partial analysis may still be available
    if result.get('csv_analysis'):
        print("Partial analysis available")
```

## 🤝 GibsonAI MCP Server Integration

This agent connects directly to the GibsonAI MCP server using the official gibson-cli:

### Server Configuration
```json
{
  "mcpServers": {
    "gibson": {
      "command": "uvx",
      "args": ["--from", "gibson-cli@latest", "gibson", "mcp", "run"]
    }
  }
}
```

### Dynamic Project Management
The agent automatically manages GibsonAI projects:
- **Existing Projects**: Searches for projects with similar names to your CSV table
- **New Projects**: Creates new projects automatically if none match
- **Project Selection**: Shows current project information in the web interface
- **No Configuration**: No need to set project UUIDs in environment variables

### Available MCP Tools
- `mcp_gibson_get_projects()`: List all projects
- `mcp_gibson_create_project()`: Create new project
- `mcp_gibson_get_project_details()`: Get project information
- `mcp_gibson_submit_data_modeling_request()`: Create database schema
- `mcp_gibson_deploy_project()`: Deploy schema to database
- `mcp_gibson_query_database()`: Execute SQL queries
- `mcp_gibson_get_deployed_schema()`: Get schema information

## 📊 Supported Data Types

The agent automatically detects and converts:

| CSV Data | Detected As | SQL Type |
|----------|-------------|----------|
| Integers | int64 | INT, BIGINT |
| Decimals | float64 | DECIMAL(10,2) |
| Text | object | VARCHAR(n), TEXT |
| Dates | datetime64 | DATE, DATETIME |
| Booleans | bool | BOOLEAN |
| Mixed | object | TEXT |

## 🐛 Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   ```
   Error: Failed to connect to GibsonAI MCP server
   Solution: Ensure gibson-cli is installed: pip install gibson-cli
   ```

2. **Configuration Errors**
   ```
   Error: OpenAI API key is required
   Solution: Set OPENAI_API_KEY in your .env file
   ```

3. **CSV Parsing Errors**
   ```
   Error: Unable to detect encoding
   Solution: Try specifying encoding in CSV_ENCODINGS config
   ```

4. **Large File Issues**
   ```
   Error: File size exceeds maximum
   Solution: Increase MAX_CSV_SIZE_MB or split the file
   ```

### Debug Mode

Enable verbose logging:

```bash
python main.py --csv file.csv --verbose
```

Or set in code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Testing

Run with example files:

```bash
# Test employee data
python main.py --csv examples/employees.csv --auto-query "Count employees by department"

# Test product data
python main.py --csv examples/products.csv --auto-query "Show expensive products"

# Test web interface
streamlit run streamlit_app.py
```

## 📚 API Reference

### process_csv(csv_file_path: str) -> Dict[str, Any]

Process a CSV file through the complete workflow.

**Returns:**
```python
{
    'success': bool,
    'csv_analysis': dict,  # Detailed analysis
    'workflow_result': dict,  # Agent responses
    'project_uuid': str,
    'table_name': str,
    'error': str  # If success=False
}
```

### query_csv_data(user_query: str, project_uuid: str, table_name: str) -> Dict[str, Any]

Query imported data using natural language.

**Returns:**
```python
{
    'success': bool,
    'user_query': str,
    'response': dict,  # Agent response with results
    'project_uuid': str,
    'table_name': str,
    'error': str  # If success=False
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- 📖 Check the [examples/README.md](examples/README.md) for detailed usage examples
- 🐛 Report issues on GitHub
- 💬 Join our community discussions
- 📧 Contact support for enterprise features

---

**Made with ❤️ using GibsonAI, LangChain, and LangGraph**
