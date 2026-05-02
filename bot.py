import telebot
import os
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "This Message is from Elvin's Bot. How can I assist you?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print("Chat ID:", message.chat.id) # for debugging purposes, to see the chat ID in the console
    bot.reply_to(message, "You said: " + message.text)

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running and Alive!"

def run_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Bot_is_Alive!")
    bot.infinity_polling()

