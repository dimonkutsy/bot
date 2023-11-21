import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('6453843079:AAFHVRXmYAKhssF8INHw6h4WfQ1eZv9pu_I')
name = None


@bot.message_handler(commands=['start'])
def start(message):  
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Введите ваше имя')
    bot.register_next_step_handler(message, user_name)
def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)   
def user_pass(message):
    password = message.text.strip()
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован!', reply_markup=markup)
    
@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Покажи график!', url='https://music.yandex.ru/users/cutsiy.d/playlists/3')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Изменить!', callback_data='edit')
    btn3 = types.InlineKeyboardButton('Удалить!', callback_data='delete')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Бот график работ!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback(callback):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'Имя: {el[1]}, пароль: {el[2]}\n'

    cur.close()
    conn.close()
    bot.send_message(callback.message.chat.id, info)

bot.polling(none_stop=True)
