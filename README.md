# Discord Self AI Chatbot with Gemini
Transform your Discord account into an AI chatbot using the Gemini AI model.

Warning: Use this tool at your own risk. I do not take any responsibility if your Discord account gets banned or faces any other consequences due to the use of this tool. Make sure to comply with Discord's terms of service and guidelines.

## Setup
- Python 3.x installed on your system.
- Discord token
- Gemini API key

### Installation

1. Clone this repository to your local machine:
```bash
git clone https://github.com/Isaiah512/discord-self-ai-chatbot.git
```

2. Install the required Python packages:
- google-generativeai

You can install them using pip:
```bash
pip install google-generativeai
```

3. Install additional dependencies:
- jq
- PIL
- curl

On debian-based systems you can install them using apt:
```bash
sudo apt-get update
sudo apt-get install jq pillow curl
```

On macOS, you can install them using Homebrew:
```bash
brew install jq pillow pillow curl
```

### Usage
1. Create a `.env` file in the project directory with the following content:
```
TOKEN=your_discord_token_here
AUTH_KEY=your_gemini_api_key_here
CHANNEL_ID=your_discord_channel_id_here
```

2. Run the script:
```
./discord_bot.sh
```
## Commands
1. `-help`
To get a list of commands available.

2. `-a text here`
Generates text based on the provided input. It accepts a string of text as anargument and generates text output accordingly.

3. `-i text here[with image attached]`
A combination of image and text as inputs that allows answer questions about the provided image.
