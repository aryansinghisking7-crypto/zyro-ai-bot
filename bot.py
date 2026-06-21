import discord
from discord.ext import commands
import os
from groq import Groq
from flask import Flask
from threading import Thread

# ===== FLASK STUFF TO KEEP RENDER ALIVE =====
app = Flask('')

@app.route('/')
def home():
    return "ZYRO AI is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ===== DISCORD BOT SETUP =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents) # ← Changed to? here

# ===== GROQ AI SETUP =====
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@bot.event
async def on_ready():
    print(f'ZYRO online as {bot.user}')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! ZYRO is alive")

@bot.command()
async def ask(ctx, *, question):
    await ctx.typing()
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.1-8b-instant",
        )
        answer = chat_completion.choices[0].message.content
        await ctx.send(answer[:2000])
    except Exception as e:
        await ctx.send(f"Error: {str(e)[:1800]}")

@bot.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return

    # Reply when ZYRO is mentioned
    if bot.user.mentioned_in(message):
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        question = question.replace(f'<@!{bot.user.id}>', '').strip()

        if question == "":
            await message.channel.send(f"Yo {message.author.mention}, ask me something!")
            return

        await message.channel.typing()
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                model="llama-3.1-8b-instant",
            )
            answer = chat_completion.choices[0].message.content
            await message.channel.send(answer[:2000])
        except Exception as e:
            await message.channel.send(f"Brain fried: {str(e)[:1800]}")

    await bot.process_commands(message) # CRITICAL - KEEP THIS LAST

# ===== START BOTH FLASK + BOT =====
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
