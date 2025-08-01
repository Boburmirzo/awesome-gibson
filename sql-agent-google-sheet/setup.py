#!/usr/bin/env python3
"""
Setup script for CSV to SQL Agent
"""

import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} found")
        return True
    else:
        print(f"❌ {description} not found: {file_path}")
        return False


def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    template_file = Path(".env.example")

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    if template_file.exists():
        shutil.copy(template_file, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
        return True
    else:
        print("❌ .env.example template not found")
        return False


def install_gibson_cli():
    """Install Gibson CLI"""
    print("🔄 Installing Gibson CLI...")
    if run_command("pip install gibson-cli", "Gibson CLI installation"):
        return True

    # Try with uvx as fallback
    print("🔄 Trying alternative installation with uvx...")
    if run_command("uvx --from gibson-cli@latest gibson --help", "Gibson CLI test"):
        return True

    print("❌ Failed to install Gibson CLI")
    print("💡 Please install manually: pip install gibson-cli")
    return False


def main():
    print("🚀 Setting up CSV to SQL Agent")
    print("=" * 50)

    # Check Python version
    check_python_version()

    # Check required files
    required_files = [
        ("requirements.txt", "Requirements file"),
        (".env.example", "Environment template"),
        ("csv_to_sql_agent.py", "Main agent file"),
        ("csv_analyzer.py", "CSV analyzer"),
        ("config.py", "Configuration module"),
    ]

    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False

    if not all_files_exist:
        print("❌ Some required files are missing")
        sys.exit(1)

    # Install Python packages
    print("\n📦 Installing Python packages...")
    if not run_command(
        "pip install -r requirements.txt", "Python packages installation"
    ):
        print("⚠️  Some packages may have failed to install")
        print("💡 You can install them manually later")

    # Install additional MCP packages
    print("\n📦 Installing MCP packages...")
    mcp_packages = ["mcp", "langchain-mcp-adapters"]

    for package in mcp_packages:
        run_command(f"pip install {package}", f"{package} installation")

    # Install Gibson CLI
    print("\n🛠️  Installing Gibson CLI...")
    install_gibson_cli()

    # Create .env file
    print("\n⚙️  Setting up configuration...")
    create_env_file()

    # Test installation
    print("\n🧪 Testing installation...")
    try:
        from config import config

        errors = config.validate()
        if errors:
            print("⚠️  Configuration issues found:")
            for category, error_list in errors.items():
                for error in error_list:
                    print(f"   - {error}")
            print("💡 Please update your .env file with the required API keys")
        else:
            print("✅ Configuration is valid")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Some packages may not be installed correctly")

    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API key:")
    print("   - OPENAI_API_KEY: Your OpenAI API key (required)")
    print()
    print("2. Test the installation:")
    print("   python main.py --csv examples/employees.csv")
    print()
    print("3. Start the web interface:")
    print("   streamlit run streamlit_app.py")
    print()
    print(
        "💡 Note: Projects are managed dynamically - no need to set GIBSON_PROJECT_UUID!"
    )
    print(
        "The agent will create or find projects automatically based on your CSV data."
    )
    print()
    print("3. Start the web interface:")
    print("   streamlit run streamlit_app.py")
    print()
    print("4. Read the documentation:")
    print("   - README.md: Main documentation")
    print("   - examples/README.md: Example usage")
    print()
    print("🆘 Need help? Check the README.md file or GitHub issues.")


if __name__ == "__main__":
    main()
