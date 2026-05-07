from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import telebot
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
BOT_TOKEN = "8655874845:AAGaFPp-OtEg7021pSa2Rup0WKabnIRhcoI"
bot = telebot.TeleBot(BOT_TOKEN)

CAR_ID = {
    "Mercedes": "4",
    "BMW": "3",
    "Ford": "2",
    "Hyundai": "1",
    "Lada": "5",
    "Mitsubishi": "6",
}

def get_car_prices(make_name, year=None):

    make_id = CAR_ID.get(make_name)
    # 1. Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless") 
    # CRITICAL: Make the bot look like a real human using Google Chrome
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        print("Opening turbo.az... Please wait 4 seconds.")

        complete_url = (f"https://turbo.az/autos?q%5Bsort%5D=price_asc&q%5Bmake%5D%5B%5D={make_id}"
                      f"&q%5Byear_from%5D={year}&q%5Byear_to%5D={year}&q%5Bcurrency%5D=azn"
                      f"&q%5Bloan%5D=0&q%5Bbarter%5D=0&q%5Bcrashed%5D=1&q%5Bpainted%5D=1&q%5Bfor_spare_parts%5D=0")
        
        driver.get(complete_url)
        time.sleep(5)  # Wait for the page to load
        
        # Get the page source and parse it
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        #scrap phase
        title_div = soup.find('div', class_='products-title')
        product_table = title_div.find_next_sibling('div', class_='products')
        first_product = product_table.find('div', class_='products-i')
        print("firs prduct defined")
        product_link = first_product.find('a', class_='products-i__link')
        product_full_link = "https://turbo.az" + product_link['href']
        product_price = first_product.find('div', class_='products-i__price products-i__bottom-text').text
        return {
            "price": product_price,
            "link": product_full_link,
        }
    
    except Exception as e:
            print(f"An error occurred: {e}")        
        

    finally:
        # Close the browser
        driver.quit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a car model and I'll fetch the prices for you.")

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