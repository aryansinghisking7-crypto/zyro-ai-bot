import discord
from discord.ext import commands
from discord import app_commands
import os
from groq import Groq
from flask import Flask
from threading import Thread

# ===== FLASK FOR UPTIMEROBOT =====
app = Flask('')

@app.route('/')
def home():
    return "ZYRO AI is online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ===== ENV VARS =====
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not DISCORD_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing DISCORD_TOKEN or GROQ_API_KEY")

# ===== DISCORD BOT SETUP =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)
groq_client = Groq(api_key=GROQ_API_KEY)

@bot.event
async def on_ready():
    print(f'ZYRO online as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s) globally')
    except Exception as e:
        print(f'Failed to sync: {e}')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! ZYRO is alive")

@bot.command()
async def ask(ctx, *, question):
    await ctx.typing()
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.1-8b-instant",
            max_tokens=800
        )
        await ctx.send(chat_completion.choices[0].message.content[:2000])
    except Exception as e:
        await ctx.send(f"Error: {str(e)[:1800]}")

@bot.tree.command(name="ask", description="Ask ZYRO AI anything")
@app_commands.describe(question="What do you want to ask?")
async def slash_ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.1-8b-instant",
            max_tokens=800
        )
        await interaction.followup.send(chat_completion.choices[0].message.content[:2000])
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)[:1800]}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot.user.mentioned_in(message):
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        question = question.replace(f'<@!{bot.user.id}>', '').strip()
        if not question:
            await message.channel.send(f"Yo {message.author.mention}, ask me something!")
            return
        await message.channel.typing()
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                model="llama-3.1-8b-instant",
                max_tokens=800
            )
            await message.channel.send(chat_completion.choices[0].message.content[:2000])
        except Exception as e:
            await message.channel.send(f"Brain fried: {str(e)[:1800]}")
    await bot.process_commands(message)

keep_alive()
bot.run(DISCORD_TOKEN)
