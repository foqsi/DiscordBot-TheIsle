from ftp import FTPClient
import os

def setup_ftp():
    """Returns an FTPClient instance using environment variables."""
    return FTPClient(
        host=os.getenv("FTP_HOST"),
        port=os.getenv("FTP_PORT"),
        username=os.getenv("FTP_USER"),
        password=os.getenv("FTP_PASS"),
        log_path=os.getenv("FTP_LOG_PATH"),
    )
