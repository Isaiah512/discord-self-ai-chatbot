"""
Conversation memory management
"""
from collections import defaultdict, deque
from langchain.schema import HumanMessage, SystemMessage
from config.settings import MAX_USER_MESSAGES, MAX_CHANNEL_MESSAGES, SYSTEM_PROMPT

# Storage for user conversations and channel messages
user_convos = {}
channel_msgs = defaultdict(lambda: deque(maxlen=MAX_CHANNEL_MESSAGES))

class ConversationMemory:
    """Handles conversation history with proper rotation of messages."""
    def __init__(self, max_messages=MAX_USER_MESSAGES):
        self.messages = []
        self.max_messages = max_messages
        self.system_prompt = None

    def add_message(self, message):
        """Handle memory rotation and management."""
        # Store system prompt separately if it's the first one
        if isinstance(message, SystemMessage) and not self.system_prompt:
            self.system_prompt = message
            self.messages.append(message)
            return
            
        self.messages.append(message)
        # If limit exceeds, do the rotation
        if len(self.messages) > self.max_messages:
            if self.system_prompt:
                # Remove the oldest message but keep the system prompt
                non_system_messages = [m for m in self.messages if m != self.system_prompt]
                to_keep = [self.system_prompt] + non_system_messages[1:]
                self.messages = to_keep
            else:
                self.messages = self.messages[1:]

    def get_messages(self):
        """Retrieve all messages in the conversation memory."""
        return self.messages

def get_user_memory(user_id):
    """Get or create a conversation memory for a user."""
    if user_id not in user_convos:
        memory = ConversationMemory()
        memory.add_message(SystemMessage(content=SYSTEM_PROMPT))
        user_convos[user_id] = memory
    return user_convos[user_id]

def store_channel_message(message):
    """Store a message in the channel history."""
    channel_id = str(message.channel.id)
    channel_msgs[channel_id].append(message)

def format_message(message):
    """Format a message for context to the model."""
    content = message.content if message.content else "[No text content]"
    return f"{message.author.name}: {content}"

def get_channel_context(channel_id):
    """Get recent context from channel messages."""
    from config.settings import MAX_CONTEXT_MESSAGES
    
    messages = channel_msgs.get(channel_id, [])
    relevant_messages = []
    
    for msg in messages:
        if msg.author.bot:
            continue
        if not msg.content or msg.type != discord.MessageType.default:
            continue
        relevant_messages.append(msg)
    
    relevant_messages = relevant_messages[-MAX_CONTEXT_MESSAGES:]
    return "\n".join(format_message(m) for m in relevant_messages)

import discord
