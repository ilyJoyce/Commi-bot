import discord  # type: ignore
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks, commands  # type: ignore
import asyncio
from iniconfig import IniConfig

config = IniConfig("config.ini")
wordlist = IniConfig("wordlist.ini")

TOKEN = config.get("config", "token")
BOT_HOST = config.get("config", "bot_host")
CHECK_INTERVAL = 1
DEAFEN_TIME_LIMIT = 60 * 20
VOICE_ACTIVITY_TIME_LIMIT = 60 * 45
MONITOR_CHANNEL_ID = 1335722013523710082
COMMUNISM_WORDLIST = wordlist.get("wordlist", "communism").split(",")

deafened_users = {}
speaking_users = {}
whitelist = {
    766992639916376064, 1141143333335465995, 871497360658800640, 729707718730055773,
    556889798170640384, 271324530901778433, 785989592158306365, 710432389943263283,
    1102328237889167470, 
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

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.typing = False
bot = commands.Bot(command_prefix="ussr:", intents=intents)
bot.remove_command("help")

last_message_time = 0
cooldown_time = 2


@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}")
    check_deafened_users.start()
    try:
        synced = await bot.tree.sync()  # Sync slash commands
        print(f"✅ {len(synced)} Slash Commands synced!")
    except Exception as e:
        print(f"❌ Fehler beim Syncen: {e}")

    with open("/home/home/bot/pfp.gif", "rb") as f:
        await bot.user.edit(avatar=f.read())

@bot.command()
async def ping(ctx):
    """Antwortet mit Pong!"""
    await ctx.send("🏓 Pong!")

@bot.command()
async def greet(ctx, member: discord.Member = None):
    """Begrüßt einen Benutzer mit Ping"""
    if member is None:
        member = ctx.author
    
    await ctx.send(f"👋 Привет, {member.mention}!")

@bot.command(aliases=["help", "commands", "support", "about"])
async def info(ctx):
    """Zeigt Informationen über den Commi Bot an"""
    embed = discord.Embed(
        title="☭ Commi Bot Info ☭",
        description="Hier sind alle wichtigen Infos über mich!",
        color=discord.Color.red()  # USSR Red 😉
    )

    embed.set_thumbnail(url=bot.user.avatar.url)  # Bot's Avatar
    embed.set_footer(text="Communism Forever! ☭")

    # Bot Details
    embed.add_field(name="📌 Name", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="💡 Präfix", value="ussr:", inline=False)

    # Features
    embed.add_field(
        name="🔧 Funktionen",
        value="✅ Automatische Moderation\n✅ Kommunismus-Propaganda\n✅ Überwachung von Voice-Chat-Aktivitäten\n✅ Faire aufteilung von Nachrichten",
        inline=False
    )

    # Server & Member Count
    embed.add_field(name="🌍 Server", value=f"{len(bot.guilds)} Server", inline=True)
    embed.add_field(name="👥 Mitglieder", value=f"{sum(g.member_count for g in bot.guilds)} Mitglieder", inline=True)

    # Add a custom GIF or image (Optional)
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

    # Bot Details
    embed.add_field(name="📌 Name", value=interaction.client.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=interaction.client.user.id, inline=True)
    embed.add_field(name="💡 Präfix", value="`ussr:`", inline=False)

    # Features
    embed.add_field(
        name="🔧 Funktionen",
        value="✅ Automatische Moderation\n✅ Kommunismus-Propaganda\n✅ Überwachung von Voice-Chat-Aktivitäten\n✅ Faire aufteilung von Nachrichten",
        inline=False
    )

    # Server & Member Count
    embed.add_field(name="🌍 Server", value=f"{len(interaction.client.guilds)} Server", inline=True)
    embed.add_field(name="👥 Mitglieder", value=f"{sum(g.member_count for g in interaction.client.guilds)} Mitglieder", inline=True)

    # Add a custom GIF or image (Optional)
    embed.set_image(url="https://media.tenor.com/Lh01n6hzpLAAAAAd/communism.gif")

    await interaction.response.send_message(embed=embed)

bot.tree.add_command(info)


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
    """Track when a user starts/stops speaking or deafens themselves."""
    current_time = asyncio.get_event_loop().time()

    if after.self_deaf and not before.self_deaf:
        deafened_users[member.id] = current_time
    elif not after.self_deaf:
        deafened_users.pop(member.id, None)

    if after.channel and (before.self_mute != after.self_mute or before.self_deaf != after.self_deaf):
        speaking_users[member.id] = current_time

    if after.channel is None:
        speaking_users.pop(member.id, None)
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

            if member.id not in speaking_users:
                speaking_users[member.id] = current_time

            time_since_deafened = current_time - \
                deafened_users.get(member.id, 0)
            time_since_spoke = current_time - speaking_users.get(member.id, 0)

            if member.id in whitelist:
                continue

            afk_channel = guild.get_channel(1335686372631117926)
            if member.voice.channel == afk_channel:
                continue

            if (member.voice.self_deaf and time_since_deafened >= DEAFEN_TIME_LIMIT) or \
               (not member.voice.self_deaf and time_since_spoke >= VOICE_ACTIVITY_TIME_LIMIT):
                try:
                    if afk_channel:
                        await member.move_to(afk_channel, reason="Zu lange taub oder keine Aktivität")
                        print(
                            f"{member.display_name} wurde in den AFK-Channel verschoben.")

                        try:
                            await member.send("Du wurdest aus dem Voice-Channel entfernt wegen Inaktivität.")
                            await target_user.send(
                                f"👤 **BENUTZER:** {member.mention} (`{member.id}`)\n"
                                f"📜 **NACHRICHT:** {member.display_name} wurde aus dem Voice-Channel entfernt wegen Inaktivität.\n"
                                f"📅 **UHRZEIT:** {datetime.now().strftime('%H:%M Uhr %d.%m.%Y')}\n"
                                f"------------------------------------------------------------------------------------\n"
                            )
                        except discord.Forbidden:
                            print(f"DM nicht möglich an {
                                  member.display_name}.")

                        deafened_users.pop(member.id, None)
                        speaking_users.pop(member.id, None)

                except discord.Forbidden:
                    print(f"Keine Rechte, um {
                          member.display_name} zu verschieben.")
                except Exception as e:
                    print(f"Fehler beim Verschieben von {
                          member.display_name}: {e}")

bot.run(TOKEN)
