import discord
from discord import app_commands
from discord.ext import commands
import datetime


def setup_restarts_command(bot: commands.Bot):
    @bot.tree.command(name="restarts", description="Show the scheduled server restart times.")
    async def restarts(interaction: discord.Interaction):
        now = datetime.datetime.now(datetime.UTC)

        restart_times = [
            now.replace(hour=17, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1),  # 11 PM UTC
            now.replace(hour=5, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1), # 11 PM UTC
        ]

        # Convert times to UNIX timestamps
        restart_timestamps = [int(restart.timestamp()) for restart in restart_times]

        embed = discord.Embed(title="🕒 Server Restarts", color=discord.Color.blue())
        embed.description = (
            "**Server**\n"
            "The Isle Server\n\n"
            "**First Restart**\n"
            f"<t:{restart_timestamps[0]}:t>\n\n"
            "**Second Restart**\n"
            f"<t:{restart_timestamps[1]}:t>"
        )

        embed.set_footer(text="All time zones are local.")

        await interaction.response.send_message(embed=embed)
