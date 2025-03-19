"""
General utility functions
"""
import os
import tempfile
from config.settings import CHUNK_SIZE, MESSAGE_CHUNK_SUFFIX

async def send_chunked_message(channel, content):
    """Send a long message in chunks"""
    from config.settings import MAX_MESSAGE_LENGTH
    
    if len(content) <= MAX_MESSAGE_LENGTH:
        await channel.send(content)
        return
        
    chunks = []
    current_chunk = ""
    sentences = content.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
    
    for sentence in sentences:
        # If a single sentence is too long, it needs to be split
        if len(sentence) > CHUNK_SIZE:
            # If current chunk has content, add it to chunks
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                
            # Split the long sentence into smaller parts
            for i in range(0, len(sentence), CHUNK_SIZE):
                part = sentence[i:i+CHUNK_SIZE]
                chunks.append(part)
        elif len(current_chunk) + len(sentence) + 1 <= CHUNK_SIZE:
            current_chunk = f"{current_chunk} {sentence}".strip() if current_chunk else sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk)
        
    for i, chunk in enumerate(chunks):
        await channel.send(f"{chunk}" + (MESSAGE_CHUNK_SUFFIX if i < len(chunks)-1 else ""))

def create_temp_file(suffix='.jpg'):
    """Create a temporary file and return its path."""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    return temp_file.name

def cleanup_temp_files(file_paths):
    """Clean up temporary files."""
    for path in file_paths:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error removing temporary file {path}: {e}")

def extract_user_info(user):
    """Extract information about the Discord user."""
    user_info = {
        'id': str(user.id),
        'name': user.name,
        'display_name': user.display_name if hasattr(user, 'display_name') else user.name,
    }
        
    return user_info
