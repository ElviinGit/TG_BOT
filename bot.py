import telebot
import os
from flask import Flask, request
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "This Message is from Elvin's Bot. How can I assist you?")

@bot.message_handler(commands=['myid'])
def send_chat_id(message):
    bot.reply_to(message, f"Your Chat ID is: {message.chat.id}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print("Chat ID:", message.chat.id) # for debugging purposes, to see the chat ID in the console
    bot.reply_to(message, "You said: " + message.text)

app = Flask(__name__)

@app.route('/')
def index():
    return "I just updated my index page! This is a simple Flask app running alongside the Telegram bot."

@app.route('/send', methods=['GET'])
def send_mesasge_from_web():
    chat_id = request.args.get('chat_id')
    text = request.args.get('text')
    secret = request.args.get('secret')
    if secret != "yob_ana":
        return "Unauthorized person detected", 403
    if not chat_id or not text:
        return "Missing chat_id or text parameter", 400 
    try:
        bot.send_message(chat_id=chat_id, text=text)
        return "Message sent successfully!"
    except Exception as e:
        return f"Failed to send message: {str(e)}", 500 

def run_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Bot_is_Alive!")
    bot.infinity_polling()

