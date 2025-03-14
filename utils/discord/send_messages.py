import discord
import logging

from utils.discord.get_user_mention import get_user_mention

logger = logging.getLogger(__name__)

async def send_message(bot, channel_id, message=None, embed=None):
    """Sends a message or embed to the specified Discord channel."""
    await send_channel_message(bot, channel_id, message, embed)

async def send_ephemeral_message(interaction: discord.Interaction, message=None, embed=None):
    """Sends an ephemeral message or embed to the specified Discord user."""
    await interaction.response.send_message(content=message, embed=embed, ephemeral=True)

async def send_dm(bot, user_id, message=None, embed=None):
    """Sends a DM or embed to the specified Discord user."""
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(content=message, embed=embed)
    except discord.Forbidden:
        user_mention = get_user_mention(user_id)
        await send_ephemeral_message(discord.Interaction, f"{user_mention}, I couldn't send you a DM. Please enable DMs from server members.")
        logger.warning(f"⚠️ Could not DM user {user_id} - Sent ephemeral message")
    except discord.NotFound:
        logger.warning(f"⚠️ User {user_id} not found.")

async def send_channel_message(bot, channel_id, message=None, embed=None):
    """Sends a message or embed to the specified Discord channel."""
    try:
        channel = await bot.fetch_channel(int(channel_id))
        await channel.send(content=message, embed=embed)
    except discord.Forbidden:
        logger.warning(f"⚠️ Could not send message to channel {channel_id} - missing permissions.")
    except discord.NotFound:
        logger.warning(f"⚠️ Channel {channel_id} not found.")