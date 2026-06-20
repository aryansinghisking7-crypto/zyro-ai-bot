import discord
import os
from groq import Groq

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

groq_client = Groq(api_key=GROQ_API_KEY)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if client.user.mentioned_in(message):
        async with message.channel.typing():
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": message.content.replace(f'<@{client.user.id}>', '').strip()
                    }
                ],
                model="llama3-8b-8192",
            )
            await message.reply(chat_completion.choices[0].message.content)

client.run(DISCORD_TOKEN)
