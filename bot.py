import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commands.account.pair import setup_pair_command
from commands.account.check_pair import setup_check_pair
from commands.admin.clear_channel_messages import setup_clear_command
from commands.other.restarts import setup_restarts_command
from commands.patreon.unlock_specie import setup_unlock_command
from commands.admin.rcon_send_command import setup_rcon_command

from scripts.ftp.ftp_get_command_logs import get_command_logs
from scripts.rcon.rcon_manage_dino_roster import update_dino_roster
from scripts.rcon.send_server_restart_announcement import send_restart_announcements

load_dotenv()

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Successfully synced {len(synced)} commands')
        print('--------')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

    # Start background tasks
    bot.loop.create_task(get_command_logs(bot))
    bot.loop.create_task(update_dino_roster(bot))

    # Schedule the restart announcements
    scheduler.add_job(send_restart_announcements, 'cron', hour=11, minute=50, timezone='America/Chicago')
    scheduler.add_job(send_restart_announcements, 'cron', hour=22, minute=50, timezone='America/Chicago')
    
    scheduler.start()

# slash commands
setup_pair_command(bot)
setup_check_pair(bot)
setup_clear_command(bot)
setup_restarts_command(bot)
setup_unlock_command(bot)
# setup_rcon_command(bot)

bot.run(os.getenv('DISCORD_TOKEN'))
