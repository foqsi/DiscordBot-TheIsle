import discord
from discord import app_commands
from discord.ext import commands

async def clear_messages(interaction: discord.Interaction, amount: int):
    """Deletes messages from the channel where the command is used."""
    # Check if the user has permission to manage messages
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            "❌ You don't have permission to delete messages!", ephemeral=True
        )
        return

    # Ensure the bot has the required permission
    if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
        await interaction.response.send_message(
            "❌ I don't have permission to delete messages in this channel!", ephemeral=True
        )
        return

    # Defer response since deletion takes time
    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    # Confirm deletion
    await interaction.followup.send(f"✅ Deleted {len(deleted)} messages!", ephemeral=True)

# Setup function to register command
def setup_clear_command(bot: commands.Bot):
    @bot.tree.command(name="clear_channel_messages", description="Delete messages in this channel")
    @app_commands.describe(amount="Number of messages to delete (default: 10)")
    async def clear_channel_messages(interaction: discord.Interaction, amount: int = 10):
        await clear_messages(interaction, amount)
