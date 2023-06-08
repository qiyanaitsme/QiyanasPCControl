import telebot
import os
import time
import subprocess
import platform
import uuid
import psutil
import requests
import re
import time
import socket
from PIL import ImageGrab
from telebot import types

# Чтение токена из файла token.txt
with open("token.txt", "r") as file:
    token = file.read().strip()

bot = telebot.TeleBot(token)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    image_path = os.path.join(os.getcwd(), 'satara.jpg')
    with open(image_path, 'rb') as photo:
        bot.send_photo(chat_id, photo)

    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1)
    bot.send_message(chat_id, "Привет! Я бот управления компьютером от Сатары. Чем могу помочь?")

    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1)
    bot.send_message(chat_id, "Можете посетить мой профиль на GITHUB. Тут всегда актуальная версия бота.:")
    bot.send_message(chat_id, "https://github.com/sataraitsme/satarapccontrol")

    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1)
    bot.send_message(chat_id, "Также вы можете связаться со мной в Telegram:")
    bot.send_message(chat_id, "https://t.me/sherbyaakodanel")

    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1)
    show_actions(chat_id)

def show_actions(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    shutdown_button = types.InlineKeyboardButton("Выключение ПК 🔌", callback_data="shutdown")
    restart_button = types.InlineKeyboardButton("Перезагрузка ПК ⌚", callback_data="restart")
    sleep_button = types.InlineKeyboardButton("Спящий режим 😴", callback_data="sleep")
    network_info_button = types.InlineKeyboardButton("Инфа о IP 📲", callback_data="network_info")
    screenshot_button = types.InlineKeyboardButton("Скрин Рабочего Стола 📸", callback_data="screenshot")
    system_info_button = types.InlineKeyboardButton("Инфа о PC 💻", callback_data="system_info")
    load_button = types.InlineKeyboardButton("Нагруженность 💪", callback_data="load")
    send_file_button = types.InlineKeyboardButton("Отправить файл 📁", callback_data="send_file")
    open_file_button = types.InlineKeyboardButton("Открыть файл 📂", callback_data="open_file")
    markup.add(shutdown_button, restart_button, sleep_button, network_info_button, screenshot_button, system_info_button, load_button, send_file_button, open_file_button)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    chat_id = call.message.chat.id
    if call.data == 'shutdown':
        os.system('shutdown /s /t 0')
        bot.send_message(chat_id, "Компьютер выключается...")
    elif call.data == 'restart':
        os.system('shutdown /r /t 0')
        bot.send_message(chat_id, "Компьютер перезагружается...")
    elif call.data == 'sleep':
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        bot.send_message(chat_id, "Компьютер переходит в спящий режим...")
    elif call.data == 'network_info':
        show_network_info(chat_id)
    elif call.data == 'screenshot':
        take_screenshot(chat_id)
    elif call.data == 'system_info':
        show_system_info(chat_id)
    elif call.data == 'load':
        show_load_info(chat_id)
    elif call.data == 'send_file':
        bot.send_message(chat_id, "Введите путь к папке, откуда вы хотите отправить файл:")
        bot.register_next_step_handler(call.message, get_folder_path)
    elif call.data == 'open_file':
        bot.send_message(chat_id, "Введите путь до файла, который необходимо открыть:")
        bot.register_next_step_handler(call.message, open_file)

    show_actions(chat_id)

def get_folder_path(message):
    chat_id = message.chat.id
    folder_path = message.text
    user_data[chat_id] = {'folder_path': folder_path}
    bot.send_message(chat_id, "Теперь отправьте файл, который вы хотите сохранить в указанной папке:")
    bot.register_next_step_handler(message, save_file)

def save_file(message):
    chat_id = message.chat.id
    folder_path = user_data[chat_id]['folder_path']
    file_info = bot.get_file(message.document.file_id)
    file_content = bot.download_file(file_info.file_path)

    file_path = os.path.join(folder_path, message.document.file_name)
    with open(file_path, 'wb') as file:
        file.write(file_content)

    bot.send_message(chat_id, f"Файл {message.document.file_name} успешно сохранён в папке {folder_path}")
    show_actions(chat_id)

def open_file(message):
    chat_id = message.chat.id
    file_path = message.text

    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', file_path])
        else:
            subprocess.Popen(['xdg-open', file_path])
        bot.send_message(chat_id, f"Файл {file_path} успешно открыт")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при открытии файла: {str(e)}")

    show_actions(chat_id)

def show_network_info(chat_id):
    external_ip = requests.get('https://api.ipify.org').text
    geoip_response = requests.get(f'http://ip-api.com/json/{external_ip}').json()
    mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    network_info = f"Внешний IP: {external_ip}\n"
    network_info += f"Страна: {geoip_response['country']}\n"
    network_info += f"Регион: {geoip_response['regionName']}\n"
    network_info += f"Город: {geoip_response['city']}\n"
    network_info += f"Часовой пояс: {geoip_response['timezone']}\n"
    network_info += f"Имя хоста: {socket.gethostname()}\n"

    bot.send_message(chat_id, "Информация о сети:\n" + network_info)

def take_screenshot(chat_id):
    screenshot_filename = 'screenshot.png'
    ImageGrab.grab().save(screenshot_filename)
    with open(screenshot_filename, "rb") as photo:
        bot.send_photo(chat_id, photo)
    os.remove(os.path.join(os.getcwd(), screenshot_filename))

def show_system_info(chat_id):
    system_info = f"ОС: {platform.system()}\n"
    system_info += f"Имя компьютера: {platform.node()}\n"
    system_info += f"Архитектура: {platform.machine()}\n"
    system_info += f"Версия ОС: {platform.version()}\n"
    system_info += f"Имя пользователя: {os.getlogin()}\n"

    bot.send_message(chat_id, "Информация о компьютере:\n" + system_info)

def show_load_info(chat_id):
    cpu_load = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    load_info = f"Загрузка ЦП: {cpu_load}%\n"
    load_info += f"Использование памяти: {memory_usage}%\n"
    load_info += f"Использование диска: {disk_usage}%\n"

    bot.send_message(chat_id, "Информация о нагрузке:\n" + load_info)

bot.polling()
