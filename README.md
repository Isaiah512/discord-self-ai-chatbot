# Discord Self AI Chatbot with Gemini
Transform your Discord account into an AI chatbot using the Google Gemini AI model.

Warning: Use this tool at your own risk. I do not take any responsibility if your Discord account gets banned or faces any other consequences due to the use of this tool. Make sure to comply with Discord's terms of service and guidelines.

## Features
- Text Conversations
- Computer vision for one or more images
- Conversation memory
- Context awareness
- Recognizes users

## Setup
- Python 3.9 or higher
- A Discord account and its token 
- Google Gemini API key

### Installation

1. Clone this repository to your local machine:
```bash
git clone https://github.com/Isaiah512/Discord-Self-AI-Chatbot.git
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

### Configuration
1. Create a `.env` file in the project directory with the following content:
```
DISCORD_TOKEN=your_discord_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

2. Run the bot:
```
python3 discord_bot.py
```

## Usage
- Mention the bot with text to get a response: `@AccountBot What is the capital of France?`
- Mention the bot with one or more image attachment: `@AccountBot What's in this image?`
- Use `@AccountName help` to see available commands.
