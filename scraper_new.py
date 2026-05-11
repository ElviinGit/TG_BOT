from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
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
    
    # 1. Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gcm-registration")
    
    # CRITICAL: Force a desktop window size so you don't get the mobile site layout
    chrome_options.add_argument("--window-size=1920,1080")

    # Make the bot look like a real human
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    "source": '''
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    Object.defineProperty(navigator, 'plugins', {
            get: function() { return {"0":{"0":{}},"1":{"0":{}},"2":{"0":{},"1":{}}}; }
    });
    Object.defineProperty(navigator, 'languages', {
        get: () => ["en-US", "en"]
    });
    Object.defineProperty(navigator, 'mimeTypes', {
        get: function() { return {"0":{},"1":{},"2":{},"3":{}}; }
    });

    window.screenY=23;
    window.screenTop=23;
    window.outerWidth=1337;
    window.outerHeight=825;
    window.chrome =
    {
      app: {
        isInstalled: false,
      },
      webstore: {
        onInstallStageChanged: {},
        onDownloadProgress: {},
      },
      runtime: {
        PlatformOs: {
          MAC: 'mac',
          WIN: 'win',
          ANDROID: 'android',
          CROS: 'cros',
          LINUX: 'linux',
          OPENBSD: 'openbsd',
        },
        PlatformArch: {
          ARM: 'arm',
          X86_32: 'x86-32',
          X86_64: 'x86-64',
        },
        PlatformNaclArch: {
          ARM: 'arm',
          X86_32: 'x86-32',
          X86_64: 'x86-64',
        },
        RequestUpdateCheckStatus: {
          THROTTLED: 'throttled',
          NO_UPDATE: 'no_update',
          UPDATE_AVAILABLE: 'update_available',
        },
        OnInstalledReason: {
          INSTALL: 'install',
          UPDATE: 'update',
          CHROME_UPDATE: 'chrome_update',
          SHARED_MODULE_UPDATE: 'shared_module_update',
        },
        OnRestartRequiredReason: {
          APP_UPDATE: 'app_update',
          OS_UPDATE: 'os_update',
          PERIODIC: 'periodic',
        },
      },
    };
    window.navigator.chrome =
    {
      app: {
        isInstalled: false,
      },
      webstore: {
        onInstallStageChanged: {},
        onDownloadProgress: {},
      },
      runtime: {
        PlatformOs: {
          MAC: 'mac',
          WIN: 'win',
          ANDROID: 'android',
          CROS: 'cros',
          LINUX: 'linux',
          OPENBSD: 'openbsd',
        },
        PlatformArch: {
          ARM: 'arm',
          X86_32: 'x86-32',
          X86_64: 'x86-64',
        },
        PlatformNaclArch: {
          ARM: 'arm',
          X86_32: 'x86-32',
          X86_64: 'x86-64',
        },
        RequestUpdateCheckStatus: {
          THROTTLED: 'throttled',
          NO_UPDATE: 'no_update',
          UPDATE_AVAILABLE: 'update_available',
        },
        OnInstalledReason: {
          INSTALL: 'install',
          UPDATE: 'update',
          CHROME_UPDATE: 'chrome_update',
          SHARED_MODULE_UPDATE: 'shared_module_update',
        },
        OnRestartRequiredReason: {
          APP_UPDATE: 'app_update',
          OS_UPDATE: 'os_update',
          PERIODIC: 'periodic',
        },
      },
    };
    ['height', 'width'].forEach(property => {
        const imageDescriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, property);

        // redefine the property with a patched descriptor
        Object.defineProperty(HTMLImageElement.prototype, property, {
            ...imageDescriptor,
            get: function() {
                // return an arbitrary non-zero dimension if the image failed to load
            if (this.complete && this.naturalHeight == 0) {
                return 20;
            }
                return imageDescriptor.get.apply(this);
            },
        });
    });

    const getParameter = WebGLRenderingContext.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Open Source Technology Center';
        }
        if (parameter === 37446) {
            return 'Mesa DRI Intel(R) Ivybridge Mobile ';
        }

        return getParameter(parameter);
    };

    const elementDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');

    Object.defineProperty(HTMLDivElement.prototype, 'offsetHeight', {
        ...elementDescriptor,
        get: function() {
            if (this.id === 'modernizr') {
            return 1;
            }
            return elementDescriptor.get.apply(this);
        },
    });
    '''
})

    
    try:
        print("Wait for site opening")
        complete_url = (f"{URL}/autos?q%5Bsort%5D=price_asc&q%5Bmake%5D%5B%5D={make_id}"
                      f"&q%5Byear_from%5D={year}&q%5Byear_to%5D={year}&q%5Bcurrency%5D=azn"
                      f"&q%5Bloan%5D=0&q%5Bbarter%5D=0&q%5Bcrashed%5D=1&q%5Bpainted%5D=1&q%5Bfor_spare_parts%5D=0")
        
        driver.get(complete_url)
        
        # 2. Smart Wait: Wait up to 15 seconds specifically for the target element to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "products-title"))
        )
        print("Page fully loaded and target element found.")
        
        # Get the page source and parse it
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Scrap phase
        title_div = soup.find('div', class_='products-title')
        product_table = title_div.find_next_sibling('div', class_='products')
        first_product = product_table.find('div', class_='products-i')
        print("First product defined")
        
        product_link = first_product.find('a', class_='products-i__link')
        product_full_link = f"{URL}{product_link['href']}"
        product_price = first_product.find('div', class_='products-i__price products-i__bottom-text').text
        
        return {
            "price": product_price.strip(),
            "link": product_full_link,
        }    
        
    except Exception as e:
        # 3. Debugging: Save what the browser sees to diagnose bot blocking
        driver.save_screenshot("debug_error.png")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"An error occurred: {e}")
        print("Saved 'debug_error.png' and 'debug_page.html' to check what the server saw.")
        return None
        
    finally:
        # Close the browser
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
