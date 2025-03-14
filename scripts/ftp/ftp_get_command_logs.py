import ftplib
import os
import re
import asyncio
from dotenv import load_dotenv

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_LOG_PATH = os.getenv("FTP_LOG_PATH")

# Local storage
LOCAL_LOG_DIR = "logs"
LOCAL_LOG_FILE = os.path.join(LOCAL_LOG_DIR, "TheIsle-Shipping.log")
LAST_PROCESSED_FILE = os.path.join(LOCAL_LOG_DIR, "last_processed_timestamp.txt")  # Stores last processed timestamp

# Discord Configuration
CHANNEL_ID = int(os.getenv("GET_LOG_CHANNEL_ID"))

# Regex for extracting command details and timestamps
COMMAND_PATTERN = re.compile(r"\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})\]\[LogTheIsleCommandData\]: ([^\[]+) \[([0-9]{17})\] used command: (.+) at: (.+)")

def ensure_log_directory():
    """Ensure local logs directory exists."""
    if not os.path.exists(LOCAL_LOG_DIR):
        os.makedirs(LOCAL_LOG_DIR)

def download_log():
    """Downloads the log file only if it's updated."""
    ensure_log_directory()

    try:
        with ftplib.FTP() as ftp:
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASS)

            # Download log file
            with open(LOCAL_LOG_FILE, "wb") as log_file:
                ftp.retrbinary(f"RETR {FTP_LOG_PATH}", log_file.write)
            return True
    except Exception as e:
        print(f"❌ FTP Error: {e}")
        return False

def get_last_processed_timestamp():
    """Retrieves the last processed timestamp to prevent duplicates."""
    if os.path.exists(LAST_PROCESSED_FILE):
        with open(LAST_PROCESSED_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    return ""

def save_last_processed_timestamp(timestamp):
    """Saves the last processed timestamp."""
    with open(LAST_PROCESSED_FILE, "w", encoding="utf-8") as file:
        file.write(timestamp)

async def send_to_discord(bot, message):
    """Sends a message to the specified Discord channel."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print("❌ Failed to find Discord channel!")

def extract_target_player(command_details):
    """
    Extracts the target player's name from command details.
    Example input:
    "Foqsi, [SteamID], Class: Pteranodon, Gender: Male, Previous value: 0.000000%, New value: 0.000000%"
    Expected output: "Foqsi"
    """
    details_parts = command_details.split(", ")
    if details_parts:
        return details_parts[0]  # The first part should be the target player's name
    return "Unknown Player"

async def process_new_logs(bot):
    """Reads and processes only new log entries, ignoring previously sent logs."""
    last_timestamp = get_last_processed_timestamp()

    try:
        with open(LOCAL_LOG_FILE, "r", encoding="utf-8") as log_file:
            new_lines = log_file.readlines()

            for line in new_lines:
                command_match = COMMAND_PATTERN.search(line)

                if command_match:
                    timestamp = command_match.group(1).strip()
                    admin_name = command_match.group(2).strip()
                    command = command_match.group(4).strip()
                    command_details = command_match.group(5).strip()

                    # Ignore previously processed timestamps
                    if timestamp <= last_timestamp:
                        continue

                    # Update last processed timestamp
                    save_last_processed_timestamp(timestamp)

                    # Extract target player
                    target_player = extract_target_player(command_details)

                    discord_message = f"🛠️ **{admin_name}** used **{command}** on **{target_player}**"

                    await send_to_discord(bot, discord_message)

    except Exception as e:
        print(f"❌ Error processing logs: {e}")

async def get_command_logs(bot):
    """Continuously checks for new command logs."""
    print("🔹 Monitoring command logs...")

    while True:
        log_updated = download_log()
        if not log_updated:
            await asyncio.sleep(5)
            continue

        await process_new_logs(bot)  # Only process new commands
        await asyncio.sleep(1)
