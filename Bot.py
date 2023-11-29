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

#При старте попросит ввести имя
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def user_name(message):
    name = message.text.strip()

    if not validate_russian(name):
        bot.reply_to(message, 'Имя может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, user_name)
        return

    bot.send_message(message.chat.id, 'А теперь фамилию 👾')
    bot.register_next_step_handler(message, user_surname, name)


#Эта функция хочет фамилию, без неё никак
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def user_surname(message, name):
    surname = message.text.strip()

    if not validate_russian(surname):
        bot.reply_to(message, 'Фамилия может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, user_surname, name)
        return

    bot.send_message(message.chat.id, 'Теперь введите пароль 🔐')
    bot.register_next_step_handler(message, user_pass, name, surname)

#Эта функция попросит пароль
#^^^^^^^^^^^^^^^^^^^^^^^^^^^
def user_pass(message, name, surname):
    password = message.text.strip()

    save_user_data_pass(name, surname, password)
    bot.send_message(message.chat.id, 'Регистрация успешна!')

#Проверка русских символов
#^^^^^^^^^^^^^^^^^^^^^^^^^
def validate_russian(text):
    return bool(re.match(r'^[а-яА-ЯёЁ\s]+$', text))

#Эта функция проверяет, зарегистрирован ли текущий пользователь
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def check_user_exists(name, surname, password):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ? AND surname = ? AND pass = ?", (name, surname, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

#Сохраняет данные пользователя (имя, фамилию, пароль) в базе данных
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def save_user_data_pass(name, surname, password):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, surname, pass) VALUES (?, ?, ?)", (name, surname, password))
    conn.commit()
    cur.close()
    conn.close()

#Реализовать аутентификацию
#^^^^^^^^^^^^^^^^^^^^^^^^^^

# Реализация аутентификации по имени, фамилии и паролю
# Шаг 1: Запрос имени пользователя
@bot.message_handler(commands=['auth'])
def authenticate(message):
    bot.send_message(message.chat.id, 'Введите имя пользователя 👤')
    bot.register_next_step_handler(message, auth_enter_name)

def auth_enter_name(message):
    name = message.text.strip()
    # Проверяем введенное имя
    
    if not validate_russian(name):
        bot.reply_to(message, 'Имя может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, auth_enter_name)
        return

    # Шаг 2: Запрос фамилии пользователя
    bot.send_message(message.chat.id, 'А теперь фамилию 👾')
    bot.register_next_step_handler(message, auth_enter_surname, name)

def auth_enter_surname(message, name):
    surname = message.text.strip()

    # Проверяем введенную фамилию
    if not validate_russian(surname):
        bot.reply_to(message, 'Фамилия может содержать только русские буквы. Попробуй еще раз.')
        bot.register_next_step_handler(message, auth_enter_surname, name)
        return

    # Проверка наличия пользователя в базе данных
    if not check_user_exists(name, surname):
        bot.send_message(message.chat.id, 'Вы не зарегистрированы. 🚫')
        return

    # Шаг 3: Запрос пароля пользователя
    bot.send_message(message.chat.id, 'Теперь введите пароль 🔐')
    bot.register_next_step_handler(message, auth_enter_password, name, surname)

def auth_enter_password(message, name, surname):
    password = message.text.strip()

    # Проверяем введенный пароль
    # Здесь можно добавить дополнительную логику проверки (например, длина пароля, специальные символы и т.д.)
    # Если пароль проходит все проверки, можно проводить аутентификацию в базе данных

    # Проверка аутентификации
    if check_user_password(name, surname, password):
        bot.send_message(message.chat.id, 'Аутентификация успешна! 👍')
    else:
        bot.send_message(message.chat.id, 'Неверный пароль. Попробуй еще раз. 🚫')

def check_user_password(name, surname, password):
    conn = sqlite3.connect('bd.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ? AND surname = ?", (name, surname))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is not None and user[3] == password:
        return True
    return False

# ...



bot.polling(none_stop=True)
