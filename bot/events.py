"""
Discord event handlers
"""
from bot.memory import store_channel_message
from bot.commands import handle_help_command, handle_text_command, handle_image_command

async def on_ready(client):
    """Called when the client has successfully connected to Discord."""
    print(f'Logged in as {client.user.name} (ID: {client.user.id})')
    print('------')
    print('Ready to respond to messages')

async def on_message(client, message):
    """Process incoming messages."""
    # Store the message in channel history
    store_channel_message(message)
    
    # Skip processing if message is from the client itself
    if message.author.id == client.user.id:
        return
        
    # Process commands when the client is mentioned
    if client.user in message.mentions:
        content = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        if content.lower() == 'help':
            await handle_help_command(message)
        elif message.attachments:
            await handle_image_command(message, content)
        else:
            await handle_text_command(message, content)
