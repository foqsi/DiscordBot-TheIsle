import discord
from discord import app_commands
from discord.ext import commands
from supabase_client import supabase

def setup_restore_dino_command(bot: commands.Bot):
    @bot.tree.command(name="restore_dino", description="Redeem a voucher to retrieve your stored dinosaur.")
    async def voucher(interaction: discord.Interaction):
        discord_id = str(interaction.user.id)
        response = supabase.table("dinosaurs").select("*").eq("discord_id", discord_id).limit(1).execute()

        if not response.data:
            await interaction.response.send_message("❌ You have no stored dinosaurs.", ephemeral=True)
            return

        dino = response.data[0]

        await interaction.response.send_message(f"✅ Your {dino['species']} (growth {dino['growth']}) has been re-spawned.", ephemeral=True)

        supabase.table("dinosaurs").delete().eq("discord_id", discord_id).eq("species", dino['species']).execute()
