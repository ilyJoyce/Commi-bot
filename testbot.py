import discord
from discord.ext import tasks, commands
import asyncio
from iniconfig import IniConfig

config = IniConfig("config.ini")

TOKEN = config.get("config", "token")
BOT_HOST = config.get("config", "bot_host")
CHECK_INTERVAL = 1
DEAFEN_TIME_LIMIT = 60 * 30
VOICE_ACTIVITY_TIME_LIMIT = 60 * 60
MONITOR_CHANNEL_ID = 1335722013523710082

deafened_users = {}
speaking_users = {}
whitelist = {
    "766992639916376064", "1141143333335465995", "871497360658800640", "729707718730055773",
    "556889798170640384", "271324530901778433", "785989592158306365", "710432389943263283",
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

        if "joyce" in message_content and "rechts" in message_content:
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
        elif any(term in message_content for term in ["communism", "kommunismus", "sozialismus", "socialism", "marxism", "marxismus", "stalin"]):
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
                    f"👤 **BENUTZER:** {message.author.mention} (`{message.author.id}`)\n"
                    f"📜 **NACHRICHT:** {message.content}\n"
                    f"📅 **UHRZEIT:** {message.created_at.strftime('%H:%M Uhr %d.%m.%YY')}\n"
                    f"🔗 **LINK:** https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                )
            except discord.Forbidden:
                print(f"Could not send a DM to {target_user} (Forbidden).")
            except Exception as e:
                print(f"Error sending DM: {e}")

    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    current_time = asyncio.get_event_loop().time()

    if after.channel is not None:
        if after.self_deaf:
            deafened_users[member.id] = current_time
        else:
            speaking_users[member.id] = current_time

    elif before.channel is not None:
        if member.id in deafened_users:
            del deafened_users[member.id]
        if member.id in speaking_users:
            del speaking_users[member.id]

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_deafened_users():
    current_time = asyncio.get_event_loop().time()

    for guild in bot.guilds:
        for member in guild.members:
            if member.voice:
                time_since_deafened = current_time - deafened_users.get(member.id, current_time)
                time_since_spoke = current_time - speaking_users.get(member.id, current_time)

                if member.id in whitelist:
                    continue

                if member.voice.self_deaf or time_since_spoke >= VOICE_ACTIVITY_TIME_LIMIT:
                    if time_since_deafened >= DEAFEN_TIME_LIMIT or time_since_spoke >= VOICE_ACTIVITY_TIME_LIMIT:
                        try:
                            await member.move_to(guild.get_channel(1335686372631117926), reason="Zu lange taub oder keine Aktivität")
                            print(f"{member.display_name} wurde aus {guild.name} entfernt wegen Inaktivität oder Taubheit.")

                            try:
                                await member.send("Du wurdest aus dem Voice-Channel entfernt, weil du zu lange die Fresse gehalten hast. Bei Beschwerden hier lecken: 8===D")
                                await target_user.send(
                                    f"🔔 **ALARM:** {member.display_name} wurde aus {guild.name} entfernt wegen Inaktivität oder Taubheit.\n"
                                    f"👤 **BENUTZER:** {member.mention} (`{member.id}`)\n"
                                    f"📅 **UHRZEIT:** {message.created_at.strftime('%H:%M Uhr %d.%m.%YY')}\n"
                                )
                            except discord.Forbidden:
                                print(f"Keine Berechtigung, {member.display_name} eine DM zu senden.")

                            deafened_users.pop(member.id, None)
                            speaking_users.pop(member.id, None)
                        except discord.Forbidden:
                            print(f"Keine Kick-Rechte für {member.display_name} in {guild.name}.")
                        except Exception as e:
                            print(f"Fehler beim Entfernen von {member.display_name} aus {guild.name}: {e}")
                else:
                    deafened_users.pop(member.id, None)
                    speaking_users.pop(member.id, None)


bot.run(TOKEN)