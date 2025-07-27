#!/usr/bin/env python3
"""
Gmail Setup Helper for Gmail Insights AI Agent
Helps users set up Gmail API credentials and test authentication
"""

import os


def check_credentials():
    """Check if Gmail credentials are properly configured"""
    print("🔍 Checking Gmail API configuration...")

    # Check environment variables
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    if not client_id:
        print("❌ GOOGLE_CLIENT_ID environment variable not set")
        return False

    if not client_secret:
        print("❌ GOOGLE_CLIENT_SECRET environment variable not set")
        return False

    if not project_id:
        print("❌ GOOGLE_PROJECT_ID environment variable not set")
        return False

    print(f"✅ GOOGLE_CLIENT_ID: {client_id[:10]}...")
    print(f"✅ GOOGLE_CLIENT_SECRET: {client_secret[:10]}...")
    print(f"✅ GOOGLE_PROJECT_ID: {project_id}")
    print(f"✅ GOOGLE_REDIRECT_URI: {redirect_uri or 'http://localhost (default)'}")

    return True


def print_setup_instructions():
    """Print Gmail API setup instructions"""
    print("\n📋 Gmail API Setup Instructions:")
    print("=" * 50)
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API' and enable it")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Desktop application'")
    print("   - Copy the Client ID and Client Secret")
    print("5. Update your .env file with:")
    print("   GOOGLE_CLIENT_ID=your_client_id_here")
    print("   GOOGLE_CLIENT_SECRET=your_client_secret_here")
    print("   GOOGLE_PROJECT_ID=your_project_id_here")
    print("   GOOGLE_REDIRECT_URI=http://localhost")
    print(
        "\n🔗 Detailed guide: https://developers.google.com/gmail/api/quickstart/python"
    )


def main():
    print("🚀 Gmail Insights AI Agent - Gmail Setup Helper")
    print("=" * 55)

    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Check basic configuration
    if not check_credentials():
        print("\n❌ Gmail configuration incomplete.")
        print_setup_instructions()
        return

    print("\n✅ Gmail API configuration looks good!")
    print("\n🎉 You're ready to use the Gmail Insights AI Agent!")
    print("\nNext steps:")
    print("1. Run: streamlit run app.py")
    print("2. Or use interactive mode: python run.py --interactive")
    print("3. On first use, you'll be prompted to authenticate with Gmail")


if __name__ == "__main__":
    main()
