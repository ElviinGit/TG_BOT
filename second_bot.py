from seleniumbase import Driver
import time
# UC Mode is specifically designed to bypass anti-bot services like Cloudflare
# 'headless=True' in UC mode uses a special 'headed-headless' trick to stay undetected
driver = Driver(uc=True, headless=True)

try:
    url = "https://turbo.az"
    
    # Using uc_open instead of get allows SB to handle potential challenges
    driver.uc_open_with_reconnect(url, reconnect_time=5)
    
    # Sometimes a small manual wait helps the page finish its internal checks
    time.sleep(3)
    
    # If there is a "Verify you are human" checkbox, this can often bypass it:
    driver.uc_gui_handle_captcha() 

    print(f"Page Title: {driver.title}")
    
    # Take a screenshot to verify what the bot actually sees
    driver.save_screenshot("turbo_success.png")

except Exception as e:
    print(f"An error occurred: {e}")
    driver.save_screenshot("debug_error.png")
finally:
    driver.quit()