# The Isle Evrima Discord Bot (Previously Foxy Dino)

A Discord bot designed for **The Isle Evrima** servers, leveraging in-game log monitoring to create an interactive experience for players and server administrators.

---

## ⚠️ Project Status

🚫 **This project is no longer under active development.**  
I’ve decided to stop working on it. While the code and commands remain available for reference, no further updates, maintenance, or support are planned.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🚀 Features

🔹 **Log Monitoring**  
The bot actively monitors live game logs to provide real-time updates and interactions.

🔹 **Commands**  
The bot supports the following slash commands:

| Command                                 | Description                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `/restarts`                             | Displays the last time the server was restarted.                                                                    |
| `/store_dino`                           | Stores a dinosaur for the player if they have 100% stamina.                                                         |
| `/restore_dino`                         | Restores a stored dinosaur for the player. Unlocks it if currently locked.                                          |
| `/unlock_dino <dino_name>`              | Allows Patreon users to unlock a dinosaur by name.                                                                  |
| `/rcon_send_command <command> <?msg>`   | Allows admins to send an RCON command to the server directly from Discord.                                          |
| `/clear_channel_messages <number>`      | Allows admins and moderators to clear a specified number of messages in a Discord channel.                          |
| `/pair`                                 | Generates a unique pairing key (e.g., `FD-PAIR-xxxxxx`) for the user. The user copies this key into in-game chat to pair their Steam and Discord accounts. If the user does not pair within a set time limit, the key is removed, allowing them to try again. |
| `/check_pair`                           | Checks the current pairing status of the user.                                                                      |

---

## ⚙️ How It Works

- **Interactive Experience**  
  The bot uses the game's live logs to detect specific in-game events and communicate them in Discord.

- **Player Pairing**  
  Pairing links Discord users with their Steam accounts using a secure, time-limited code (`FD-PAIR-xxxxxx`).

- **Admin Tools**  
  Admins and moderators have access to advanced commands like RCON control and chat cleanup directly from Discord.

- **Event Broadcasting**  
  Currently, only admin commands are fully implemented. In future updates, event-based messages (like deaths, spawns, etc.) can be shared in Discord channels.

---

## 🛠️ Setup & Configuration

> **Note:** A full setup guide will be provided in a future release.

1. Clone the repository.
2. Configure your bot token and RCON credentials in the environment variables.
