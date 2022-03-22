"""Discord bot that recommends a percentage volume for each user in a voice chat."""

import asyncio
import logging
import os
import dotenv
import discord as dc
from discord import app_commands as ac
from .measurement import db_to_dc_percent, loudness, float_to_array


# Loudness units relative to full scale (LUFS) that the recommended adjustment aims for
# by default.
TARGET_LUFS = -28


# Priveleged intent.
# When turned off, the bot will only know if a user is in a voice channel if they have
# changed their voice channel after the bot has logged in (not tested if the bot gets
# this info when it first joins a guild.)
MEMBERS_INTENT = True


# For testing the bot on a single Guild. None to make the slash command upload global.
dotenv.load_dotenv(".env")
test_guild_id = os.getenv("TEST_GUILD")
test_guild: None | dc.Object = test_guild_id and dc.Object(test_guild_id)  # type: ignore

logger = logging.getLogger("discord.voice_eq_bot")

intents = dc.Intents()
intents.voice_states = True
intents.guilds = True
intents.members = MEMBERS_INTENT
client = dc.Client(intents=intents)


tree = ac.CommandTree(client)


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user} (ID: {client.user.id})")  # type: ignore

    # Sync the application command with Discord.
    await tree.sync(guild=test_guild)


@tree.command()
async def help(intr: dc.Interaction):
    "Show help."
    help_str = (
        "Use `/measure` to have the bot join your current voice channel,"
        " and measure everyone's voice loudness."
        " While measuring, everyone should talk at their usual loudness."
        " (Talking at the same is ok.)\n"
        "After that, bot recommends percentages that you should set everyone else's"
        " volume at."
        " (You can ignore your own percentage.)"
    )
    await intr.response.send_message(help_str)


@tree.command(guild=test_guild)
async def measure(intr: dc.Interaction, duration: int = 10):
    """Join the voice channel to measure each member's voice level,
    and recommend volume percentages.
    """
    # TODO: Check if the bot has the required permissions.

    if not intr.guild:
        return

    duration = min(duration, 30)

    try:
        voice_chn = intr.user.voice.channel  # type: ignore
        assert voice_chn
    except (AttributeError, AssertionError):
        await intr.response.send_message(
            "You need to be in a voice channel", ephemeral=True
        )
        return

    permissions = voice_chn.permissions_for(intr.guild.me)
    if not permissions.connect:
        await intr.response.send_message(
            "The bot doesn't have permission to join the voice channel.", ephemeral=True
        )
        return

    async with await voice_chn.connect(timeout=5, cls=dc.VoiceClient) as voice_client:
        resp = intr.response.send_message(
            "Measuring voice levels, everyone should speak now."
        )
        resp_task = asyncio.create_task(resp)

        voice_receiver: dc.VoiceReceiver = await voice_client.start_receiving(
            buffer=10, output_type="float"
        )
        await resp_task

        user_pcms: dict[dc.User | dc.Member, bytearray] = {}
        async for member, _, pcm in voice_receiver(duration):

            if isinstance(member, dc.Object):  # If the user could not be got, skip.
                continue

            user_pcms.setdefault(member, bytearray()).extend(pcm)

    loudnesses = {
        user: loudness(
            float_to_array(pcm, voice_receiver.channels), voice_receiver.sampling_rate
        )
        for user, pcm in user_pcms.items()
    }
    adjustments = {
        user: db_to_dc_percent(TARGET_LUFS - loud) for user, loud in loudnesses.items()
    }

    reply_lines = []

    for vc_user, adj in adjustments.items():

        # If the required adjustment is above this value, assume the person did not
        # speak properly.
        ADJ_CUTOFF = 3.0
        if adj > ADJ_CUTOFF:
            pass
        else:
            adj_perc_str = f"{adj:.0%}"
            rel_loudness = loudnesses[vc_user] - TARGET_LUFS
            reply_lines.append(
                f"`{vc_user.display_name}`: `{adj_perc_str}`  (` {-rel_loudness:+3.1f} dB {'🔉' if rel_loudness > 0 else '🔊'}`)"
            )

    # Sort names alphabetically, as it's how it appears on the Discord GUI.
    reply_lines.sort()

    if len(reply_lines) == 0:
        await intr.followup.send("No one talked.")
    else:
        await intr.followup.send(
            "__Optimal volume settings:__\n\n" + "\n".join(reply_lines)
        )
