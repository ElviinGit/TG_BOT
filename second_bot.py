import undetected_chromedriver as uc
import time
driver = uc.Chrome()
driver.get("https//turbo.az")
time.sleep(10)
driver.quit()
print(" closed after 10 second")