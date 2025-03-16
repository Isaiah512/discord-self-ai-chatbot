"""
Bot commands
"""
from bot.memory import get_user_memory, get_channel_context
from bot.ai_service import process_text_query, process_image_query
from utils.helpers import send_chunked_message, extract_user_info

async def handle_help_command(message):
    """Display help message."""
    help_text = (
        "**How to use me**\n"
        "Mention me with a text for conversation, or attach an image (with an optional caption).\n"
        "\nCommands:\n"
        "`help` - Show this help message"
    )
    await message.channel.send(help_text)

async def handle_text_command(message, query):
    """Handle text-based queries."""
    if not query:
        await message.channel.send("Please provide a message after mentioning me.")
        return
    
    try:
        user_id = str(message.author.id)
        conversation_memory = get_user_memory(user_id)
        channel_context = get_channel_context(str(message.channel.id))
        user_info = extract_user_info(message.author)
        
        response_content = await process_text_query(
            conversation_memory, 
            query, 
            channel_context,
            user_info
        )
        
        await send_chunked_message(message.channel, response_content)
        
    except Exception as e:
        await message.channel.send(f"An error occurred: {str(e)}")
        print(f"Error in text processing: {e}")

async def handle_image_command(message, prompt):
    """Handle image-based queries."""
    attachments = message.attachments
    
    try:
        channel_context = get_channel_context(str(message.channel.id))
        user_info = extract_user_info(message.author)
        
        if len(attachments) > 1:
            await message.channel.send(f"Processing {len(attachments)} attachments...")
        
        response_text = await process_image_query(
            prompt,
            attachments,
            channel_context,
            user_info
        )
        
        await send_chunked_message(message.channel, response_text)
        
    except Exception as e:
        await message.channel.send(f"An error occurred: {str(e)}")
        print(f"Error in image processing: {e}")
