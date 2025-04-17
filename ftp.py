import os
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

class FTPClient:
    """
    FTP Client for downloading files from a remote server.
    """

    def __init__(self, host=None, port=None, username=None, password=None, log_path=None):
        self.host = host or os.getenv("FTP_HOST")
        self.port = int(port or os.getenv("FTP_PORT", 21))
        self.username = username or os.getenv("FTP_USER")
        self.password = password or os.getenv("FTP_PASS")
        self.log_path = log_path or os.getenv("FTP_LOG_PATH")
        self.ftp = None

    def connect(self):
        """Establish connection to the FTP server."""
        try:
            self.ftp = FTP()
            self.ftp.connect(self.host, self.port, timeout=10)
            self.ftp.login(self.username, self.password)
            print("🔹 FTP Connection Established.")
            return True
        except Exception as e:
            print(f"❌ FTP Connection Error: {e}")
            self.ftp = None
            return False

    def disconnect(self):
        """Close the FTP connection."""
        if self.ftp:
            try:
                self.ftp.quit()
                print("🔴 FTP Connection Closed.")
            except Exception as e:
                print(f"⚠️ FTP Disconnect Error: {e}")
            finally:
                self.ftp = None

    def download_file(self, file_name, local_dir="logs"):
        """Download a file from the FTP server to a local directory."""
        if not self.ftp:
            if not self.connect():
                return None

        try:
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, file_name)

            with open(local_path, "wb") as file:
                self.ftp.retrbinary(f"RETR {self.log_path}", file.write)

            print(f"✅ Downloaded log file to {local_path}")
            return local_path
        except Exception as e:
            print(f"❌ FTP Download Error: {e}")
            return None
