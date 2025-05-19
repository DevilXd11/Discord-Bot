Here’s your full script with the upgraded, roomier !about owner embed already in place.
(Only the owner block changed; everything else is unchanged.)

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

LOGO_URL = "PASTE-YOUR-LINK-HERE"   # ← drop your image link here

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
        type = discord.ActivityType.watching,
        name = f"MC Server: {random.choice(SERVER_IPS)}"
    ))
    print(f'Bot is ready as {bot.user}')

# ---------- Fancy !ip ----------
@bot.command()
async def ip(ctx):
    """Send all server IPs in a decorative embed"""
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

# ---------- Server status ----------
@bot.command()
async def status(ctx, ip: str = None):
    """Check server status (optional: specify IP)"""
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
@bot.command(name="about")
async def about_owner(ctx, *, subject: str = None):
    """Usage: !about owner"""
    if subject and subject.lower() == "owner":
        embed = discord.Embed(
            title="👑  *HUBMC OWNER PROFILE*",
            description=(
                "‣ Name:**  *Shiva*\n"
                "‣ Hometown:**  Navi Mumbai, India  🇮🇳\n"
                "‣ Role:**  Event Creator & Community Lead  🎉\n"
                "‣ Vision:**  Keep HUBMC fresh, fair & fun for everyone  🛠\n"
                "‣ Motto:**  “Play together, grow together!”  ✨\n"
                "\n"
                "I’m the mind behind every festival, head-hunt, and surprise drop you’ve loved so far.\n"
                "My DMs are *always open*—hit me up with ideas, feedback, or just to chill in voice!\n"
            ),
            color=0xf1c40f
        )

        # extra breathing room
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        embed.set_thumbnail(url=LOGO_URL)
        embed.set_footer(text="Made with ♥ in Navi Mumbai • See you in-game!")
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("Try !about owner 🙂")

# ---------- Message listener ----------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    triggers = [
        'ip?', 'server ip', 'what is the ip', 'minecraft server',
        'how to join', 'hubmc', 'mc ip', 'whats the ip',
        'what is the ip?', 'ip kya hen?', 'ip', 'IP'
    ]

    if (any(t in message.content.lower() for t in triggers)
        and not message.content.startswith(bot.command_prefix)):
        
        embed = discord.Embed(
            title="🎮 HUBMC Server Info",
            description=(
                "Here are the addresses you can use:\n\n"
                f"*Main:* {MAIN_IP}\n" +
                "\n".join([f"*Alt {i+1}:* {ip}" for i, ip in enumerate(OTHER_IPS)]) +
                "\n\nUse **!ip** anytime for this card, or **!status** to see if we’re online!"
            ),
            color=0x9b59b6
        )
        embed.set_thumbnail(url=LOGO_URL)
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# ========================
# START EVERYTHING
# ========================
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("ERROR: Discord token not found! Please add DISCORD_TOKEN in the Secrets tab!")
    exit(1)

print(f"Token found: {token[:10]}... Starting bot!")
Thread(target=run).start()
bot.run(token)

Next step: plug your public image URL into LOGO_URL, redeploy, and enjoy the slick new owner card!
