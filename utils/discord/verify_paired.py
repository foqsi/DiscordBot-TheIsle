import sys
import asyncio
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase

async def verify_paired(discord_id):
    """
    Checks if a Discord user is paired and completed.
    
    Returns:
        - steam_id (if completed)
        - None, error_message (if not paired)
    """
    try:
        response = (
            supabase.table("pairings")
            .select("steam_id, status")
            .eq("discord_id", discord_id)
            .execute()
        )

        if not response.data:
            return None, "⚠️ You are not paired. Use `/pair` to link your account."

        pairing = response.data[0]

        if pairing["status"] != "completed":
            return None, "⚠️ Your pairing is not completed. Try `/pair` again."

        return pairing["steam_id"], None
    except Exception as e:
        return None, f"❌ Database error:\n```{e}```"