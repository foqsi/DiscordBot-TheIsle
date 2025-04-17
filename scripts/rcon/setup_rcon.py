import os
from prcon import PersistentRconClient

def setup_rcon():
    """Returns an RconClient instance using environment variables."""
    return PersistentRconClient(
        host=os.getenv("RCON_IP"),
        port=int(os.getenv("RCON_PORT")),
        password=os.getenv("RCON_PASSWORD"),
    )