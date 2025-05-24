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

MAIN_IP   = "PLAY.HUBMC.FUN"
OTHER_IPS = ["HUBMC.XYZ", "HUBMC.PRO"]
SERVER_IPS = [MAIN_IP] + OTHER_IPS

LOGO_URL = "https://i.imgur.com/ZX7wjcY.png"  # <-- Add your HUBMC logo URL here (same as owner pfp if needed)

# ========================
# FLASK KEEP-ALIVE SERVER
# ========================
app = Flask(__name__)

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
        type = discord.ActivityType.watching,
        name = f"MC Server: {random.choice(SERVER_IPS)}"
    ))
    print(f'Bot is ready as {bot.user}')

@bot.command()
async def ip(ctx):
    embed = discord.Embed(
        title="🌐  HUBMC Network – Join the Adventure!",
        description=(
            "✨ *Main Address*\n"
            f"{MAIN_IP}\n\n"
            "🔗 *Alternate Addresses*\n" +
            "\n".join([f"{ip}" for ip in OTHER_IPS])
        ),
        color=0x00bcd4
    )
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_footer(text="See you in-game! 🏹")
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx, ip: str = None):
    try:
        target_ip = ip or random.choice(SERVER_IPS)
        data = requests.get(f"https://api.mcsrvstat.us/2/{target_ip}").json()

        if data['online']:
            players = f"{data['players']['online']}/{data['players']['max']}"
            version = data.get('version', 'Unknown')

            embed = discord.Embed(
                title=f"🟢 ONLINE – {target_ip}",
                color=0x2ecc71
            )
            embed.add_field(name="Players",  value=players)
            embed.add_field(name="Version",  value=version)

            motd = "\n".join(data.get('motd', {}).get('clean', []))
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
        await ctx.send(f"⚠ Error checking status: {e}")

# ---------- !about owner ----------
CROWN_EMOJI = "<:image:1374372573315469432>"
CROWN_ICON  = "https://media.discordapp.net/attachments/1347455174645514364/1374024609589887006/dg.png?ex=682d3463&is=
