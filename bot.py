import discord
from discord import app_commands
import os
from groq import Groq
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Fake web server to keep Render happy
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ZYRO is alive')

def run_fake_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# Your actual bot code below
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@client.event
async def on_ready():
    await tree.sync()
    print(f'✅ {client.user} online')

@tree.command(name="ask", description="Ask AI")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    try:
        res = groq.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.1-8b-instant"
        )
        await interaction.followup.send(res.choices[0].message.content[:2000])
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

client.run(os.environ.get("DISCORD_TOKEN"))
