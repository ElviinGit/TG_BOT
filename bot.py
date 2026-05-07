import telebot
import os
from flask import Flask, render_template_string, request
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

operation_logs = ["Waiting For Tasks..."]

def add_log(message):
    operation_logs.append(message)
    if len(operation_logs) > 10:
        operation_logs.pop(0)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Bot Operations Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background-color: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        input, textarea { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #0088cc; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #005f8e; }
        .log-box { height: 250px; overflow-y: scroll; background: #222; color: #0f0; padding: 10px; font-family: monospace; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🤖 Bot Dashboard</h1>
    
    <div class="card">
        <h2>Send a Message</h2>
        <!-- The form sends a POST request to the /send endpoint -->
        <form action="/send" method="POST">
            <label>Secret Password:</label>
            <input type="password" name="secret" placeholder="Enter secret key..." required>
            
            <label>Chat ID:</label>
            <input type="text" name="chat_id" placeholder="e.g., 123456789" required>
            
            <label>Message:</label>
            <textarea name="text" rows="4" placeholder="Type your message here..." required></textarea>
            
            <button type="submit">Send to Telegram</button>
        </form>
    </div>

    <div class="card">
        <h2>Operations Log</h2>
        <div class="log-box">
            {% for log in logs %}
                <div>> {{ log }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "This Message is from Elvin's Bot. How can I assist you?")
    add_log(f"Received /start or /help command from {message.chat.id}")

@bot.message_handler(commands=['myid'])
def send_chat_id(message):
    bot.reply_to(message, f"Your Chat ID is: {message.chat.id}")
    add_log(f"Sent chat ID to {message.chat.id}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print("Chat ID:", message.chat.id) # for debugging purposes, to see the chat ID in the console
    bot.reply_to(message, "You said: " + message.text)
    add_log(f"Echoed message from {message.chat.id}: {message.text}")

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, logs=operation_logs)

@app.route('/send', methods=['POST'])
def send_message_from_web():
    chat_id = request.form.get('chat_id')
    text = request.form.get('text')
    secret = request.form.get('secret')
    if secret != "yob_ana":
        return "Unauthorized person detected", 403
    if not chat_id or not text:
        return "Missing chat_id or text parameter", 400 
    try:
        bot.send_message(chat_id=chat_id, text=text)
        add_log(f"Sent message to {chat_id}: {text}")   
        return "Success! Message sent to Telegram. <br><br> <a href='/'>Go Back</a>"
    except Exception as e:
        add_log(f"Failed to send message to {chat_id}: {str(e)}")
        return f"Failed to send message: {e} <br><br> <a href='/'>Go Back</a>", 500

def run_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Bot_is_Alive!")
    bot.infinity_polling()

