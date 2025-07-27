#!/usr/bin/env python3
"""
Test script for Gmail Insights AI Agent
Tests the basic functionality without requiring full setup
"""

import asyncio
import os
from dotenv import load_dotenv


def test_environment():
    """Test environment configuration"""
    print("🧪 Testing Environment Configuration...")

    # Load environment variables
    load_dotenv()

    # Check required variables
    required_vars = ["MODEL_API_KEY"]
    optional_vars = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_PROJECT_ID"]

    print("\n📋 Required Environment Variables:")
    all_required_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"❌ {var}: Not set")
            all_required_present = False

    print("\n📋 Optional Environment Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (Gmail features will be limited)")

    return all_required_present


def test_imports():
    """Test if all required packages can be imported"""
    print("\n🧪 Testing Package Imports...")

    imports_to_test = [
        ("agno.agent", "Agent"),
        ("agno.storage.sqlite", "SqliteStorage"),
        ("agno.tools.mcp", "MultiMCPTools"),
        ("dotenv", "load_dotenv"),
        ("pydantic", "BaseModel"),
        ("streamlit", None),
    ]

    all_imports_successful = True

    for module_name, class_name in imports_to_test:
        try:
            if class_name:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ {module_name}.{class_name}")
            else:
                __import__(module_name)
                print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_imports_successful = False
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")

    return all_imports_successful


def test_model_initialization():
    """Test if the model can be initialized"""
    print("\n🧪 Testing Model Initialization...")

    try:
        from llm_model import get_model

        model_id = os.getenv("MODEL_ID", "llama-3.3-70b-versatile")
        api_key = os.getenv("MODEL_API_KEY")

        if not api_key:
            print("❌ Cannot test model - MODEL_API_KEY not set")
            return False

        # Try to initialize the model (but don't make API calls)
        model = get_model(model_id, api_key)
        print(f"✅ Model initialized: {model_id}")
        return True

    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return False


async def test_gibson_connection():
    """Test connection to GibsonAI MCP server"""
    print("\n🧪 Testing GibsonAI MCP Connection...")

    try:
        from agno.tools.mcp import MultiMCPTools

        # Try to connect to Gibson MCP server with short timeout
        async with MultiMCPTools(
            ["uvx --from gibson-cli@latest gibson mcp run"],
            env=os.environ,
            timeout_seconds=30,  # Short timeout for testing
        ) as mcp_tools:
            print("✅ GibsonAI MCP server connection successful")
            return True

    except Exception as e:
        print(f"❌ GibsonAI MCP connection failed: {e}")
        print("   Make sure to run 'gibson auth login' first")
        return False


def test_gmail_toolkit():
    """Test Gmail toolkit initialization"""
    print("\n🧪 Testing Gmail Toolkit...")

    try:
        from agno.tools.gmail import GmailTools

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        project_id = os.getenv("GOOGLE_PROJECT_ID")

        if not all([client_id, client_secret, project_id]):
            print("⚠️  Gmail credentials not configured - skipping Gmail test")
            return None

        # Try to initialize (but don't authenticate)
        gmail_tools = GmailTools()
        print("✅ Gmail tools initialized successfully")
        return True

    except Exception as e:
        print(f"❌ Gmail tools initialization failed: {e}")
        return False


async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Gmail Insights AI Agent - Comprehensive Test Suite")
    print("=" * 60)

    test_results = []

    # Test environment
    test_results.append(("Environment", test_environment()))

    # Test imports
    test_results.append(("Package Imports", test_imports()))

    # Test model
    test_results.append(("Model Initialization", test_model_initialization()))

    # Test Gibson connection
    test_results.append(("GibsonAI Connection", await test_gibson_connection()))

    # Test Gmail toolkit
    gmail_result = test_gmail_toolkit()
    if gmail_result is not None:
        test_results.append(("Gmail Toolkit", gmail_result))

    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1

    total = passed + failed
    print(f"\n🏆 Results: {passed}/{total} tests passed")

    if failed == 0:
        print("🎉 All tests passed! You're ready to use the Gmail Insights AI Agent!")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")

    return failed == 0


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
