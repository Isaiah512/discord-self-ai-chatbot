#!/usr/bin/env python3
"""
Main entry point for the Discord client that uses Google's Gemini AI
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = ['DISCORD_TOKEN', 'GEMINI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Import client after environment validation
from bot.client import client

if __name__ == "__main__":
    client.run(os.getenv('DISCORD_TOKEN'))
