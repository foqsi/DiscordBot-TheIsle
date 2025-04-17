import os
from ftplib import FTP, error_perm
from dotenv import load_dotenv

load_dotenv()

class PersistentFTPClient:
    """
    Persistent FTP client that keeps the connection open for multiple operations.
    """

    def __init__(self, host=None, port=None, username=None, password=None):
        self.host = host or os.getenv("FTP_HOST")
        self.port = int(port or os.getenv("FTP_PORT", 21))
        self.username = username or os.getenv("FTP_USER")
        self.password = password or os.getenv("FTP_PASS")
        self.ftp = None

    def connect(self):
        """Establish a persistent connection to the FTP server."""
        try:
            self.ftp = FTP()
            self.ftp.connect(self.host, self.port, timeout=10)
            self.ftp.login(self.username, self.password)
            print("🔹 FTP connection established.")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to FTP server: {e}")
            self.ftp = None
            return False

    def is_connected(self):
        """Check if the connection is alive."""
        try:
            self.ftp.voidcmd("NOOP")
            return True
        except:
            return False

    def ensure_connection(self):
        """Reconnect if the connection is lost."""
        if not self.ftp or not self.is_connected():
            print("🔄 Reconnecting to FTP...")
            return self.connect()
        return True

    def download_file(self, remote_path, local_dir="logs", local_file_name=None):
        """Download a file from the FTP server."""
        if not self.ensure_connection():
            return None

        try:
            os.makedirs(local_dir, exist_ok=True)
            file_name = local_file_name or os.path.basename(remote_path)
            local_path = os.path.join(local_dir, file_name)

            with open(local_path, "wb") as file:
                self.ftp.retrbinary(f"RETR {remote_path}", file.write)

            print(f"✅ Downloaded file to {local_path}")
            return local_path
        except error_perm as e:
            print(f"❌ FTP permission error: {e}")
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
        return None

    def list_dir(self, path="."):
        """List files in a directory on the FTP server."""
        if not self.ensure_connection():
            return []

        try:
            files = self.ftp.nlst(path)
            print("📁 Directory listing:")
            for file in files:
                print(f" - {file}")
            return files
        except Exception as e:
            print(f"❌ Could not list directory: {e}")
            return []

    def upload_file(self, local_path, remote_path=None):
        """Upload a file to the FTP server."""
        if not self.ensure_connection():
            return False

        try:
            with open(local_path, "rb") as file:
                destination = remote_path or os.path.basename(local_path)
                self.ftp.storbinary(f"STOR {destination}", file)
            print(f"✅ Uploaded {local_path} to {destination}")
            return True
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return False

    def disconnect(self):
        """Close the FTP connection."""
        if self.ftp:
            try:
                self.ftp.quit()
                print("🔴 FTP connection closed.")
            except Exception as e:
                print(f"⚠️ Error during FTP disconnect: {e}")
            finally:
                self.ftp = None
