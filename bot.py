import discord
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel('gemini-1.5-flash')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot: 
        return
    if message.content.startswith('!ask '):
        prompt = message.content[5:]
        try:
            response = model.generate_content(prompt)
            await message.channel.send(response.text[:2000]) # Discord limit
        except Exception as e:
            await message.channel.send(f"Error: {e}")

client.run(os.getenv('DISCORD_TOKEN'))
