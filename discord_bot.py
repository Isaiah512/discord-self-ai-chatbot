import discord
import google.generativeai as genai
import aiohttp
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
AUTH_KEY = os.getenv("AUTH_KEY")

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

TextModel = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
convo = TextModel.start_chat(history=[])
ImageModel = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.content.startswith('-a '):
            await self.RunTextModel(message=message)

        elif message.content == '-help':
            await message.channel.send('For text prompt: -a\nFor vision prompt: -i')

        elif message.content.startswith('-i'):
            await self.RunImageModel(message=message)

    async def RunTextModel(self, message):
        prompt = message.content[3:].strip()

        try:
            response = convo.send_message(prompt)
            message_response = response.text
        except Exception as e:
            message_response = f"{type(e).__name__}: {e.args}"
        if message_response:
            await message.channel.send(message_response)
        else:
            await message.channel.send("Failed to generate response.")

    async def RunImageModel(self,message):
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
            try:
                img = Image.open(image_file)
                response = ImageModel.generate_content([prompt, img], stream=True) 
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

client = MyClient()
client.run(AUTH_KEY)
