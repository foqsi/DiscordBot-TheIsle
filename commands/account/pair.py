import discord
import uuid
import datetime
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from supabase_client import supabase
from utils.discord.send_messages import send_ephemeral_message, send_channel_message, send_dm
from utils.discord.check_pairing_status import check_pairing_status

load_dotenv()

CHANNEL_ID = os.getenv('ADMIN_USER_PAIRING')

def setup_pair_command(bot: commands.Bot):
    @bot.tree.command(name='pair', description='Link your Discord account with your SteamID.')
    async def pair(interaction: discord.Interaction):
        discord_id = str(interaction.user.id)
        discord_username = interaction.user.name
        pair_code = f"FD-PAIR-{str(uuid.uuid4())}"

        data = {
            "discord_id": discord_id,
            "pair_code": pair_code,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }

        embed = discord.Embed(
            title="🦖 Foxy Dino Account Pairing\n\n",
            color=discord.Color.green()
        )
        embed.description = (
            "✅  ***Follow these steps to pair your account:***\n\n"
            "1️⃣  **Join any game server powered by Foxy Dino.**\n\n"
            "2️⃣  **Paste this command into the in-game chat:**\n"
            f"```{pair_code}```\n"
            "3️⃣  **Stay connected until you receive confirmation here in Discord that the pairing was successful.**\n\n"
            "⏳ If you don't get notified within **15 minutes**, you can safely retry using `/pair`."
        )

        try:

            # Insert the pair request into the database
            insert_pair = supabase.table('pairings').insert(data).execute()
            await send_channel_message(bot, CHANNEL_ID, f"**{discord_username}** {(discord_id)} attempt: **{pair_code}**")
            
            if insert_pair.data:
                await send_ephemeral_message(interaction, embed=embed)
                await asyncio.sleep(10)  # Wait 10 seconds before checking the pairing status
                

                await check_pairing_status(bot, discord_id, pair_code)

            else:
                await send_ephemeral_message(interaction, "Failed to create pair request.")
        except Exception as e:
            await send_ephemeral_message(interaction, f"An error occurred:\n ```{e}```")