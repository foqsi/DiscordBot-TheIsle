import discord
from discord.ext import commands
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts")))

# Import unlock functions
from scripts.rcon.rcon_manage_dino_roster import TEMP_UNLOCKS, unlock_dino_for_temp

def setup_unlock_command(bot):
    @bot.tree.command(name="unlock_specie", description="Temporarily unlocks a dino for 2 minutes.")
    async def unlock(interaction: discord.Interaction, dino_name: str):
        dino_name = dino_name.capitalize()

        # Verify dino exists
        if dino_name not in TEMP_UNLOCKS:
            TEMP_UNLOCKS[dino_name] = True

            # Immediately respond to avoid Discord timeout
            await interaction.response.send_message(
                f"🔓 **{interaction.user.mention} has unlocked {dino_name} for everyone for two minutes!**",
                ephemeral=False
            )

            # Run unlock logic in the background (prevents command timeout)
            bot.loop.create_task(unlock_dino_for_temp(interaction.client, dino_name, interaction.user))

        else:
            await interaction.response.send_message(f"⚠️ **{dino_name} is already unlocked!**", ephemeral=True)
