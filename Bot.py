import telebot
from telebot import types

token = '6488401011:AAEWjxtd4ljpTzX_wt4bWNNp2QuT5AXQOiY'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Я бот для графиков, пока ничаго не умею.")

# Handle '/start' and '/help'
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message, """\
Я пока ничаго не умею))\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message, 'Отстань')


bot.infinity_polling()