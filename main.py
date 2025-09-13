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

FIRE_EMOJI = "<a:Fire:1416306773505085462>"
BOW_EMOJI = "<a:1079008620106240052:1416310758806917211>"
THUMBNAIL_URL = "https://imgur.com/Dv1sUPb.png"

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
        target_ips = [ip] if ip else SERVER_IPS
        online_data = None
        chosen_ip = None

        for test_ip in target_ips:
            try:
                data = requests.get(f"https://api.mcsrvstat.us/2/{test_ip}", timeout=2).json()
                if data.get('online'):
                    online_data = data
                    chosen_ip = test_ip
                    break
            except:
                continue

        if online_data:
            players = f"{online_data['players']['online']}/{online_data['players']['max']}"
            version = online_data.get('version', 'Unknown')
            motd = "\n".join(online_data.get('motd', {}).get('clean', []))
            motd = motd.strip().removeprefix('kk').removesuffix('kk').strip()

            embed = discord.Embed(title=f"🟢 ONLINE – {chosen_ip}", color=0x2ecc71)
            embed.add_field(name="Players", value=players)
            embed.add_field(name="Version", value=version)
            if motd:
                embed.add_field(name="Message", value=motd, inline=False)
        else:
            embed = discord.Embed(title="🔴 SERVER OFFLINE", description="All servers are currently offline.", color=0xe74c3c)

        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠ Error checking status: {e}")

# ================
# ABOUT OWNER
# ================
CROWN_EMOJI = "<:image:1416311728437985352>"
CROWN_ICON = "https://i.imgur.com/Dv1sUPb.png"
OWNER_PFP = "https://imgur.com/Dv1sUPb.png"
BANNER_IMG = "https://yourdomain.com/banner.png"

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

    if message.channel.category and message.channel.category.name.upper() == "INFORMATION":
        return

    content = message.content.lower()

    responses = {
        "who is the owner": "👑 The owner of HubMC is **Shiva**.",
        "what is the ip": f"**{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}**\n{BOW_EMOJI} **IP:** `{MAIN_IP}`\n{BOW_EMOJI} **PORT:** `{PORT}`",
        "hubmc ": f"**{FIRE_EMOJI} HubMC IP Address {FIRE_EMOJI}**\n{BOW_EMOJI} **IP:** `{MAIN_IP}`\n{BOW_EMOJI} **PORT:** `{PORT}`",
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
