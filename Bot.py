import telebot
import sqlite3
import re

bot = telebot.TeleBot('6453843079:AAFHVRXmYAKhssF8INHw6h4WfQ1eZv9pu_I')

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(50), surname VARCHAR(50), pass VARCHAR(50), version INTEGER DEFAULT 0)')
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Введи своё имя 👾')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    name = message.text.strip()

    if not validate_russian(name):
        bot.reply_to(message, 'Имя может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, user_name)
        return

    bot.send_message(message.chat.id, 'А теперь фамилию 👾')
    bot.register_next_step_handler(message, user_surname, name)

def user_surname(message, name):
    surname = message.text.strip()

    if not validate_russian(surname):
        bot.reply_to(message, 'Фамилия может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, user_surname, name)
        return

    user_exists = check_user_exists(name, surname)

    if user_exists:
        bot.send_message(message.chat.id, 'Пользователь с такими данными уже зарегистрирован. Попробуй еще раз.')
        bot.register_next_step_handler(message, user_name)
    else:
        save_user_data(name, surname)
        bot.send_message(message.chat.id, 'Регистрация успешна!')
        # В этом месте данные пользователя успешно сохранены в базе данных

def validate_russian(text):
    return bool(re.match(r'^[а-яА-ЯёЁ\s]+$', text))

def check_user_exists(name, surname):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ? AND surname = ?", (name, surname))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

def save_user_data(name, surname):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, surname) VALUES (?, ?)", (name, surname))
    conn.commit()
    cur.close()
    conn.close()

@bot.message_handler(commands=['auth'])
def authenticate(message):
    bot.send_message(message.chat.id, 'Введите имя пользователя 👤')
    bot.register_next_step_handler(message, check_username)

def check_username(message):
    username = message.text.strip()

    if username == 'admin':
        bot.send_message(message.chat.id, 'Введите пароль 🔐')
        bot.register_next_step_handler(message, check_password)
    else:
        bot.send_message(message.chat.id, 'Неверное имя пользователя. Попробуйте еще раз.')
        bot.register_next_step_handler(message, check_username)

def check_password(message):
    password = message.text.strip()

    if password == 'admin':
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add(telebot.types.KeyboardButton('Список пользователей 📋'))
        bot.send_message(message.chat.id, 'Вы успешно авторизованы! Выберите действие:', reply_markup=markup)
        bot.register_next_step_handler(message, handle_admin_action)
    else:
        bot.send_message(message.chat.id, 'Неверный пароль. Попробуйте еще раз.')
        bot.register_next_step_handler(message, check_password)

def handle_admin_action(message):
    if message.text == 'Список пользователей 📋':
        users = get_user_list()
        if not users:
            bot.send_message(message.chat.id, 'На данный момент нет зарегистрированных пользователей.')
        else:
            user_list = '\n'.join(users)
            bot.send_message(message.chat.id, f'Список зарегистрированных пользователей:\n{user_list}')
    else:
        bot.send_message(message.chat.id, 'Неверное действие. Выберите корректную опцию.')

def get_user_list():
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("SELECT name, surname FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return [f"{name} {surname}" for name, surname in users]

bot.polling(none_stop=True)
