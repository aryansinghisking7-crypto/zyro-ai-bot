import discord
from discord import app_commands
import os
from groq import Groq

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')

@tree.command(name="ask", description="Ask AI")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    res = groq.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model="llama-3.1-8b-instant"
    )
    await interaction.followup.send(res.choices[0].message.content[:2000])

client.run(os.environ.get("DISCORD_TOKEN"))
