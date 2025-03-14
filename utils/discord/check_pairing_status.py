import asyncio
from supabase_client import supabase
from utils.discord.send_messages import send_dm
from scripts.ftp.ftp_get_pairing_chats import get_pairing_chats

async def check_pairing_status(bot, discord_id, pair_code):
    """Checks if pair was successful. Sends DM to user and deletes the pair request after 15 minutes if not successful."""
    try:
        pairing_success = await asyncio.wait_for(get_pairing_chats(bot), timeout=900)
        
        if pairing_success:
            await send_dm(bot, discord_id, (
            "✅ **Your Foxy Dino account has been successfully paired!**\n\n"
            "Keep your pair key safe for future reference.\n"
            f"```{pair_code}```"))
            return True
        
    except asyncio.TimeoutError:
        # If 15 minutes pass without successful pairing
        delete_pair_request = (
            supabase.table('pairings')
            .delete()
            .eq('pair_code', pair_code)
            .execute()
        )

        if delete_pair_request:
            await send_dm(bot, discord_id, "⚠️ Your pairing request has expired. You may try `/pair` again.")
            return False

    except Exception as e:
        print(f"❌ Error in check_pairing_status: {e}")
        return False