import discord
import os
from groq import Groq

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        if not prompt:
            await message.channel.send("Yo, @ me with a question!")
            return

        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )
            response = chat_completion.choices[0].message.content
            
            # Discord has a 2000 character limit
            if len(response) > 2000:
                response = response[:1997] + "..."
                
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send(f"Error: {e}")
            print(f"Error: {e}")

client.run(os.environ.get("DISCORD_TOKEN"))
