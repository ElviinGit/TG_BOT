from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import telebot
from dotenv import load_dotenv
import os
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
URL = os.environ.get("URL")
bot = telebot.TeleBot(BOT_TOKEN)

CAR_ID = {
    "Mercedes": "4",
    "BMW": "3",
    "Ford": "2",
    "Hyundai": "1",
    "Lada": "5",
    "Mitsubishi": "6",
    "Nissan": "7",
    "Kia": "8",
    "Audi": "9",
    "Daewoo": "11",
    "Byd": "51",
    "Changan": "163",
}

def get_car_prices(make_name, year=None):
    make_id = CAR_ID.get(make_name)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")  # try headless=new or remove for debugging
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        complete_url = (
            f"{URL}/autos?q%5Bsort%5D=price_asc&q%5Bmake%5D%5B%5D={make_id}"
            f"&q%5Byear_from%5D={year}&q%5Byear_to%5D={year}&q%5Bcurrency%5D=azn"
            f"&q%5Bloan%5D=0&q%5Bbarter%5D=0&q%5Bcrashed%5D=1&q%5Bpainted%5D=1&q%5Bfor_spare_parts%5D=0"
        )
        driver.get(complete_url)

        # Wait up to 15s for the products container or a known element to appear
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.products")))
        except Exception:
            # Save debug artifacts
            timestamp = int(time.time())
            screenshot = f"/tmp/page_{timestamp}.png"
            htmlfile = f"/tmp/page_{timestamp}.html"
            driver.save_screenshot(screenshot)
            with open(htmlfile, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise RuntimeError(f"Timed out waiting for products. Saved {screenshot} and {htmlfile} for inspection.")

        soup = BeautifulSoup(driver.page_source, "html.parser")

        title_div = soup.find("div", class_="products-title")
        if not title_div:
            # Save debug artifacts
            timestamp = int(time.time())
            htmlfile = f"/tmp/page_no_title_{timestamp}.html"
            with open(htmlfile, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise ValueError(f"products-title not found in page. Saved HTML to {htmlfile}")

        product_table = title_div.find_next_sibling("div", class_="products")
        if not product_table:
            raise ValueError("products sibling not found after products-title")

        first_product = product_table.find("div", class_="products-i")
        if not first_product:
            raise ValueError("No product entries found in products container")

        product_link = first_product.find("a", class_="products-i__link")
        product_full_link = f"{URL}{product_link['href']}" if product_link else None
        price_div = first_product.find("div", class_="products-i__price products-i__bottom-text")
        product_price = price_div.get_text(strip=True) if price_div else None

        return {"price": product_price, "link": product_full_link}

    finally:
        driver.quit()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a car model and I'll fetch the prices for you.")

#user input validation
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ Please provide both car model and year (e.g., 'Mercedes 2020').")
        return
    make_name = parts[0].upper() if parts[0].upper() in CAR_ID else parts[0].capitalize()
    year = parts[1]
    if not year.isdigit() or len(year) != 4:
        bot.reply_to(message, "❌ Please provide a valid year (e.g., '2020').")
        return
    loading_msg = bot.reply_to(message, "Processing your request... Please wait.")  
    data = get_car_prices(make_name, year)
    bot.delete_message(chat_id=loading_msg.chat.id, message_id=loading_msg.message_id)                                                          
    if not data:
        response = "❌ Could not find any cars at the moment."
        bot.send_message(chat_id=message.chat.id, text=response)
    elif data.get("error"):
        bot.send_message(chat_id=message.chat.id, text=f"❌ Error occurred: {data['error']}")
    else:
        caption = (f"✅ Car: {make_name} {year}\n"
                   f"💰 Price: {data['price']}\n"
                   f"Link : {data['link']}")                                                                   
        bot.send_message(chat_id=message.chat.id, text=caption, parse_mode="Markdown")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
