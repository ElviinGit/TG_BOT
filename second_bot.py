from seleniumbase import SB

# Use SB context manager for automatic cleanup
with SB(uc=True, xvfb=True, block_images=True) as sb:
    url = "https://turbo.az"
    
    try:
        # We use a longer timeout and avoid the 'reconnect' function 
        # initially to see if a standard UC load works first.
        sb.activate_cdp_mode(url) # CDP mode is often stealthier than standard get
        sb.sleep(5)
        
        # Check if we are challenged
        if "challenges.cloudflare.com" in sb.get_page_source():
            print("Cloudflare detected. Attempting bypass...")
            sb.uc_gui_click_captcha()
            sb.sleep(4)

        print(f"Success! Title: {sb.get_title()}")
        sb.save_screenshot("turbo_final.png")

    except Exception as e:
        print(f"Caught Error: {e}")
        # We don't save screenshot here because if the browser 
        # is crashed, save_screenshot will just throw another error.