import re
import discord
from discord.ext import commands
import os
import asyncio
import sys
import datetime
from postgrest.exceptions import APIError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.discord.verify_paired import verify_paired
from supabase_client import supabase
from scripts.rcon.setup_rcon import setup_rcon

rcon_client = setup_rcon()

# Regex pattern to parse dino stats from RCON response
DINO_STATS_PATTERN = re.compile(
    r"\[.*\] PlayerDataName: (.*?), PlayerID: (\d+), .*? Class: (.*?), Growth: ([\d.]+), "
    r"Health: ([\d.]+), Stamina: ([\d.]+), Hunger: ([\d.]+), Thirst: ([\d.]+)"
)

def rcon_fetch_dino_data(steam_id):
    """Fetch dino stats via RCON using Steam ID."""
    if not rcon_client.connect():
        return None

    response = rcon_client.send_command("getplayerdata", steam_id)
    rcon_client.disconnect()

    if not response or "No response received" in response:
        return None

    match = DINO_STATS_PATTERN.search(response)
    if match:
        return {
            "steam_id": steam_id,
            "dino_class": match.group(3),
            "growth": float(match.group(4)),
            "health": float(match.group(5)),
            "stamina": float(match.group(6)),
            "stored_at": datetime.datetime.utcnow().isoformat()
        }

    return None

async def store_dino(interaction=None, discord_id=None):
    """Handles storing the dino, either via Discord command or manually."""
    if not discord_id and interaction:
        discord_id = str(interaction.user.id)

    # Verify if user is paired
    steam_id, error_message = await verify_paired(discord_id)
    if not steam_id:
        if interaction:
            await interaction.response.send_message(error_message, ephemeral=True)
        else:
            print(error_message)
        return

    if interaction:
        await interaction.response.send_message(f"⏳ Fetching dino stats...", ephemeral=True)

    # Fetch dino data via RCON
    dino_data = rcon_fetch_dino_data(steam_id)
    
    if not dino_data:
        if interaction:
            await interaction.followup.send("❌ Failed to retrieve dino data. Ensure you're logged in and try again.", ephemeral=True)
        else:
            print("❌ Failed to retrieve dino data.")
        return

    if dino_data["growth"] < 0.75 or dino_data["stamina"] < 1.00:
        if interaction:
            await interaction.followup.send("❌ Your dinosaur does not meet the storage requirements (Growth: 1.0, Stamina: 1.00).", ephemeral=True)
        else:
            print("❌ Dino does not meet storage requirements.")
        return

    dino_data["discord_id"] = discord_id  # Attach discord_id for database storage

    try:
        response = supabase.table("dinosaurs").insert(dino_data).execute()
        if response.data:
            success_message = (
                f"✅ Dino stored successfully!\n"
                f"🔖 **Voucher**\n ```{response.data[0]['id']}```"
            )
            if interaction:
                await interaction.followup.send(success_message, ephemeral=True)
            else:
                print(success_message)
        else:
            if interaction:
                await interaction.followup.send("❌ Failed to store dino. Try again later.", ephemeral=True)
            else:
                print("❌ Failed to store dino.")
    except APIError as e:
        error_msg = f"❌ Database error:\n```{e}```"
        if interaction:
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            print(error_msg)
    except Exception as e:
        error_msg = f"❌ Unexpected error:\n```{e}```"
        if interaction:
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            print(error_msg)

def setup_store_dino_command(bot: commands.Bot):
    """Registers the `/store_dino` command in the bot."""
    @bot.tree.command(name="store_dino", description="Store your current dinosaur.")
    async def store_dino_command(interaction: discord.Interaction):
        await store_dino(interaction)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python store_dino.py <discord_id>")
        sys.exit(1)

    discord_id = sys.argv[1]
    asyncio.run(store_dino(discord_id=discord_id))
