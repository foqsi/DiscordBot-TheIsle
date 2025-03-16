from asyncio.log import logger
import os
import re
import asyncio
from dotenv import load_dotenv
from supabase_client import supabase
from .setup_ftp import ftp_download_file

load_dotenv()

# Local storage settings
LOCAL_LOG_DIR = "logs"
LOCAL_LOG_FILE = os.path.join(LOCAL_LOG_DIR, "TheIsle-Shipping.log")

# Regex patterns
PAIR_CODE_PATTERN = re.compile(r"FD-PAIR-[a-fA-F0-9\-]+")
STEAM_ID_PATTERN = re.compile(r"\[([0-9]{17})\]:")  # Extracts Steam ID

last_log_size = 0  # Track last read position

async def process_new_logs(bot):
    """Reads and processes only new log entries, filtering for pairing codes."""
    global last_log_size
    pairing_found = False

    try:
        with open(LOCAL_LOG_FILE, "r", encoding="utf-8") as log_file:
            log_file.seek(last_log_size)
            new_lines = log_file.readlines()
            last_log_size = log_file.tell()

            for line in new_lines:
                if "[LogTheIsleChatData]" in line:
                    pair_match = PAIR_CODE_PATTERN.search(line)
                    steam_match = STEAM_ID_PATTERN.search(line)

                    if pair_match and steam_match:
                        pair_code = pair_match.group()
                        steam_id = steam_match.group(1)

                        # First, find the existing pairing request
                        existing_pair = supabase.table("pairings")\
                            .select("*")\
                            .eq("pair_code", pair_code)\
                            .eq("status", "pending")\
                            .execute()

                        if existing_pair.data:
                            # Update the existing record with the steam_id
                            update_result = supabase.table("pairings")\
                                .update({"steam_id": steam_id, "status": "completed"})\
                                .eq("pair_code", pair_code)\
                                .execute()
                            
                            if update_result.data:
                                print(f"✅ Steam ID {steam_id} paired with code {pair_code}")
                                pairing_found = True
                                break
                        else:
                            print(f"❌ No pending pair request found for code {pair_code}")
                            
    except Exception as e:
        print(f"❌ Error processing logs: {e}")
    
    return pairing_found

async def get_pairing_chats(bot):
    """Continuously checks for new chat logs and updates Supabase until a pairing is found."""
    global last_log_size
    print("🔹 Monitoring chat logs for pairing codes...")

    try:
        while True:
            downloaded_file = ftp_download_file("TheIsle-Shipping.log", LOCAL_LOG_DIR)
            if not downloaded_file:
                logger.warning("❌ Could not download chat log file.")
                await asyncio.sleep(5)
                continue

            new_log_size = os.path.getsize(downloaded_file)
            if new_log_size > last_log_size:
                pairing_found = await process_new_logs(bot)
                if pairing_found:
                    print("✅ Pairing successful! Stopping monitoring.")
                    return True  # Return True when pairing is successful

            await asyncio.sleep(5)

    except Exception as e:
        print(f"❌ Error in get_pairing_chats: {e}")
        return False