import asyncio
from rcon import RconClient

async def send_restart_announcements():
    """Sends countdown announcements before restart"""

    # Create a fresh RCON client
    rcon = RconClient()

    if not rcon.connect():
        print("❌ Failed to connect to RCON server for restart announcements.")
        return

    try:
        await rcon.send_command("announce", "Server restart in 10 minutes.")
        await asyncio.sleep(300)  # Wait 5 minutes
        await rcon.send_command("announce", "Server restart in 5 minutes.")
        await asyncio.sleep(180)  # Wait 3 minutes
        await rcon.send_command("announce", "Server restart in 2 minutes! SAFE LOG NOW")
    except Exception as e:
        print(f"❌ Failed to send restart announcements: {e}")
    finally:
        rcon.disconnect()
