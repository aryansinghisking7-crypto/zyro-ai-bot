import discord
from discord.ext import commands
from discord import app_commands
import os
from threading import Thread
from flask import Flask
from groq import Groq

# --- Flask Keep Alive for Render ---
app = Flask('')

@app.route('/')
def home():
    return "AI Zyro + Groq is online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Start Flask ---
keep_alive()

# --- Groq Setup ---
groq_client = Groq(api_key=os.environ['GROQ_API_KEY'])

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} | AI Zyro Ready')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

# --- /ask Command with Groq ---
@bot.tree.command(name="ask", description="Ask AI Zyro anything - powered by Groq")
@app_commands.describe(prompt="Your question for Zyro")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are AI Zyro, a helpful, friendly Discord bot. Keep replies under 1800 characters. Use markdown formatting when helpful."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=800
        )
        response = chat_completion.choices[0].message.content

    except Exception as e:
        response = f"Groq API error: {e}\nCheck
