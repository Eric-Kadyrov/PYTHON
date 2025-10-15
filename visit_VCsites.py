import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pynput import keyboard  # for detecting ESC key

# === List of websites ===
urls = [
    "https://www.iqt.org/",
    "https://shieldcap.com/",
    "https://www.decisivepoint.com/",
    "https://www.razorsvc.com/",
    "https://a16z.com/american-dynamism/",
    "https://www.dcvc.com/",
    "https://www.8vc.com/",
    "https://www.lockheedmartin.com/en-us/who-we-are/lockheed-martin-ventures.html",
    "https://www.rtx.com/who-we-are/ventures",
    "https://www.aeroequity.com/ventures/",
    "https://www.redcellpartners.com/",
    "https://washingtonharbour.com/",
    "https://www.nif.fund/",
    "https://seraphim.vc/",
    "https://svc.vc/",
    "https://www.paladincapgroup.com/",
    "https://www.nightdragon.com/",
    "https://www.americasfrontier.org/",
    "https://p72.vc/defense-tech/",
    "https://www.harpoon.vc/",
    "https://www.newnorthvc.com/",
    "https://www.synventures.com/",
    "https://www.luxcapital.com/",
    "https://www.nato.int/cps/en/natohq/topics_216199.htm",
    "https://airbusventures.com/",
    "https://www.safran-group.com/safran-corporate-ventures",
    "https://www.leonardo.com/en/innovation/leonardo-ventures",
    "https://www.thalesgroup.com/en/innovation/venture",
    "https://www.honeywell.com/us/en/company/ventures",
    "https://www.boozallen.com/solutions/ai-data-analytics/booz-allen-ventures.html",
    "https://www.spacecapital.com/",
    "https://www.spacefund.com/",
    "https://www.starbridgevc.com/",
    "https://www.promus.vc/",
    "https://www.alpinespace.vc/",
    "https://www.scout.vc/",
    "https://www.embedded.ventures/",
    "https://starburst.aero/",
    "https://mseq.vc/",
    "https://www.ubiquity.vc/",
    "https://eclipse.vc/",
    "https://root.vc/",
    "https://typeone.vc/",
    "https://www.karman-ventures.com/",
    "https://www.iqcapital.vc/",
    "https://www.amadeuscapital.com/",
    "https://oup.vc/",
    "https://parkwalkadvisors.com/",
    "https://www.j2vp.com/",
    "https://www.capitalfactory.com/defense/"
]

# === Global flag to detect ESC ===
stop_flag = False

def on_press(key):
    global stop_flag
    try:
        if key == keyboard.Key.esc:
            print("\n[!] ESC pressed — stopping the program...")
            stop_flag = True
            return False  # stop listener
    except Exception as e:
        print(f"Error detecting key: {e}")

# === Start background thread to listen for ESC ===
listener = keyboard.Listener(on_press=on_press)
listener.start()

# === Setup Chrome options ===
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Optional: Uncomment to run headless (no browser window)
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

try:
    for url in urls:
        if stop_flag:
            print("[!] Program stopped by user.")
            break

        print(f"Visiting: {url}")
        try:
            driver.get(url)
            for _ in range(5):
                if stop_flag:
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error loading {url}: {e}")

finally:
    driver.quit()
    listener.stop()
    print("✅ Browser closed. Program finished.")
