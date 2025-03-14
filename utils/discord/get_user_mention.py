async def get_user_mention(user_id):
    """Returns a string that mentions the specified user."""
    return f"<@{user_id}>"