"""
Google Gemini models
"""
import os
import aiohttp
from PIL import Image
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from utils.helpers import create_temp_file, cleanup_temp_files
from config.settings import (
    GEMINI_MODEL_TEXT, 
    GEMINI_MODEL_VISION,
    GEMINI_TEMPERATURE, 
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_SAFETY_SETTINGS
)

# Configure Google Generative AI API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize the text model with LangChain
text_model = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL_TEXT,
    google_api_key=os.getenv('GEMINI_API_KEY'),
    temperature=GEMINI_TEMPERATURE,
    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
    convert_system_message_to_human=True,
    safety_settings=GEMINI_SAFETY_SETTINGS
)

async def process_text_query(conversation_memory, query, channel_context=None, user_info=None):
    """Process a text query"""
    enhanced_query = query

    # Build the text prompt 
    user_context = ""
    if user_info:
        user_context = f"You are speaking with {user_info['name']} (User ID: {user_info['id']}). "
    
    if channel_context or user_context:
        enhanced_query = f"{user_context}\nRecent channel conversation for context:\n{channel_context}\n\nMy text: {query}"
    
    conversation_memory.add_message(HumanMessage(content=enhanced_query))
    response = text_model.invoke(conversation_memory.get_messages())
    conversation_memory.add_message(response)
    
    return response.content

async def process_image_query(prompt, attachments, channel_context=None, user_info=None):
    """Process images"""
    if not attachments:
        return "I was expecting an image but found none."
    
    if not prompt:
        prompt = "Describe this image in detail."
    
    # Build the vision prompt
    user_context = ""
    if user_info:
        user_context = f"You are speaking with {user_info['name']} (User ID: {user_info['id']}). "
    
    vision_prompt_text = f"{user_context}User query: {prompt}"
    
    if channel_context:
        vision_prompt_text = f"{user_context}Recent relevant conversation:\n{channel_context}\n\nUser query: {prompt}"
    
    images = []
    temp_files = []
    
    try:
        async with aiohttp.ClientSession() as session:
            for i, attachment in enumerate(attachments):
                if not attachment.content_type or not attachment.content_type.startswith('image/'):
                    continue
                
                image_url = attachment.url
                temp_path = create_temp_file(suffix='.jpg')
                temp_files.append(temp_path)
                
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        with open(temp_path, 'wb') as f:
                            f.write(await resp.read())
                        img = Image.open(temp_path)
                        images.append(img)
        
        if not images:
            return "No valid images were processed."
        
        # Process with Gemini vision model
        model = genai.GenerativeModel(GEMINI_MODEL_VISION)
        
        if len(images) == 1:
            contents = [vision_prompt_text, images[0]] if vision_prompt_text else images[0]
        else:
            contents = [vision_prompt_text] + images
        
        response = model.generate_content(contents)
        
        # Handle response
        response_text = ""
        if hasattr(response, "text") and response.text:
            response_text = response.text
        elif hasattr(response, "parts") and response.parts:
            for part in response.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text
        
        if not response_text:
            return "Couldn't interpret the image(s). Please try again."
            
        return response_text
    
    except Exception as e:
        return f"An error occurred while processing the image(s): {str(e)}"
    
    finally:
        cleanup_temp_files(temp_files)
