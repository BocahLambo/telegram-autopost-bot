from telethon import TelegramClient, events
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- DATA BOT ANDA ---
api_id = 21346373
api_hash = 'e3ce2491b1f8b793cc40021dc2e2cb71'
bot_token = '8460135468:AAGO0ZztlIsmqy3M746PgJz1JQkNkMqsYS4'
source_channel = 'POSEIDON_DEGEN_CALLS'
target_channel = 'tokenvestors'

# --- INIT TELETHON CLIENT ---
client = TelegramClient('tokenvestors_session', api_id, api_hash).start(bot_token=bot_token)

# --- FUNCTION AMBIL SCREENSHOT CHART ---
def screenshot_chart(url):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1280,720")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    time.sleep(5)
    screenshot_path = 'chart.png'
    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path

# --- FUNCTION SAAT ADA PESAN BARU DI CHANNEL SUMBER ---
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    original = event.message.message

    dexscreener_match = re.search(r'(https:\/\/dexscreener\.com\/([\w-]+)\/[^\s]+)', original)
    if not dexscreener_match:
        return
    dexscreener_url = dexscreener_match.group(1)
    chain = dexscreener_match.group(2).upper()

    symbol_match = re.search(r'\$(\w+)', original)
    symbol = symbol_match.group(1).upper() if symbol_match else chain

    name_match = re.search(r'\$?\w+\s*[-:]?\s*([A-Za-z0-9 ]{2,30})', original)
    name = name_match.group(1).strip() if name_match else 'UnknownToken'

    tg_match = re.search(r'(https:\/\/t\.me\/[^\s]+)', original)
    x_match = re.search(r'(https:\/\/x\.com\/[^\s]+)', original)
    social = tg_match.group(1) if tg_match else (x_match.group(1) if x_match else '')

    description = re.sub(r'https:\/\/[^\s]+', '', original)
    description = re.sub(r'\$[A-Z0-9]+', '', description)
    description = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', description)
    description = description.strip()

    caption = f"${{chain}} - {{name}}\n\n{{description}}\n\n{{dexscreener_url}}"
    if social:
        caption += f"\n\nTG / X: {{social}}"

    chart_path = screenshot_chart(dexscreener_url)
    await client.send_file(target_channel, chart_path, caption=caption)

client.run_until_disconnected()
