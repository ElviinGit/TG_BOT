import undetected_chromedriver as uc
import time
with uc.Chrome(version_main=147) as driver:
    driver.get("https://turbo.az")
    time.sleep(10)
    driver.save_screenshot("debug_error.png")
    print(" closed after 10 second")