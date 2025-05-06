import os
import discord
import requests
from discord.ext import commands
from flask import Flask
from threading import Thread

# ========================
# BOT SETUP
# ========================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
SERVER_IP = "hubmc.pro"  # Updated Minecraft server IP

# ========================
# FLASK KEEP-ALIVE SERVER
# ========================
app = Flask('')

@app.route('/')
def home():
    return "Minecraft IP Bot is running! Server: hubmc.pro"  # Updated

def run():
    app.run(host='0.0.0.0', port=8080)

# ========================
# BOT COMMANDS & EVENTS
# ========================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"MC Server: {SERVER_IP}"  # Auto-updated
    ))
    print(f'Bot is ready as {bot.user}')

@bot.command()
async def ip(ctx):
    """Get the server IP"""
    embed = discord.Embed(
        title="🏠 Minecraft Server IP",
        description=f"Connect using:\n`{SERVER_IP}`",  # Auto-updated
        color=0x3498db
    )
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    """Check server status"""
    try:
        response = requests.get(f"https://api.mcsrvstat.us/2/{SERVER_IP}")  # Auto-updated
        data = response.json()

        if data['online']:
            status = "🟢 ONLINE"
            players = f"{data['players']['online']}/{data['players']['max']}"
            version = data.get('version', 'Unknown')

            embed = discord.Embed(
                title=f"{status} - {SERVER_IP}",  # Auto-updated
                color=0x2ecc71
            )
            embed.add_field(name="Players", value=players)
            embed.add_field(name="Version", value=version)

            if 'motd' in data:
                motd = "\n".join(data['motd']['clean'])
                embed.add_field(name="Message", value=motd, inline=False)
        else:
            embed = discord.Embed(
                title="🔴 SERVER OFFLINE",
                description=f"The server {SERVER_IP} is currently offline",  # Auto-updated
                color=0xe74c3c
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠ Error checking status: {str(e)}")
@bot.event
async def on_message(message):
    if message.author == bot.user:  # Ignore self
        return

    triggers = [
        'ip?', 'server ip', 'what is the ip',
        'minecraft server', 'how to join',
        'hubmc', 'mc ip', 'whats the ip', 
        'what is the ip?', 'ip kya hen?',
        'ip', 'mc ip', 'hubmc', 'IP'
    ]
    
    # Check if message matches triggers AND isn't a bot command
    if (any(trigger in message.content.lower() for trigger in triggers) 
        and not message.content.startswith(bot.command_prefix)):
        await message.channel.send(
            f"🎮 Minecraft Server IP: {SERVER_IP}\n"
            f"Type !ip for details or !status to check if it's online!"
        )
    
    await bot.process_commands(message)  # Process commands normally

# ========================
# START EVERYTHING
# ========================
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("ERROR: Discord token not found! Please add DISCORD_TOKEN in the Secrets tab!")
    exit(1)

print(f"Token found: {token[:10]}... Starting bot!")
Thread(target=run).start()  # Start Flask server in background
bot.run(token)  # Start bot
@bot.event
async def on_error(event, *args):
    print(f"Error in {event}: {args}")
