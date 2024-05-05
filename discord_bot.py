import os
import discord
from discord.ext import commands
import aiohttp
import google.generativeai as genai
from PIL import Image 
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
AUTH_KEY = os.getenv("AUTH_KEY")

bot = commands.Bot(command_prefix='-', self_bot=True)

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == '-help':
        await message.channel.send('For text prompt: -a\nFor vision prompt: -i')
    elif message.content.startswith('-i'):
        # vision prompt
        attachments = message.attachments
        if attachments:
            image_url = attachments[0].url
            image_file = "discord_image.jpg"
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        with open(image_file, 'wb') as f:
                            f.write(await resp.read())

            prompt = message.content[2:].strip()  
            genai.configure(api_key=TOKEN)

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]

            model = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)

            try:
                img = Image.open(image_file)
                response = model.generate_content([prompt, img], stream=True) 
                response.resolve()
                message_response = response.text
            except Exception as e:
                message_response = f"ERROR: {str(e)}"

            os.remove(image_file)

            if message_response:
                await message.channel.send(message_response)
            else:
                await message.channel.send("Failed to generate response.")
        else:
            await message.channel.send("No image attached.")
    elif message.content.startswith('-a'):
        # text prompt
        prompt = message.content[2:].strip()
        genai.configure(api_key=TOKEN)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 100
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        try:
            convo = model.start_chat(history=[])
            response = convo.send_message(prompt)
            message_response = response.text
        except Exception as e:
            message_response = f"ERROR: {str(e)}"

        if message_response:
            await message.channel.send(message_response)
        else:
            await message.channel.send("Failed to generate response.")

bot.run(AUTH_KEY)

