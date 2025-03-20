import os
import re
import asyncio
from .setup_rcon import setup_rcon
from dotenv import load_dotenv

load_dotenv()
RCON_CLIENT = setup_rcon()

CHANNEL_ID = int(os.getenv("PUBLIC_ALERTS"))

DISCORD_HEADER = ("## ♻️ Automated Population Control Update\n\n"
                   "The following spawn changes were automatically applied to the game server. "
                   "You can still spawn with an existing save or in a nest even if a species is disabled.\n")

#  Dinosaur species with individual population caps
DINO_POPULATION_CAPS = {
    "Dryosaurus": -1,
    "Hypsilophodon": -1,
    "Pachycephalosaurus": 8,
    "Stegosaurus": 20,
    "Tenontosaurus": None,
    "Carnotaurus": None,
    "Maiasaura": None,
    "Ceratosaurus": None,
    "Deinosuchus": 10,
    "Diabloceratops": 0,
    "Omniraptor": 24,
    "Pteranodon": 0,
    "Troodon": 10,
    "Beipiaosaurus": -1,
    "Gallimimus": 8,
    "Dilophosaurus": None,
    "Herrerasaurus": 24
}

#  Temporary Unlock Tracking
TEMP_UNLOCKS = {}

#  Regex Patterns
DINO_PATTERN = re.compile(r"Class: BP_(\w+)_C")
HEALTH_PATTERN = re.compile(r"Health: ([0-9.]+)")
STEAM_ID_PATTERN = re.compile(r"PlayerID: (\d{17})")

#  Store last known state of each dino
last_dino_state = {}

async def get_dino_population():
    """Fetch live player data from RCON and count dino species, excluding dead players."""
    if not RCON_CLIENT.connect():
        return {}

    #  Get **actual logged-in players**
    player_list_response = RCON_CLIENT.send_command("playerlist")
    online_steam_ids = set(re.findall(r"(\d{17})", player_list_response))

    #  Get full player details
    response = RCON_CLIENT.send_command("getplayerdata")
    RCON_CLIENT.disconnect()

    if not response or "No response received" in response:
        return {}

    #  Count only **alive** dinos
    dino_count = {dino: 0 for dino in DINO_POPULATION_CAPS.keys()}
    for line in response.split("\n"):
        dino_match = DINO_PATTERN.search(line)
        health_match = HEALTH_PATTERN.search(line)
        steam_id_match = STEAM_ID_PATTERN.search(line)

        if dino_match and health_match and steam_id_match:
            dino_class = dino_match.group(1)
            health = float(health_match.group(1))
            steam_id = steam_id_match.group(1)

            #  Only count **alive** dinos and players **currently logged in**
            if health > 0.00 and steam_id in online_steam_ids and dino_class in dino_count:
                dino_count[dino_class] += 1

    return dino_count

async def update_dino_roster(bot):
    """Continuously monitors dino population and updates the roster in real-time."""
    await bot.wait_until_ready()
    print("🔹 Monitoring dino population...")

    global last_dino_state  #  Store the last known dino state

    while True:
        try:
            dino_population = await get_dino_population()
            if not dino_population:
                await asyncio.sleep(5)  #  Retry after delay
                continue

            #  Determine enabled species, including temporary unlocks
            enabled_dinos = [
                dino for dino, count in dino_population.items()
                if dino in TEMP_UNLOCKS or DINO_POPULATION_CAPS[dino] is None or count <= DINO_POPULATION_CAPS[dino]
            ]

            #  Apply changes via RCON
            roster_string = ",".join(enabled_dinos)
            if RCON_CLIENT.connect():
                RCON_CLIENT.send_command("updateplayables", roster_string)
                RCON_CLIENT.disconnect()

            #  Detect changes and notify Discord (ONLY for changed dinos)
            await notify_dino_changes(bot, dino_population)

            #  Save new roster state
            last_dino_state = {dino: count for dino, count in dino_population.items()}

            await asyncio.sleep(5)  #  Ensure loop keeps running
        except Exception as e:
            print(f"❌ Error in update_dino_roster: {e}")
            await asyncio.sleep(5)  #  Retry if something fails

async def notify_dino_changes(bot, dino_population):
    """Sends messages to Discord **only** if a specific dino was enabled or disabled."""
    global last_dino_state
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    changes = []  # Store changed dino messages

    for dino, count in dino_population.items():
        cap = DINO_POPULATION_CAPS[dino]
        if cap is None:
            continue  # Skip dinos with no cap

        previously_enabled = last_dino_state.get(dino, None) is None or last_dino_state[dino] <= cap
        currently_enabled = count <= cap

        if currently_enabled and not previously_enabled:
            # ✅ Dino was just enabled
            changes.append(f"> ✅ **{dino.upper()}** spawns have been **ENABLED**\n")

        elif not currently_enabled and previously_enabled:
            # ❌ Dino was just disabled
            changes.append(f"> ❌ **{dino.upper()}** spawns have been **DISABLED**\n")

    if changes:
        # Send the **header message** only once
        # Combine header + changes and send as one message
        final_message = f"{DISCORD_HEADER}\n" + "\n".join(changes) + "\n=============================================="
        await channel.send(final_message)

async def unlock_dino_for_temp(bot, dino_name, user):
    """Temporarily unlocks a dino for 2 minutes."""
    dino_name = dino_name.capitalize()
    if dino_name not in DINO_POPULATION_CAPS:
        return

    #  Add to temporary unlocks
    TEMP_UNLOCKS[dino_name] = True

    #  Apply changes via RCON
    enabled_dinos = [
        dino for dino in DINO_POPULATION_CAPS.keys()
        if dino in TEMP_UNLOCKS or DINO_POPULATION_CAPS[dino] is None or dino_name == dino
    ]
    roster_string = ",".join(enabled_dinos)

    if RCON_CLIENT.connect():
        RCON_CLIENT.send_command("updateplayables", roster_string)
        RCON_CLIENT.disconnect()

    #  Wait for 2 minutes, then disable the dino
    await asyncio.sleep(120)
    await disable_unlocked_dino(bot, dino_name)

async def disable_unlocked_dino(bot, dino_name):
    """Removes a temporarily unlocked dino from the roster after 2 minutes and notifies Discord."""
    if dino_name in TEMP_UNLOCKS:
        del TEMP_UNLOCKS[dino_name]  #  Remove from temp unlock list

    #  Ensure Discord channel is found before sending
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        message = f"{DISCORD_HEADER}\n" + (f"> ❌ **{dino_name.upper()}** spawns have been **DISABLED**\n") + "\n=============================================="
        await channel.send(message)

    else:
        print("⚠️ Could not find the Discord channel!")  # Debugging log

    #  Reapply regular population rules
    await update_dino_roster(bot)