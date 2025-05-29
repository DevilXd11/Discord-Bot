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

MAIN_IP = "play.hubmc.fun"
PORT = "19132"
OTHER_IPS = ["hubmc.xyz", "hubmc.pro"]
SERVER_IPS = [MAIN_IP] + OTHER_IPS

FIRE_EMOJI = "<a:fire_gif:1376182475700703362>"
BOW_EMOJI = "<a:enchanted_bow:1376182511922708642>"
THUMBNAIL_URL = "https://i.imgur.com/GKmqhho.png"

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
# BOT EVENTS
# ========================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"MC Server: {random.choice(SERVER_IPS)}"
    ))
    print(f'Bot is ready as {bot.user}')

# ========================
# BOT COMMANDS
# ========================
@bot.command()
async def ip(ctx):
    embed = discord.Embed(color=0xFFA500)
    embed.description = (
        f"**{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}**\n\n"
        f"{BOW_EMOJI} **IP:** `{MAIN_IP}`\n"
        f"{BOW_EMOJI} **PORT:** `{PORT}`"
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx, ip: str = None):
    try:
        target_ip = ip or random.choice(SERVER_IPS)
        data = requests.get(f"https://api.mcsrvstat.us/2/{target_ip}").json()
        if data['online']:
            players = f"{data['players']['online']}/{data['players']['max']}"
            version = data.get('version', 'Unknown')
            embed = discord.Embed(title=f"🟢 ONLINE – {target_ip}", color=0x2ecc71)
            embed.add_field(name="Players", value=players)
            embed.add_field(name="Version", value=version)
            motd = "\n".join(data.get('motd', {}).get('clean', []))
            motd = motd.strip().removeprefix('kk').removesuffix('kk').strip()
            if motd:
                embed.add_field(name="Message", value=motd, inline=False)
        else:
            embed = discord.Embed(title="🔴 SERVER OFFLINE", description=f"The server {target_ip} is currently offline", color=0xe74c3c)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠ Error checking status: {e}")

# ================
# ABOUT OWNER
# ================
CROWN_EMOJI = "<:image:1374372573315469432>"
CROWN_ICON = "https://media.discordapp.net/attachments/1347455174645514364/1374024609589887006/dg.png"
OWNER_PFP = "https://i.imgur.com/ZX7wjcY.png"
BANNER_IMG = "https://yourdomain.com/banner.png"  # Optional

@bot.command(name="about")
async def about_owner(ctx, *, subject: str = None):
    if subject and subject.lower() == "owner":
        embed = discord.Embed(
            title=f"{CROWN_EMOJI} HUBMC OWNER PROFILE",
            description=(
                "‣ **Name:** Shiva\n"
                "‣ **Hometown:** Navi Mumbai, India 🇮🇳\n"
                "‣ **Role:** Event Creator & Community Lead 🎉\n"
                "‣ **Vision:** Keep HUBMC fresh, fair & fun for everyone 🛠\n"
                "‣ **Motto:** “Play together, grow together!” ✨\n\n"
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

# ========================
# AUTO RESPONSE TO QUESTIONS
# ========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Ignore channels in INFORMATION category
    if message.channel.category and message.channel.category.name.upper() == "INFORMATION":
        return

    content = message.content.lower()

    responses = {
        "who is the owner": "👑 The owner of HubMC is **Shiva**.",
        "what is the ip": f"**{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}**\n\n{BOW_EMOJI} **IP:** `{MAIN_IP}`\n{BOW_EMOJI} **PORT:** `{PORT}`",
        "hubmc": f"**{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}**\n\n{BOW_EMOJI} **IP:** `{MAIN_IP}`\n{BOW_EMOJI} **PORT:** `{PORT}`",
        "how to join": f"To join, use IP: `{MAIN_IP}` and Port: `{PORT}` in Minecraft.",
        "what is in survival": "🏕️ In Survival mode, you can:\n• Build & survive in the wild\n• Explore dungeons\n• Complete quests\n• PvE boss fights",
        "what is in pvp": "⚔️ In PvP mode, you can:\n• Battle players in arenas\n• Join ranked fights\n• Earn coins from kills\n• Use kits & enchantments"
    }

    sent = False
    for question, reply in responses.items():
        if question in content:
            embed = discord.Embed(description=reply, color=0xFFA500)
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(text=f"Requested by {message.author.name}", icon_url=message.author.avatar.url if message.author.avatar else None)
            await message.channel.send(embed=embed)
            sent = True
            break

    if not message.content.startswith(bot.command_prefix):
        triggers = ["ip?", "server ip", "minecraft server", "mc ip", "ip kya hen?", "ip"]
        if any(t in content for t in triggers) and not sent:
            embed = discord.Embed(
                description=f"**{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}**\n\n{BOW_EMOJI} **IP:** `{MAIN_IP}`\n{BOW_EMOJI} **PORT:** `{PORT}`",
                color=0xFFA500
            )
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(text=f"Requested by {message.author.name}", icon_url=message.author.avatar.url if message.author.avatar else None)
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

# ========================
# START BOT
# ========================
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("ERROR: Discord token not found! Please add DISCORD_TOKEN in the Secrets tab!")
    exit(1)

print(f"Token found: {token[:10]}... Starting bot!")
Thread(target=run).start()
bot.run(token)
