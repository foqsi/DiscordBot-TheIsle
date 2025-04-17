import discord
import asyncio
import os

from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from scripts.rcon.setup_rcon import setup_rcon
from utils.discord.send_messages import send_ephemeral_message, send_channel_message

load_dotenv()

CHANNEL_ID = int(os.getenv("PUBLIC_ALERTS"))

# Commands that require a message
MESSAGE_REQUIRED_COMMANDS = {"announce", "directmessage", "ban"}
COMMANDS = MESSAGE_REQUIRED_COMMANDS.union({"playerlist"})

def setup_rcon_command(bot: commands.Bot):

    async def rcon_autocomplete(interaction: discord.Interaction, current: str):
        """Provides autocomplete suggestions based on the user's input."""
        return [
            app_commands.Choice(name=cmd, value=cmd)
            for cmd in COMMANDS if current.lower() in cmd.lower()
        ]

    @bot.tree.command(name='rcon', description='Send RCON command via Discord.')
    @app_commands.autocomplete(command=rcon_autocomplete)
    async def rcon(interaction: discord.Interaction, command: str, message: str = None):
        # If the command requires a message but none is provided, show an error
        if command in MESSAGE_REQUIRED_COMMANDS and (message is None or message.strip() == ""):
            await send_ephemeral_message(interaction, f"⚠️ **A message is required for the `{command}` command!**")
            return

        rcon_client = setup_rcon()
        if rcon_client.connect():
            # Send the RCON command with or without a message
            response = rcon_client.send_command(command, command_data=message or "")

            await send_ephemeral_message(
                interaction,
                f"Response: \n```{response}```"
            )

            # If the command is "announce", send the announcement to the public alerts channel
            if command == "announce":
                await send_channel_message(bot, CHANNEL_ID, f"📢 Announcement posted via RCON: *{message}*")
        else:
            await send_ephemeral_message(interaction, "❌ **Failed to connect to RCON server.**")
