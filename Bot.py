import telebot
import sqlite3
import re
from telebot import types

bot = telebot.TeleBot('6453843079:AAFHVRXmYAKhssF8INHw6h4WfQ1eZv9pu_I')
registered_users = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if user_id in registered_users:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_logout = telebot.types.KeyboardButton('Выйти')
        keyboard.add(button_logout)
        bot.send_message(message.chat.id, 'Вы уже авторизованы. 👍', reply_markup=keyboard)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button_login = telebot.types.KeyboardButton('Войти')
        button_register = telebot.types.KeyboardButton('Зарегистрироваться')
        keyboard.add(button_login, button_register)
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard)

@bot.message_handler(commands=['reg'])
@bot.message_handler(func=lambda message: message.text.lower() == "зарегистрироваться")
def start(message):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(50), surname VARCHAR(50), pass VARCHAR(50), version INTEGER DEFAULT 0, logged_in INTEGER DEFAULT 0)')
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
    if check_user_exists(name, surname):
        bot.send_message(message.chat.id, 'Пользователь уже существует. Попробуйте использовать другое имя или фамилию.')
        return
    bot.send_message(message.chat.id, 'Теперь введите пароль 🔐')
    bot.register_next_step_handler(message, user_pass, name, surname)

def user_pass(message, name, surname):
    password = message.text.strip()
    save_user_data_pass(name, surname, password)
    bot.send_message(message.chat.id, 'Вы зарегистрированы!')

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

def save_user_data_pass(name, surname, password):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, surname, pass) VALUES (?, ?, ?)", (name, surname, password))
    conn.commit()
    cur.close()
    conn.close()

@bot.message_handler(commands=['auth'])
@bot.message_handler(func=lambda message: message.text.lower() == "войти")
def authenticate(message):
    bot.send_message(message.chat.id, 'Введите имя пользователя 👤')
    bot.register_next_step_handler(message, auth_enter_name)

def auth_enter_name(message):
    name = message.text.strip()
    if not validate_russian(name):
        bot.reply_to(message, 'Имя может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, auth_enter_name)
        return
    bot.send_message(message.chat.id, 'А теперь фамилию 👾')
    bot.register_next_step_handler(message, auth_enter_surname, name)

def auth_enter_surname(message, name):
    surname = message.text.strip()
    if not validate_russian(surname):
        bot.reply_to(message, 'Фамилия может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, auth_enter_surname, name)
        return
    if not check_user_exists(name, surname):
        bot.send_message(message.chat.id, 'Пользователь не найден. Попробуй еще раз. 🚫')
        return
    bot.send_message(message.chat.id, 'Теперь введите пароль 🔐')
    bot.register_next_step_handler(message, auth_enter_password, name, surname)

def auth_enter_password(message, name, surname):
    password = message.text.strip()
    if check_password(name, surname, password):
        registered_users[message.from_user.id] = {'name': name, 'surname': surname}
        set_logged_in(name, surname, 1)
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_logout = telebot.types.KeyboardButton('Выйти')
        keyboard.add(button_logout)
        bot.send_message(message.chat.id, 'Вы успешно вошли в аккаунт! 😊', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Неверный пароль. Попробуй еще раз. 🚫')

def check_password(name, surname, password):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ? AND surname = ? AND pass = ?", (name, surname, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

def set_logged_in(name, surname, value):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("UPDATE users SET logged_in = ? WHERE name = ? AND surname = ?", (value, name, surname))
    conn.commit()
    cur.close()
    conn.close()

@bot.message_handler(func=lambda message: message.text.lower() == "выйти")
def handle_logout(message):
    user_id = message.from_user.id
    if user_id in registered_users:
        name = registered_users[user_id]['name']
        surname = registered_users[user_id]['surname']
        registered_users.pop(user_id)  # Удаляем пользователя из словаря
        set_logged_in(name, surname, 0)
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button_login = telebot.types.KeyboardButton('Войти')
        button_register = telebot.types.KeyboardButton('Зарегистрироваться')
        keyboard.add(button_login, button_register)
        bot.send_message(message.chat.id, 'Вы успешно вышли из аккаунта. 👋', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Чтобы выйти из аккаунта, сначала войдите в него.')

bot.polling(none_stop=True)