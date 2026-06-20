import discord
from discord.ext import commands
from discord import app_commands
import os
from threading import Thread
from flask import Flask

# --- Flask Keep Alive for Render ---
app = Flask('')

@app.route('/')
def home():
    return "AI Zyro is online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Start Flask BEFORE bot so Render binds the port
keep_alive()

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} | AI Zyro Ready')
    try:
        synced = await bot.tree.sync()
