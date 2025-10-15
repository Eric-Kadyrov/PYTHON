import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pynput import keyboard

urls = [
    "https://www.iqt.org/",
    "https://shieldcap.com/",
    "https://www.decisivepoint.com/",
    # ...
    "https://www.capitalfactory.com/defense/"
]

stop_flag = False

def on_press(key):
    global stop_flag
    if key == keyboard.Key.esc:
        print("\n[!] ESC pressed — stopping...")
        stop_flag = True
        return False

listener = keyboard.Listener(on_press=on_press)
listener.start()

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

print("🚀 Starting browser automation...")
driver = webdriver.Chrome(options=chrome_options)

try:
    for url in urls:
        if stop_flag:
            print("[!] Program stopped by user.")
            break
        print(f"Visiting: {url}")
        try:
            driver.get(url)
            wait_time = random.uniform(4, 7)
            start = time.time()
            while time.time() - start < wait_time:
                if stop_flag:
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error loading {url}: {e}")

finally:
    print("🛑 Stopping browser and listener...")
    driver.quit()
    listener.stop()
    print("✅ Browser closed. Program finished.")
