import requests
import time
from telegram import Bot
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# ===== CONFIG =====
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
BITNODES_URL = "https://bitnodes.io/api/v1/snapshots/latest/"
SLEEP_INTERVAL = 300  # 5 minutes
# ==================

bot = Bot(token=TELEGRAM_TOKEN)
last_reachable = None
last_average = None

def fetch_bitnodes():
    """Fetch reachable nodes and average from Bitnodes API"""
    try:
        response = requests.get(BITNODES_URL, timeout=10)
        data = response.json()
        reachable = data["nodes_reachable"]
        average = data["nodes_total"]  # Or whatever metric you want
        return reachable, average
    except Exception as e:
        print(Fore.RED + f"Error fetching Bitnodes data: {e}")
        return None, None

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        print(Fore.GREEN + "Message sent successfully!")
    except Exception as e:
        print(Fore.RED + f"Failed to send Telegram message: {e}")

def main():
    global last_reachable, last_average
    while True:
        reachable, average = fetch_bitnodes()
        if reachable is None:
            time.sleep(SLEEP_INTERVAL)
            continue

        msg = f"Reachable Nodes: {reachable}\nAverage Nodes: {average}"

        # Only send if data changed
        if reachable != last_reachable or average != last_average:
            send_telegram_message(msg)
            last_reachable = reachable
            last_average = average
        else:
            print(Fore.YELLOW + "No change, not sending Telegram message.")

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
