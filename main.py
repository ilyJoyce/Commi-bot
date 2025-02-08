import discord  # type: ignore
from discord.ext import commands  # type: ignore
from discord import app_commands  # type: ignore
from discord.ext import tasks, commands  # type: ignore
import asyncio
from datetime import datetime
from iniconfig import IniConfig

config = IniConfig("config.ini")
wordlist = IniConfig("wordlist.ini")

TOKEN = config.get("config", "token")
BOT_HOST = config.get("config", "bot_host")
CO_HOST = config.get("config", "co_host")
CHECK_INTERVAL = 10
DEAFEN_TIME_LIMIT = 60 * 20
VOICE_ACTIVITY_TIME_LIMIT = 60 * 45
MONITOR_CHANNEL_ID = 1335722013523710082
COMMUNISM_WORDLIST = wordlist.get("wordlist", "communism").split(",")

active_voice_clients = {}
deafened_users = {}
whitelist = {
    766992639916376064, 1141143333335465995, 871497360658800640, 729707718730055773,
    556889798170640384, 271324530901778433, 785989592158306365, 710432389943263283,
    1102328237889167470, 314760782187462657
}

# 766992639916376064 - teufelshirn
# 1141143333335465995 - 2nd account
# 871497360658800640 - Ashley
# 729707718730055773 - Joyce
# 556889798170640384 - Felix
# 271324530901778433 - Mara
# 785989592158306365 - Zoe
# 710432389943263283 - Leyla
# 1102328237889167470 - Alki
# 314760782187462657 - Ratte

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.typing = False
async def get_prefix(bot, message):
    raw_content = message.content.lower()
    if raw_content.startswith("ussr:"):
        return message.content[:5]
    return "ussr:"
bot = commands.Bot(case_insensitive=True, command_prefix=get_prefix, intents=intents)
bot.remove_command("help")
spam_ss = False

last_message_time = 0
cooldown_time = 2




@bot.event
async def on_ready():
    target_user = await bot.fetch_user(BOT_HOST)
    print(f"Eingeloggt als {bot.user}")
    await target_user.send(
        f"🆙 **BOT-START:** Kommi Bot wurde erfolgreich gestartet\n"
        f"------------------------------------------------------------------------------------\n"
    )
    check_deafened_users.start()

    with open("/home/home/bot/pfp.gif", "rb") as f:
        await bot.user.edit(avatar=f.read())


@bot.command()
async def ping(ctx):
    """Antwortet mit Pong!"""
    await ctx.send("🏓 Pong!")

@bot.command()
async def ussr(ctx, member: discord.Member = None):
    if ctx.author.guild_permissions.ban_members:
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            active_voice_clients[ctx.guild.id] = vc

            vc.play(discord.FFmpegPCMAudio("ussr.mp3"))
            while vc.is_playing():
                await asyncio.sleep(1)

            if ctx.guild.id in active_voice_clients:
                del active_voice_clients[ctx.guild.id]
            await vc.disconnect()
        else:
            await ctx.send("Du musst in nem VC sein du Schlumpf~ UwU")
    else:
        await ctx.send("Du hast leider nicht die Erlaubnis den command zu nutzen, nya~ >w<")

@bot.command()
async def es_nervt(ctx, member: discord.Member = None):
    if ctx.author.guild_permissions.ban_members:
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            active_voice_clients[ctx.guild.id] = vc

            vc.play(discord.FFmpegPCMAudio("ashley.mp3"))
            while vc.is_playing():
                await asyncio.sleep(1)

            if ctx.guild.id in active_voice_clients:
                del active_voice_clients[ctx.guild.id]
            await vc.disconnect()
        else:
            await ctx.send("Du musst in nem VC sein du Schlumpf~ UwU")
    else:
        await ctx.send("Du hast leider nicht die Erlaubnis den command zu nutzen, nya~ >w<")

@bot.command()
async def stop(ctx):
    if ctx.author.guild_permissions.ban_members:    
        if ctx.guild.id in active_voice_clients:
            vc = active_voice_clients[ctx.guild.id]
            
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()

            del active_voice_clients[ctx.guild.id]

            await ctx.send("Sowjetische Propaganda wurde beendet~ >:3")
        else:
            await ctx.send("Ich bin doch gar nicht in nem Voice-Channel, Kamerad~ :3")
    else:
        await ctx.send("Du hast leider nicht die Erlaubnis den command zu nutzen, nya~ >w<")

@bot.command()
async def spam(ctx, member: discord.Member, *, message: str = "SOZIALISMUS!!! ~w~"):
    global spam_ss
    bot_host = await bot.fetch_user(BOT_HOST)
    co_host = await bot.fetch_user(CO_HOST)
    if ctx.author == bot_host or ctx.author.id == co_host:
        if member:
            spam_ss = True
            await ctx.send(f"Spamming {member.mention}, mit Nachricht: '{message}' gestartet!")
            while spam_ss:
                await member.send(message)
                await asyncio.sleep(4)
        else:
            await ctx.send("Kein:e Benutzer:in angegeben~ >w<")
    else:
        await ctx.send("Du bist leider kein:e Entwickler:in des Bots~ >w<")

@bot.command()
async def stop_spam(ctx):
    global spam_ss
    bot_host = await bot.fetch_user(BOT_HOST)
    co_host = await bot.fetch_user(CO_HOST)
    if ctx.author == bot_host or ctx.author == co_host:
        spam_ss = False
        await ctx.send("Spamming gestoppt!")
    else:
        await ctx.send("Du bist leider kein:e Entwickler:in des Bots~ >w<")


@bot.command()
async def disconnect(ctx, member: discord.Member, server_id: int = None):
    if not isinstance(ctx.channel, discord.DMChannel):
        server = ctx.guild
    else:
        if not server_id:
            await ctx.send("Bitte gib mir die Server-ID, wo du den/die Benutzer:in aus dem Channel schmeißn willst~ UwU Zum Beispiel: `ussr:bumm @user 123456789012345678`.")
            return
        server = bot.get_guild(server_id)
        if not server:
            await ctx.send(f"Kann den Server mit ID {server_id} nicht finden! Überprüf die ID nochmal und versuch es erneut~ ^w^")
            return

    member_permissions = server.get_member(ctx.author.id)
    if not member_permissions or not member_permissions.guild_permissions.move_members:
        await ctx.send("Du hast leider nicht die Erlaubnis, Mitglieder zu verschieben~ >:3")
        return

    if member.voice and member.voice.channel:
        channel = member.voice.channel

        vc = await channel.connect()
        active_voice_clients[ctx.guild.id] = vc
        vc.play(discord.FFmpegPCMAudio("disconnected.mp3"))
        while vc.is_playing():
                await asyncio.sleep(0.1)

        if member.voice and member.voice.channel == channel:
            await member.move_to(None)
            await ctx.send(f"Ich hab {member.mention} aus dem Channel geschmießen ^w^.")
        else:
            await ctx.send(f"W-was? {member.mention} hat sich einfach verpisst? >w<")

        if ctx.guild.id in active_voice_clients:
                del active_voice_clients[ctx.guild.id]
        await vc.disconnect()
    else:
        await ctx.send(f"{member.mention} ist nicht mal in nem Channel! Ts-ts~ >:3")

@bot.command()
async def move(ctx, member: discord.Member, channel_id: int = None):
    if not isinstance(ctx.channel, discord.DMChannel):
        server = ctx.guild
    else:
        await ctx.send("Bitte gib mir die Channel-ID, wohin du den/die Benutzer:in verschieben willst~ UwU Zum Beispiel: `ussr:bumm @user 123456789012345678`.")
        return

    member_permissions = server.get_member(ctx.author.id)
    if not member_permissions or not member_permissions.guild_permissions.move_members:
        await ctx.send("Du hast leider nicht die Erlaubnis, Mitglieder zu verschieben~ >:3")
        return

    current_channel_id = member.voice.channel

    if not member.voice or not member.voice.channel:
        await ctx.send(f"{member.mention} ist nicht mal in nem Channel! Ts-ts~ >:3")
        return

    target_channel = server.get_channel(channel_id)
    if not target_channel or not isinstance(target_channel, discord.VoiceChannel):
        await ctx.send("Ich kann diesen Channel nicht finden oder es ist kein Voice-Channel~ >w<")
        return

    vc = await current_channel_id.connect()
    active_voice_clients[ctx.guild.id] = vc
    vc.play(discord.FFmpegPCMAudio("auto.mp3"))
    await asyncio.sleep(4.35)
    await member.move_to(target_channel)
    await ctx.send(f"Ich hab {member.mention} nach {target_channel.name} verschoben~ ^w^.")
    while vc.is_playing():
        await asyncio.sleep(0.1)

    if ctx.guild.id in active_voice_clients:
        del active_voice_clients[ctx.guild.id]
    await vc.disconnect()

@bot.command()
async def bumm(ctx, member: discord.Member, server_id: int = None):
    if not isinstance(ctx.channel, discord.DMChannel):
        server = ctx.guild
    else:
        if not server_id:
            await ctx.send("Bitte gib mir die Server-ID, wo du den/die Benutzer:in aus dem Channel schmeißn willst~ UwU Zum Beispiel: `ussr:bumm @user 123456789012345678`.")
            return
        server = bot.get_guild(server_id)
        if not server:
            await ctx.send(f"Kann den Server mit ID {server_id} nicht finden! Überprüf die ID nochmal und versuch es erneut~ ^w^")
            return

    member_permissions = server.get_member(ctx.author.id)
    if not member_permissions or not member_permissions.guild_permissions.move_members:
        await ctx.send("Bumm :3")
        return

    if member.voice and member.voice.channel:
        channel = member.voice.channel

        vc = await channel.connect()
        active_voice_clients[ctx.guild.id] = vc
        vc.play(discord.FFmpegPCMAudio("verpiss-dich.mp3"))
        await asyncio.sleep(1.8)

        if member.voice and member.voice.channel == channel:
            await member.move_to(None)
            await ctx.send(f"Ich hab {member.mention} aus dem Channel geschmießen ^w^.")
            await asyncio.sleep(0.8)
        else:
            await ctx.send(f"W-was? {member.mention} hat sich einfach verpisst? >w<")

        if ctx.guild.id in active_voice_clients:
                del active_voice_clients[ctx.guild.id]
        await vc.disconnect()
    else:
        await ctx.send(f"{member.mention} ist nicht mal in nem Channel! Ts-ts~ >:3")


@bot.command(aliases=["lgbt", "furry"])
async def gay(ctx):
    """GAY!"""
    await ctx.send(
        f"⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠛⠛⢛⣿⣿⣿⣿⣿⣿⣿⠟⣁⣤⠹⣿⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⡿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⣉⣤⣶⣿⠏⣴⣿⣿⣿⣿⣿⡿⠛⣡⣾⣿⣿⡆⢻⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⠁⣶⣶⣶⣦⣤⣭⣉⡛⠻⢿⣿⣿⣿⡿⢋⣴⣿⣿⣿⣿⠃⠼⠿⠿⠿⣿⠿⢋⣴⣾⣿⣿⣿⣿⣷⠘⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⡆⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣍⠻⠟⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠸⢿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣧⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡂⣻⣿⣿⣿⣿⣿⣿⣿⣁⣙⡛⠛⠛⠃⢘⣿⣿⣿⣿⣿⣿⣿⠃⣿⣿⣿⣿\n"
        f"⣿⣿⠏⠙⢋⣥⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿\n"
        f"⣿⠏⣸⣶⣿⣿⣧⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢠⣿⣿⣿⣿\n"
        f"⣿⠀⣿⣿⣿⣿⣿⣆⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢸⣿⣿⣿⣿\n"
        f"⣿⠀⣿⣿⣿⣿⣿⣿⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⠿⢿⣿⣿⠛⠛⠛⠻⠿⠿⠿⠿⠿⣿⣿⣿⠇⣿⣿⣿⣿⣿\n"
        f"⣿⣆⠩⣿⣿⣿⣿⣿⣷⠘⣿⣿⣿⣯⡅⢠⣶⣶⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⣶⣦⠰⣦⡼⢰⣿⣿⣿⣿⣿\n"
        f"⣿⣿⣆⠙⣿⣿⣿⣿⣿⣧⡈⢿⣿⣿⡇⣿⣿⣏⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⣹⣿⡇⢿⣷⣶⣬⣉⠻⢿⣿\n"
        f"⣿⣿⣯⠁⣈⠻⣿⣿⣿⠟⣋⣠⣍⣉⣃⠘⢿⣿⡄⠀⠀⠀⠀⢀⣼⣿⣿⣿⣷⡀⠀⠀⠀⠀⣠⣿⡿⢁⣿⣿⣿⣿⣿⠷⠆⢻\n"
        f"⣿⣿⣿⣷⡈⢿⣿⣿⣁⣘⡛⠻⠿⢿⣿⣷⣤⣿⣿⣶⣤⣤⣶⣿⣿⣿⣍⣭⣿⣿⡷⢖⣶⣾⣿⣿⣡⣾⣿⣿⣿⡄⢲⣶⣿⣿\n"
        f"⣿⣿⣿⣿⣷⠈⣿⣿⣿⣿⣿⣿⢃⣾⣿⣿⡿⠛⠫⠭⢉⣿⣿⡘⠛⣋⣤⣍⣛⣋⣥⣾⡟⢋⠫⠍⣹⣿⡿⣿⣿⡇⢸⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⠁⣿⣿⣿⣿⣿⠃⣾⣿⣿⣿⣶⣭⣷⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣽⣿⣿⡿⠋⣤⣌⠹⠇⣸⣿⣿⣿\n"
        f"⣿⣿⣿⢿⠏⣼⣿⣿⣿⣿⣿⠸⠟⣉⣴⣬⡉⢉⠉⣉⣭⣍⡙⢿⣿⣿⣿⣿⣿⣿⠿⠿⠛⢛⣋⣡⣴⣿⣿⣿⣷⣶⣿⣿⣿⣿\n"
        f"⣿⣿⠃⢀⣾⣿⣿⣿⣿⣿⣯⣤⣾⣿⣿⡿⢡⡏⣸⣿⣿⣿⣿⣦⣙⣿⣿⣿⣿⠃⠸⠾⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⠏⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠴⢻⠀⣿⣿⣿⣿⣿⣿⠘⣿⣿⣟⡀⠠⠈⣘⣿⣷⣦⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠖⢂⣴⣿⡄⣿⣿⣿⣿⣿⣿⡆⢻⣿⣷⣄⣄⣙⠻⣿⣿⣿⣧⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢃⣴⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣷⠘⣿⣿⣿⣿⠀⣤⣸⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⡄⢻⣿⣿⣿⣿⣿⣿⣿⣿⠇⡾⢿⣿⣿⣿⡇⡀⢿⣿⣿⣿⣿⣿⡆⢹⣿⡇⠈⠀⣿⣿⣿⣿⣿⡇⢻⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⠙⠣⠘⣿⣿⣿⣿⣿⣿⣿⣿⣀⡁⠸⣿⣿⡿⢁⣧⠘⣿⣿⣿⣿⣿⣿⡄⢿⣷⡇⢿⣿⣿⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣧⡐⢆⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡦⠙⣋⣴⣿⣿⡄⢹⣿⣿⣿⣿⣿⣷⠘⣿⡇⢸⣿⣿⣿⣿⣿⡇⣼⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⣷⣄⠑⣌⠻⣿⣿⣿⣿⣿⠟⢋⣴⣾⣿⣿⢿⣿⣿⡀⢿⣿⣿⣿⣿⣿⣧⠹⣧⢸⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣷⣦⣉⠒⠭⠟⠟⢁⣴⣿⣿⣿⣿⣿⣦⣍⡙⠳⡈⢿⣿⣿⣿⣿⣿⣆⢹⠈⣿⣿⣿⣿⣿⠂⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣿⣿⣷⠂⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⡈⠿⣿⣿⣿⣿⣿⡄⠀⣿⣿⣿⣿⣿⠀⣤⣍⣙⠻⢿⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣿⣿⠁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠙⣿⣿⣿⣿⣷⠀⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣦⡌⢻⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣿⡏⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡈⢿⣿⣿⣿⣇⢹⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣆⠻⣿\n"
        f"⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⢻⣿⣿⣿⡄⢿⣿⣿⣿⢰⣿⣿⣿⣿⣿⣿⣿⣆⠹\n"
        f"⣿⣿⣿⣿⣿⣿⣇⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⢿⣿⣿⣷⡈⢿⣿⡏⢸⣿⣿⣿⣿⣿⣿⣿⣿⡆\n"
        f"⣿⣿⣿⣿⣿⣿⠏⣀⠰⠹⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠘⣿⣿⣿⣷⣌⠻⣧⣈⣉⡛⠻⣿⣿⣿⣿⡿⢀\n"
        f"⣿⣿⣿⣿⣿⣿⠀⢿⣷⣌⠑⢍⡻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⢻⣿⣿⣿⣿⣧⠘⣿⣿⣿⣷⡌⢻⣿⠏⣠⣾\n"
        f"⣿⣿⣿⣿⣿⣿⣦⣌⡙⠛⠛⠆⠈⠒⢝⡻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿⣿⣿⠀⣴⣾⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣍⡓⠾⣯⣿⣟⣛⣛⣻⣿⣿⠿⠂⢼⣿⣿⣿⣿⣿⣿⠃⣾⣿⣿⣿⠟⢰⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣬⣍⣉⣉⣉⣥⣤⣾⣷⡈⠫⣽⣿⣿⠿⢁⣌⣉⣉⣉⣠⣴⣿⣿⣿⣿⣿\n"
        f"⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣶⣶⡿⣿⣿⠿⢿⣿⣿⣿⣿⣿⣿⣿\n"
    )


@bot.command()
async def greet(ctx, member: discord.Member = None):
    """Begrüßt einen Benutzer mit Ping"""
    if member is None:
        member = ctx.author

    await ctx.send(f"👋 Привет, {member.mention}!")


@bot.command(aliases=["help"])
async def commands(ctx):
    """List all commands"""
    embed = discord.Embed(
        title="☭ Commi Bot Commands ☭",
        description="Hier sind alle commands aufgelistet!",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Communism Forever! ☭")

    embed.add_field(name="📌 Name", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="💡 Präfix", value="ussr:", inline=False)

    embed.add_field(
        name="🔧 Commands:",
        value="**ping** -> pong\n**info** -> Zeigt generelle Infos zum bot.\n**gay** -> GAY!\n**greet** `<user-ping>` -> begruesst einen User.\n**kommunismus** -> erklaert den Kommunismus.",
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(aliases=["about"])
async def info(ctx):
    """Zeigt Informationen über den Commi Bot an"""
    embed = discord.Embed(
        title="☭ Commi Bot Info ☭",
        description="Hier sind alle wichtigen Infos über mich!",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Communism Forever! ☭")

    embed.add_field(name="📌 Name", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="💡 Präfix", value="ussr:", inline=False)

    embed.add_field(
        name="🔧 Funktionen",
        value="✅ Automatische Moderation\n✅ Kommunismus-Propaganda\n✅ Überwachung von Voice-Chat-Aktivitäten\n✅ Slash commands",
        inline=False
    )

    embed.add_field(name="🌍 Server", value=f"{
                    len(bot.guilds)} Server", inline=True)
    embed.add_field(name="👥 Mitglieder", value=f"{
                    sum(g.member_count for g in bot.guilds)} Mitglieder", inline=True)

    embed.set_image(url="https://c.tenor.com/KOI-kAqLStgAAAAd/tenor.gif")

    await ctx.send(embed=embed)


@app_commands.command(name="info", description="Zeigt Informationen über den Commi Bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="☭ Commi Bot Info ☭",
        description="Hier sind alle wichtigen Infos über mich!",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=interaction.client.user.avatar.url)
    embed.set_footer(text="Communism Forever! ☭")

    embed.add_field(
        name="📌 Name", value=interaction.client.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=interaction.client.user.id, inline=True)
    embed.add_field(name="💡 Präfix", value="`ussr:`", inline=False)

    embed.add_field(
        name="🔧 Funktionen",
        value="✅ Automatische Moderation\n✅ Kommunismus-Propaganda\n✅ Überwachung von Voice-Chat-Aktivitäten\n✅ Slash commands",
        inline=False
    )

    embed.add_field(name="🌍 Server", value=f"{
                    len(interaction.client.guilds)} Server", inline=True)
    embed.add_field(name="👥 Mitglieder", value=f"{sum(
        g.member_count for g in interaction.client.guilds)} Mitglieder", inline=True)

    embed.set_image(url="https://c.tenor.com/KOI-kAqLStgAAAAd/tenor.gif")

    await interaction.response.send_message(embed=embed)

bot.tree.add_command(info)


@bot.command()
async def kommunismus(ctx):
    embed = discord.Embed(
        title="☭ Was ist Kommunismus? ☭",
        description=(
            "Kommunismus ist eine politische und wirtschaftliche Ideologie, die auf "
            "Gleichheit, Gemeinschaftseigentum und die Abschaffung der Klassenunterschiede abzielt. "
            "Das Ziel ist eine Gesellschaft ohne Privateigentum an Produktionsmitteln, "
            "in der alle Menschen gleichberechtigt am Wohlstand teilhaben."
        ),
        color=discord.Color.red()
    )

    embed.add_field(
        name="🛠️ Kerngedanken",
        value=(
            "- **Gleichheit**: Keine soziale Klasse, jeder hat die gleichen Rechte.\n"
            "- **Gemeinsames Eigentum**: Keine privaten Produktionsmittel, alles gehört dem Volk.\n"
            "- **Planwirtschaft**: Die Wirtschaft wird zentral geplant, um Bedürfnisse zu erfüllen.\n"
            "- **Internationale Solidarität**: Klassenkämpfe enden, wenn Arbeiter:in weltweit vereint sind."
        ),
        inline=False
    )

    embed.add_field(
        name="📜 Wichtige Theoretiker",
        value=(
            "- **Karl Marx & Friedrich Engels** – Verfasser des Kommunistischen Manifests (1848)\n"
            "- **Wladimir Lenin** – Führte die Russische Revolution (1917) an\n"
            "- **Mao Zedong** – Führte den Kommunismus in China ein"
        ),
        inline=False
    )

    embed.set_footer(text="Kommunismus – Eine Idee für eine gerechtere Welt.")
    embed.set_thumbnail(url=bot.user.avatar.url)

    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    global last_message_time

    if message.author == bot.user:
        return

    try:
        target_user = await bot.fetch_user(BOT_HOST)
    except Exception as e:
        print(f"❌ Failed to fetch user: {e}")
        return

    if message.channel.id == MONITOR_CHANNEL_ID:
        current_time = message.created_at.timestamp()
        message_content = message.content.lower()
        detected_type = None

        if message.author.id == target_user:
            if any(term in message_content for term in COMMUNISM_WORDLIST):
                await message.reply("COMMUNISM FOREVER <a:ussr:1335731521352503358>")
                detected_type = "Communism-related terms detected"
            else:
                await message.reply("Angenommen ✅")
                detected_type = "self detected"
        elif ("joyce" in message_content or "ashley" in message_content) and "rechts" in message_content:
            await message.reply("RECHTS UND LINKS MISCHEN SICH NICHT GUT 😡")
            detected_type = "Ashley + Rechts or Joyce + Rechts detected"
        elif "joyce" in message_content or "ashley" in message_content:
            await message.reply("Angenommen ✅")
            detected_type = "Joyce or Ashley detected"
        elif any(term in message_content for term in ["links", "left", "nazis verbrennen"]):
            await message.reply("Angenommen ✅")
            detected_type = "Leftist terms detected"
        elif "nino bannen" in message_content:
            await message.reply("Angenommen ✅")
            detected_type = "Ban request for Nino detected"
        elif any(term in message_content for term in COMMUNISM_WORDLIST):
            await message.reply("COMMUNISM FOREVER <a:ussr:1335731521352503358>")
            detected_type = "Communism-related terms detected"
        else:
            if current_time - last_message_time > cooldown_time:
                await message.reply("Abgelehnt ❌")
                detected_type = "General rejection"

        last_message_time = current_time

        if detected_type and target_user:
            try:
                await target_user.send(
                    f"🔔 **ALARM:** {detected_type}\n"
                    f"👤 **BENUTZER:** {
                        message.author.mention} (`{message.author.id}`)\n"
                    f"📜 **NACHRICHT:** {message.content}\n"
                    f"📅 **UHRZEIT:** {message.created_at.strftime(
                        '%H:%M Uhr %d.%m.%Y')}\n"
                    f"🔗 **LINK:** https://discord.com/channels/{
                        message.guild.id}/{message.channel.id}/{message.id}\n"
                    f"------------------------------------------------------------------------------------\n"
                )
            except discord.Forbidden:
                print(f"Could not send a DM to {target_user} (Forbidden).")
            except Exception as e:
                print(f"Error sending DM: {e}")

    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    """Track when a user deafens themselves."""
    current_time = asyncio.get_event_loop().time()

    if after.self_deaf and not before.self_deaf:
        deafened_users[member.id] = current_time
    elif not after.self_deaf:
        deafened_users.pop(member.id, None)

    if after.channel is None:
        deafened_users.pop(member.id, None)


@tasks.loop(seconds=CHECK_INTERVAL)
async def check_deafened_users():
    current_time = asyncio.get_event_loop().time()
    target_user = await bot.fetch_user(BOT_HOST)

    for guild in bot.guilds:
        for member in guild.members:
            if not member.voice:
                continue

            if member.id not in deafened_users and member.voice.self_deaf:
                deafened_users[member.id] = current_time

            time_since_deafened = current_time - deafened_users.get(member.id, 0)

            if member.id in whitelist:
                continue

            afk_channel = guild.get_channel(1335686372631117926)
            if member.voice.channel == afk_channel:
                continue

            if (member.voice.self_deaf and time_since_deafened >= DEAFEN_TIME_LIMIT):
                try:
                    if afk_channel:
                        await member.move_to(afk_channel, reason="Zu lange taub oder keine Aktivität")
                        print(
                            f"{member.display_name} wurde in den AFK-Channel verschoben.")

                        try:
                            await member.send("Du wurdest aus dem Voice-Channel entfernt wegen Inaktivität.")
                            try:
                                await target_user.send(
                                    f"👤 **BENUTZER:** {
                                        member.mention} (`{member.id}`)\n"
                                    f"📜 **NACHRICHT:** {
                                        member.display_name} wurde aus dem Voice-Channel entfernt wegen Inaktivität.\n"
                                    f"📅 **UHRZEIT:** {datetime.now().strftime(
                                        '%H:%M Uhr %d.%m.%Y')}\n"
                                    f"------------------------------------------------------------------------------------\n"
                                )
                            except discord.Forbidden:
                                print(f"DM nicht möglich an {
                                      target_user.display_name}.")
                                await member.send("Es konnte keine DM an {target_user.display_name} geschickt werden.")
                        except discord.Forbidden:
                            print(f"DM nicht möglich an {
                                  member.display_name}.")

                        deafened_users.pop(member.id, None)

                except discord.Forbidden:
                    print(f"Keine Rechte, um {
                          member.display_name} zu verschieben.")
                except Exception as e:
                    print(f"Fehler beim Verschieben von {
                          member.display_name}: {e}")
                    await target_user.send(
                        f"❌ **FEHLER:** Fehler beim Verschieben von {
                            member.display_name}: {e}\n"
                        f"------------------------------------------------------------------------------------\n"
                    )

bot.run(TOKEN)
