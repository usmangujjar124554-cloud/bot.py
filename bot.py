from selenium import webdriver
from selenium.webdriver.common.by import By
from colorama import Fore, init
import requests
import time
import traceback

# ✅ Initialize colorama
init(autoreset=True)

# ✅ Telegram config
BOT_TOKEN = "8381325662:AAGdCTqrFaTKWeLJTNnbSRBlM3r3tXU9F-4"   # ⚠️ replace safely
CHAT_ID = "7013708017"

def send_to_telegram(message):
    """Send message to your Telegram chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(Fore.CYAN + "📨 Telegram message sent successfully!")
        else:
            print(Fore.RED + f"⚠️ Telegram API error: {response.text}")
    except Exception as e:
        print(Fore.RED + f"❌ Telegram send failed: {e}")

# ✅ Start browser
driver = webdriver.Chrome()
driver.get("https://bitnodes.io/dashboard/")
print(Fore.GREEN + "✅ Bitnodes dashboard khul gaya successfully!\n")

def rgb_or_rgba_to_hex(color_str):
    """Convert rgb(...) or rgba(...) string to hex"""
    if not color_str:
        return None
    try:
        color_str = color_str.strip().replace("rgba(", "").replace("rgb(", "").replace(")", "")
        parts = color_str.split(",")
        r, g, b = [int(float(x.strip())) for x in parts[:3]]
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return None

# ✅ Store last known values
last_reachable = None
last_average = None
last_change = None
last_trend = None

while True:
    try:
        time.sleep(10)

        # ✅ Fetch live values
        reachable = driver.find_element(By.ID, "reachable-nodes").text
        average = driver.find_element(By.ID, "average-nodes").text
        change_element = driver.find_element(By.ID, "change-nodes")
        change_text = change_element.text

        # ✅ Detect caret color
        caret_color_rgb = driver.execute_script("""
            let el = document.querySelector('#change-nodes i');
            if (el) return window.getComputedStyle(el).color;
            return null;
        """)
        caret_color_hex = rgb_or_rgba_to_hex(caret_color_rgb)

        # ✅ Detect trend
        if caret_color_hex == "#3c763d":
            trend = "Positive (Green ↑)"
        elif caret_color_hex == "#a94442":
            trend = "Negative (Red ↓)"
        else:
            trend = f"Neutral ({caret_color_hex})"

        # ✅ Print locally
        print("\033[H\033[J", end="")  # clear terminal
        print(Fore.CYAN + f"Reachable Nodes:__ {reachable}")
        print(Fore.CYAN + f"Average Nodes:_____   {average}")
        print(Fore.CYAN + f"Change Nodes:______    {change_text}")
        print(Fore.CYAN + f"Trend:_____________           {trend}")

        # ✅ Check if data changed
        if (reachable != last_reachable or
            average != last_average or
            change_text != last_change or
            trend != last_trend):

            print(Fore.GREEN + "📤 Data changed — sending update to Telegram...")

            # ✅ Send live update to Telegram
            message = (
                f"📊 Bitnodes Live Update\n"
                f"Reachable Nodes: {      reachable}\n"
                f"Average Nodes: {        average}\n"
                f"Change: {               change_text}\n"
                f"Trend: {                trend}"
            )
            send_to_telegram(message)

            # ✅ Save new data
            last_reachable =reachable
            last_average =  average
            last_change =   change_text
            last_trend =    trend

        else:
            print(Fore.YELLOW + "⏸ No change detected — skipping Telegram send.")

        print(Fore.MAGENTA + "\n⏳ Next update in 30 seconds...\n")

    except Exception as e:
        # ✅ Handle any error
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(Fore.RED + f"❌ Error occurred:\n{error_message}")

        # ✅ Send last known good data + error to Telegram
        error_alert = (
            f"⚠️ Bitnodes Monitor Error ⚠️\n\n"
            f"❌ An error occurred:\n{error_message}\n\n"
            f"📊 Last Known Good Data:\n"
            f"Reachable Nodes: {last_reachable}\n"
            f"Average Nodes: {last_average}\n"
            f"Change: {last_change}\n"
            f"Trend: {last_trend}"
        )
        send_to_telegram(error_alert)

        # Wait a bit before retrying
        time.sleep(10)

# ✅ Cleanup
driver.quit()

