import undetected_chromedriver as uc
import time
options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(version_main=147, options=options)
try:
    driver.get("https://turbo.az")
    print(driver.title)
except Exception as e:
    driver.save_screenshot("debug_error.png")
driver.quit()