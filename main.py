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

MAIN_IP   = "play.hubmc.fun"
PORT      = "19132"
OTHER_IPS = ["hubmc.xyz", "hubmc.pro"]
SERVER_IPS = [MAIN_IP] + OTHER_IPS

# Custom Emojis (Replace names with actual emoji names from your server)
FIRE_EMOJI = "<a:fire_gif:1376182475700703362>"
BOW_EMOJI  = "<a:enchanted_bow:1376182511922708642>"

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
        type=discord.ActivityType.watching,
        name=f"MC Server: {random.choice(SERVER_IPS)}"
    ))
    print(f'Bot is ready as {bot.user}')

@bot.command()
async def ip(ctx):
    embed = discord.Embed(
        title=f"{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}",
        color=0xFFA500
    )
    embed.add_field(name=f"{BOW_EMOJI} IP", value=f"`{MAIN_IP}`", inline=False)
    embed.add_field(name=f"{BOW_EMOJI} PORT", value=f"`{PORT}`", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
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
            embed.add_field(name="Players", value=players)
            embed.add_field(name="Version", value=version)

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
CROWN_ICON  = "https://media.discordapp.net/attachments/1347455174645514364/1374024609589887006/dg.png?ex=682d3463&is=682be2e3&hm=9311c2377716aa93ffc0d6c6ee03d5434dbf74fe569678503011bc37acfdf8b5&=&format=webp&quality=lossless&width=62&height=80"
OWNER_PFP   = "https://i.imgur.com/ZX7wjcY.png"
BANNER_IMG  = "https://yourdomain.com/banner.png"  # Optional banner image

@bot.command(name="about")
async def about_owner(ctx, *, subject: str = None):
    if subject and subject.lower() == "owner":
        embed = discord.Embed(
            title=f"{CROWN_EMOJI} HUBMC OWNER PROFILE",
            description=(
                "‣ Name:**  Shiva\n"
                "‣ Hometown:**  Navi Mumbai, India 🇮🇳\n"
                "‣ Role:**  Event Creator & Community Lead 🎉\n"
                "‣ Vision:**  Keep HUBMC fresh, fair & fun for everyone 🛠\n"
                "‣ Motto:**  “Play together, grow together!”** ✨\n\n"
                "I’m the mind behind every festival, head-hunt, and surprise drop you’ve loved so far.\n"
                "My DMs are always open—hit me up with ideas, feedback, or just to chill in voice!"
            ),
            color=0xf1c40f,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=" ", icon_url=CROWN_ICON)
        embed.set_thumbnail(url=OWNER_PFP)
        embed.set_image(url=BANNER_IMG)
        embed.set_footer(text="Made with ♥ in Navi Mumbai • See you in-game!")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Try !about owner 🙂")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    triggers = [
        'ip?', 'server ip', 'what is the ip', 'minecraft server',
        'how to join', 'hubmc', 'mc ip', 'whats the ip',
        'what is the ip?', 'ip kya hen?', 'ip', 'IP'
    ]

    if any(t in message.content.lower() for t in triggers) and not message.content.startswith(bot.command_prefix):
        embed = discord.Embed(
            title=f"{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}",
            color=0xFFA500
        )
        embed.add_field(name=f"{BOW_EMOJI} IP", value=f"`{MAIN_IP}`", inline=False)
        embed.add_field(name=f"{BOW_EMOJI} PORT", value=f"`{PORT}`", inline=False)
        embed.set_footer(text=f"Requested by {message.author.name}")
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
