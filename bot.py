import discord
from discord.ext import commands
import google.generativeai as genai
import os

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    print("ERROR: Missing DISCORD_TOKEN or GEMINI_API_KEY")
    exit()

genai.configure(api_key=GEMINI_API_KEY)

# Auto-pick a working model instead of hardcoding
def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-2.0-flash' in m.name:
                    print(f"Using model: {m.name}")
                    return genai.GenerativeModel(m.name)
                if 'gemini-1.5-flash' in m.name:
                    print(f"Using model: {m.name}")
                    return genai.GenerativeModel(m.name)
    except Exception as e:
        print(f"Model listing failed: {e}")
    # Fallback to most common working name
    print("Using fallback: gemini-2.0-flash-exp")
    return genai.GenerativeModel('gemini-2.0-flash-exp')

model = get_working_model()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('ZYRO AI is online!')

@bot.command(name='ask')
async def ask(ctx, *, question):
    try:
        async with ctx.typing():
            response = model.generate_content(question)
            text = response.text
            
            # Handle Discord 2000 char limit
            for chunk in [text[i:i+2000] for i in range(0, len(text), 2000)]:
                await ctx.send(chunk)
                
    except Exception as e:
        await ctx.send(f"Gemini error: {str(e)}")
        print(f"Error: {e}")

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

bot.run(DISCORD_TOKEN)
