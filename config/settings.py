"""
Configuration settings
"""
import os
from google.generativeai.types.safety_types import HarmCategory, HarmBlockThreshold

# pre-prompt
SYSTEM_PROMPT = """
You are a helpful and knowledgeable AI assistant.
Your personality traits:
- You provide detailed and accurate information
- You're good at explaining complex topics in simple terms
- You respond directly to questions without unnecessary disclaimers

Always respond in a natural, conversational manner.
When responding, use the conversation history to provide context-aware answers.
"""

# model settings
GEMINI_MODEL_TEXT = "gemini-2.0-flash"
GEMINI_MODEL_VISION = "gemini-2.0-flash"
GEMINI_TEMPERATURE = 0.5
GEMINI_MAX_OUTPUT_TOKENS = 2048

# safety settings
GEMINI_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}

# bot settings
MAX_MESSAGE_LENGTH = 2000
CHUNK_SIZE = 1900
MESSAGE_CHUNK_SUFFIX = " (continued...)"

# memory settings
MAX_USER_MESSAGES = 100
MAX_CHANNEL_MESSAGES = 50
MAX_CONTEXT_MESSAGES = 10
