import discord
from discord.ext import tasks, commands
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
}

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.typing = False
bot = commands.Bot(command_prefix="!", intents=intents)

last_message_time = 0
cooldown_time = 2


@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}")
    check_deafened_users.start()

    with open("/home/home/bot/pfp.gif", "rb") as f:
        await bot.user.edit(avatar=f.read())


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
        elif "joyce" in message_content and "rechts" in message_content:
            await message.reply("RECHTS UND LINKS MISCHEN SICH NICHT GUT 😡")
            detected_type = "Joyce + Rechts detected"
        elif "ashley" in message_content and "rechts" in message_content:
            await message.reply("RECHTS UND LINKS MISCHEN SICH NICHT GUT 😡")
            detected_type = "Ashley + Rechts detected"
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
                        '%H:%M Uhr %d.%m.%YY')}\n"
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

    if after.channel is None:
        speaking_users.pop(member.id, None)
        deafened_users.pop(member.id, None)


@tasks.loop(seconds=CHECK_INTERVAL)
async def check_deafened_users():
    current_time = asyncio.get_event_loop().time()
    target_user = await bot.fetch_user(BOT_HOST)

    for guild in bot.guilds:
        for member in guild.members:
            if member.voice:
                if member.id not in deafened_users and member.voice.self_deaf:
                    deafened_users[member.id] = current_time

                if member.id not in speaking_users:
                    speaking_users[member.id] = current_time

                time_since_deafened = current_time - \
                    deafened_users.get(member.id, 0)
                time_since_spoke = current_time - \
                    speaking_users.get(member.id, 0)

                if member.id in whitelist:
                    continue

                if member.voice.self_deaf or time_since_spoke >= VOICE_ACTIVITY_TIME_LIMIT:
                    if time_since_deafened >= DEAFEN_TIME_LIMIT or time_since_spoke >= VOICE_ACTIVITY_TIME_LIMIT:
                        try:
                            channel = guild.get_channel(1335686372631117926)
                            if channel:
                                await member.move_to(channel, reason="Zu lange taub oder keine Aktivität")
                                print(f"{member.display_name} wurde aus {
                                      guild.name} entfernt.")

                                try:
                                    await member.send("Du wurdest aus dem Voice-Channel entfernt.")
                                except discord.Forbidden:
                                    print(f"DM nicht möglich an {
                                          member.display_name}.")
                        except Exception as e:
                            print(f"Fehler beim Entfernen von {
                                  member.display_name}: {e}")

bot.run(TOKEN)
