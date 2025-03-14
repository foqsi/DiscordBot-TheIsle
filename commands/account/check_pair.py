import discord
from discord.ext import commands
from utils.discord.send_messages import send_ephemeral_message
from utils.discord.verify_paired import verify_paired

def setup_check_pair(bot: commands.Bot):
    @bot.tree.command(name='check_pair', description='Check if your Discord account is paired with Steam.')
    async def check_pair(interaction: discord.Interaction):
        discord_id = str(interaction.user.id)
        steam_id, error_message = await verify_paired(discord_id)
        
        if error_message:
            await send_ephemeral_message(interaction, error_message)
            return
        
        await send_ephemeral_message(
            interaction, 
            f"✅ Your account is paired with Steam ID: `{steam_id}`"
        )