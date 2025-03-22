"""
Conversation memory management
"""
from collections import defaultdict, deque
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config.settings import MAX_USER_MESSAGES, MAX_CHANNEL_MESSAGES, SYSTEM_PROMPT

# Storage for user conversations, channel messages, and user info
user_convos = {}
user_info_storage = {}
channel_msgs = defaultdict(lambda: deque(maxlen=MAX_CHANNEL_MESSAGES))

class ConversationMemory:
    """Handles conversation history with rotation of the messages."""
    def __init__(self, max_messages=MAX_USER_MESSAGES):
        self.messages = []
        self.max_messages = max_messages
        
    def add_message(self, message):
        """Add a message to the conversation."""
        self.messages.append(message)
        self._rotate_messages()
    
    def _rotate_messages(self):
        """Ensure the conversation doesn't exceed the maximum number of messages."""
        if len(self.messages) <= self.max_messages:
            return
            
        # find the system message
        system_idx = None
        for i, msg in enumerate(self.messages):
            if isinstance(msg, SystemMessage):
                system_idx = i
                break
        
        # If we have a system message, keep it and remove oldest normal messages
        if system_idx is not None:
            system_msg = self.messages[system_idx]
            other_messages = [m for i, m in enumerate(self.messages) if i != system_idx]
            to_keep = other_messages[-(self.max_messages - 1):]
            self.messages = [system_msg] + to_keep
        else:
            self.messages = self.messages[-self.max_messages:]

def get_user_memory(user_id):
    """Get or create a conversation memory for a user."""
    if user_id not in user_convos:
        memory = ConversationMemory()
        memory.add_message(SystemMessage(content=SYSTEM_PROMPT))
        user_convos[user_id] = memory
    return user_convos[user_id]

def store_user_info(user_id, user_info):
    """Store or update user information."""
    user_info_storage[user_id] = user_info

def get_user_info(user_id):
    """Retrieve stored user information."""
    return user_info_storage.get(user_id)

def store_channel_message(message):
    """Store a message in the channel history."""
    channel_id = str(message.channel.id)
    channel_msgs[channel_id].append(message)
    
    # store user info
    if not message.author.bot:
        from utils.helpers import extract_user_info
        user_id = str(message.author.id)
        user_info = extract_user_info(message.author)
        store_user_info(user_id, user_info)

def format_message(message):
    """Format a message for context."""
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

# Import discord to avoid circular import issues
import discord
