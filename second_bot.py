import undetected_chromedriver as uc
import time
driver = uc.Chrome()
try:
    driver.get("https//turbo.az")
    time.sleep(10)
except Exception as e:
        driver.save_screenshot("debug_error.png")
driver.quit()
print(" closed after 10 second")