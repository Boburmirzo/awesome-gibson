#!/usr/bin/env python3
"""
Run script for Gmail Insights AI Agent
Provides a simple command-line interface for testing the agent
"""

import asyncio
import argparse
import sys
from agent import run_gmail_insights_agent, setup_gibson_schema


async def main():
    parser = argparse.ArgumentParser(description="Gmail Insights AI Agent")
    parser.add_argument(
        "--setup-schema",
        action="store_true",
        help="Set up the GibsonAI database schema",
    )
    parser.add_argument("--query", type=str, help="Query to send to the agent")
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Session ID for conversation persistence",
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    try:
        # Set up schema if requested
        if args.setup_schema:
            print("Setting up GibsonAI database schema...")
            await setup_gibson_schema()
            print("✅ Schema setup completed!")
            return

        # Handle single query
        if args.query:
            print(f"Processing query: {args.query}")
            response = await run_gmail_insights_agent(
                message=args.query, session_id=args.session_id
            )
            print("\n🤖 Agent Response:")
            print("=" * 50)
            print(response.content)
            return

        # Interactive mode
        if args.interactive:
            session_id = args.session_id or "interactive_session"
            print("🚀 Gmail Insights AI Agent - Interactive Mode")
            print("Type 'quit' or 'exit' to stop, 'schema' to setup database schema")
            print("=" * 60)

            while True:
                try:
                    query = input("\n💬 Your query: ").strip()

                    if query.lower() in ["quit", "exit"]:
                        print("👋 Goodbye!")
                        break

                    if query.lower() == "schema":
                        print("Setting up GibsonAI database schema...")
                        await setup_gibson_schema()
                        print("✅ Schema setup completed!")
                        continue

                    if not query:
                        continue

                    print("🔄 Processing...")
                    response = await run_gmail_insights_agent(
                        message=query, session_id=session_id
                    )

                    print("\n🤖 Agent Response:")
                    print("-" * 40)
                    print(response.content)
                    print("-" * 40)

                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")

            return

        # Default: show help
        parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
