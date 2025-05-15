import os
import discord
import random
import requests
from discord.ext import commands
from flask import Flask
from threading import Thread

# ========================
# BOT SETUP
# ========================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

MAIN_IP = "PLAY.HUBMC.FUN"
OTHER_IPS = ["HUBMC.XYZ", "HUBMC.PRO"]
SERVER_IPS = [MAIN_IP] + OTHER_IPS

# ========================
# FLASK KEEP-ALIVE SERVER
# ========================
app = Flask('')

@app.route('/')
def home():
    return "Minecraft IP Bot is running! Server IPs: " + ", ".join(SERVER_IPS)

def run():
    app.run(host='0.0.0.0', port=8080)

# ========================
# BOT COMMANDS & EVENTS
# ========================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"MC Server: {random.choice(SERVER_IPS)}"
    ))
    print(f'Bot is ready as {bot.user}')

@bot.command()
async def ip(ctx):
    """Get all server IPs"""
    embed = discord.Embed(
        title="🏠 Minecraft Server IPs",
        description=f"*Main IP:* {MAIN_IP}\n\n" +
                    "*Other IPs:*\n" +
                    "\n".join([f"• {ip}" for ip in OTHER_IPS]),
        color=0x3498db
    )
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx, ip: str = None):
    """Check server status (optional: specify IP)"""
    try:
        target_ip = ip or random.choice(SERVER_IPS)
        response = requests.get(f"https://api.mcsrvstat.us/2/{target_ip}")
        data = response.json()

        if data['online']:
            status = "🟢 ONLINE"
            players = f"{data['players']['online']}/{data['players']['max']}"
            version = data.get('version', 'Unknown')

            embed = discord.Embed(
                title=f"{status} - {target_ip}",
                color=0x2ecc71
            )
            embed.add_field(name="Players", value=players)
            embed.add_field(name="Version", value=version)

            if 'motd' in data:
                motd = "\n".join(data['motd']['clean'])
                motd = motd.strip().removeprefix('kk').removesuffix('kk').strip()
                if motd:
                    embed.add_field(name="Message", value=motd, inline=False)
        else:
            embed = discord.Embed(
                title="🔴 SERVER OFFLINE",
                description=f"The server {target_ip} is currently offline",
                color=0xe74c3c
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠ Error checking status: {str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    triggers = [
        'ip?', 'server ip', 'what is the ip',
        'minecraft server', 'how to join',
        'hubmc', 'mc ip', 'whats the ip', 
        'what is the ip?', 'ip kya hen?',
        'ip', 'IP'
    ]
    
    if (any(trigger in message.content.lower() for trigger in triggers) 
        and not message
