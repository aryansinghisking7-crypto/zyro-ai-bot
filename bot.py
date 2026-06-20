import discord
from discord.ext import commands
import os
import asyncio
from groq import Groq, RateLimitError, APIError

# Load keys from Railway Variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Safety check
if not DISCORD_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing DISCORD_TOKEN or GROQ_API_KEY in environment variables")

# Init Groq client
client = Groq(api_key=GROQ_API_KEY)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print('ZYRO AI on Groq is online!')
    await bot.change_presence(activity=discord.Game(name="Type!ask <question>"))

@bot.command(name='ask')
@commands.cooldown(1, 3, commands.BucketType.user) # 1 use per 3 sec per user
async def ask(ctx, *, question: str = None):
    if question is None:
        await ctx.send("Ask me something: `!ask what is AI?`")
        return
        
    try:
        async with ctx.typing():
            # Groq call
            chat = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are ZYRO AI, a helpful Discord bot. Keep replies concise and friendly."},
                    {"role": "user", "content": question}
                ],
                model="llama-3.1-8b-instant", # Fast + free model
                temperature=0.7,
                max_tokens=800 # Prevent huge replies
            )
            
            text = chat.choices[0].message.content.strip()
            
            # Discord 2000 char limit fix
            if len(text) > 2000:
                chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
                    await asyncio.sleep(0.5) # Prevent rate limit
            else:
                await ctx.send(text)
                
    except RateLimitError:
        await ctx.send("⚠️ I'm being rate limited by Groq. Try again in a few seconds.")
    except APIError as e:
        await ctx.send(f"🚫 Groq API error: `{str(e)}`")
    except Exception as e:
        await ctx.send(f"❌ Unexpected error: `{str(e)}`")
        print(f"Error in!ask: {e}")

@ask.error
async def ask_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Slow down! Try again in {error.retry_after:.1f}s")

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! `{round(bot.latency * 1000)}ms`')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return # Ignore unknown commands
    print(f"Command error: {error}")

bot.run(DISCORD_TOKEN)
