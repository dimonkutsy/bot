
import telebot
import sqlite3
import re
from telebot import types

bot = telebot.TeleBot('6453843079:AAFHVRXmYAKhssF8INHw6h4WfQ1eZv9pu_I')

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(50), surname VARCHAR(50), pass VARCHAR(50), version INTEGER DEFAULT 0)')
    conn.commit()
    cur.close()
    conn.close()

    if is_user_authenticated(message.from_user.id):
        # Если пользователь уже авторизован, показываем кнопку "Выйти"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton('Выйти')
        markup.add(button1)
        bot.send_message(message.chat.id, 'Вы уже авторизованы. 😊', reply_markup=markup)
    else:
        # Если пользователь не авторизован, показываем кнопки "Войти" и "Зарегистрироваться"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton('Войти')
        button2 = types.KeyboardButton('Зарегистрироваться')
        markup.add(button1, button2)
        bot.send_message(message.chat.id, 'Зарегистрируйтесь или войдите 👾', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Войти')
def authenticate_command(message):
    if is_user_authenticated(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы уже авторизованы. 😊')
    else:
        authenticate(message)

@bot.message_handler(func=lambda message: message.text == 'Выйти')
def logout_command(message):
    if is_user_authenticated(message.from_user.id):
        unmark_user_authenticated(message.from_user.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton('Войти')
        button2 = types.KeyboardButton('Зарегистрироваться')
        markup.add(button1, button2)
        bot.send_message(message.chat.id, 'Вы успешно вышли! 👋', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вы уже вышли. 😊')
        # Опционально можно добавить кнопку "Войти" для пользователя, который уже вышел
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton('Войти')
        button2 = types.KeyboardButton('Зарегистрироваться')
        markup.add(button1, button2)
        bot.send_message(message.chat.id, 'Хотите войти снова? 😉', reply_markup=markup)

def unmark_user_authenticated(user_id):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("UPDATE users SET version = 0 WHERE id = ?", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

@bot.message_handler(func=lambda message: message.text == 'Зарегистрироваться')
def register_command(message):
    start_registration(message)

def start_registration(message):
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

    if check_user_exists(name, surname, ''):
        bot.send_message(message.chat.id, 'Пользователь с таким именем и фамилией уже зарегистрирован. 🚫')
    else:
        bot.send_message(message.chat.id, 'Теперь введите пароль 🔐')
        bot.register_next_step_handler(message, user_pass, name, surname)

def user_pass(message, name, surname):
    password = message.text.strip()

    save_user_data_pass(name, surname, password)
    bot.send_message(message.chat.id, 'Регистрация успешна!')

def validate_russian(text):
    return bool(re.match(r'^[а-яА-ЯёЁ\s]+$', text))

def check_user_exists(name, surname, password):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    if password:
        cur.execute("SELECT * FROM users WHERE name = ? AND surname = ? AND pass = ?", (name, surname, password))
    else:
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

def is_user_authenticated(user_id):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ? AND version = 1", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

def authenticate(message):
    if is_user_authenticated(message.from_user.id):
        bot.send_message(message.chat.id, 'Вы уже авторизованы. 😊')
    else:
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

    if not check_user_exists(name, surname, ''):
        bot.send_message(message.chat.id, 'Пользователь не найден. Попробуй еще раз. 🚫')
        return

    bot.send_message(message.chat.id, 'Введите пароль 🔐')
    bot.register_next_step_handler(message, auth_enter_password, name, surname)

def auth_enter_password(message, name, surname):
    password = message.text.strip()

    if check_user_exists(name, surname, password):
        # Пользователь авторизован
        mark_user_authenticated(message.from_user.id)
        # Показываем кнопку "Выйти"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton('Выйти')
        markup.add(button1)
        bot.send_message(message.chat.id, 'Аутентификация успешна! 👍', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Неверный пароль. Попробуй еще раз. 🚫')

def mark_user_authenticated(user_id):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("UPDATE users SET version = 1 WHERE id = ?", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def unmark_user_authenticated(user_id):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("UPDATE users SET version = 0 WHERE id = ?", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

bot.polling(none_stop=True)