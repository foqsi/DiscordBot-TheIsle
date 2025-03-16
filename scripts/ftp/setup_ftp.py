import os
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

# Load FTP Credentials
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_LOG_PATH = os.getenv("FTP_LOG_PATH")

def setup_ftp():
    """Establish a connection to the FTP server and return the FTP object."""
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
        ftp.login(FTP_USER, FTP_PASS)
        print("🔹 FTP Connection Established.")
        return ftp
    except Exception as e:
        print(f"❌ FTP Connection Error: {e}")
        return None

def ftp_download_file(file_name, local_dir="logs"):
    """Downloads a file from the FTP server."""
    ftp = setup_ftp()
    if not ftp:
        return None

    try:
        os.makedirs(local_dir, exist_ok=True)
        local_file_path = os.path.join(local_dir, file_name)

        with open(local_file_path, "wb") as file:
            ftp.retrbinary(f"RETR {FTP_LOG_PATH}", file.write)

        ftp.quit()
        print(f"✅ Downloaded {file_name} to {local_file_path}")
        return local_file_path
    except Exception as e:
        print(f"❌ FTP Download Error: {e}")
        return None
