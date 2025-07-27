#!/usr/bin/env bash
# Gmail Insights AI Agent - Quick Setup Script

set -e

echo "🚀 Gmail Insights AI Agent - Quick Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the gmail-insights-ai-agent directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 10 ]); then
    echo "❌ Error: Python 3.10+ is required. You have Python $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .

echo "✅ Dependencies installed successfully"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding"
else
    echo "✅ .env file already exists"
fi

# Check Gibson CLI
if ! command -v gibson &> /dev/null; then
    echo "⚠️  Gibson CLI not found. Installing..."
    pip install gibson-cli
    echo "✅ Gibson CLI installed"
else
    echo "✅ Gibson CLI found"
fi

# Check if Gibson is authenticated
if ! gibson auth status &> /dev/null; then
    echo "⚠️  Gibson CLI not authenticated. Please run:"
    echo "   gibson auth login"
else
    echo "✅ Gibson CLI authenticated"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - Set MODEL_API_KEY (your LLM provider API key)"
echo "   - Set GMAIL_CREDENTIALS_JSON path (see README for Gmail setup)"
echo ""
echo "2. Test your setup:"
echo "   python test_setup.py"
echo ""
echo "3. Set up Gmail API (if not done already):"
echo "   python setup_gmail.py"
echo ""
echo "4. Run the application:"
echo "   streamlit run app.py"
echo ""
echo "For detailed instructions, see README.md"
