import socket
import os
from dotenv import load_dotenv

load_dotenv()

class PersistentRconClient:
    """
    Persistent RCON Client to maintain an open connection to The Isle Evrima game server.
    """

    command_byte_map = {
        'announce': 0x10,
        'directmessage': 0x11,
        'serverdetails': 0x12,
        'wipecorpses': 0x13,
        'updateplayables': 0x15,
        'ban': 0x20,
        'kick': 0x30,
        'playerlist': 0x40,
        'save': 0x50,
        'getplayerdata': 0x77,
        'togglewhitelist': 0x81,
        'addwhitelist': 0x82,
        'removewhitelist': 0x83,
        'toggleglobalchat': 0x84,
        'togglehumans': 0x86,
        'toggleai': 0x90,
        'disableaiclasses': 0x91,
        'aidensity': 0x92,
    }

    def __init__(self, host=None, port=None, password=None, timeout=5):
        self.host = host or os.getenv("SERVER_IP")
        self.port = int(port or os.getenv("RCON_PORT"))
        self.password = password or os.getenv("RCON_PW")
        self.timeout = timeout
        self.socket = None
        self.is_authorized = False

    def connect(self):
        if not self.host or not self.port or not self.password:
            print("❌ Missing RCON credentials.")
            return False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)

        try:
            self.socket.connect((self.host, self.port))
            return self.authorize()
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def authorize(self):
        if self.is_authorized:
            return True

        try:
            packet = b'\x01' + self.password.encode() + b'\x00'
            self.send_packet(packet)
            response = self.read_packet()
            if "Accepted" in response:
                self.is_authorized = True
                return True
            else:
                print(f"❌ Authorization failed: {response}")
                return False
        except Exception as e:
            print(f"❌ Auth error: {e}")
            return False

    def send_packet(self, data):
        try:
            self.socket.sendall(data)
        except Exception as e:
            print(f"❌ Packet send failed: {e}")
            self.is_authorized = False

    def read_packet(self):
        try:
            data = self.socket.recv(4096)
            return data.decode('utf-8', errors='ignore')
        except socket.timeout:
            return "⚠️ Timeout: No response"
        except Exception as e:
            return f"❌ Receive error: {e}"

    def send_command(self, command_name, command_data=""):
        if command_name not in self.command_byte_map:
            return f"❌ Unknown command: {command_name}"

        if not self.socket or not self.is_authorized:
            print("🔄 Attempting reconnect...")
            if not self.connect():
                return "❌ Could not connect or authorize."

        command_byte = self.command_byte_map[command_name]
        packet = b'\x02' + bytes([command_byte]) + command_data.encode() + b'\x00'
        self.send_packet(packet)
        return self.read_packet()

    def close(self):
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"⚠️ Disconnect error: {e}")
            finally:
                self.socket = None
                self.is_authorized = False


# Usage Example:
if __name__ == "__main__":
    rcon = PersistentRconClient()
    if rcon.connect():
        print("🔗 Connected. Type 'exit' to quit.")
        while True:
            user_input = input("RCON> ")
            if user_input.lower() == "exit":
                break
            parts = user_input.split(" ", 1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""
            response = rcon.send_command(cmd, arg)
            print(f"📡 {response}")
        rcon.close()
    else:
        print("❌ Failed to start RCON session.")
