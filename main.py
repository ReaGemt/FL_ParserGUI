import os
import time
import asyncio
import threading
import logging
import logging.handlers  # для RotatingFileHandler
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv, set_key
from parser import parse_tasks  # обновлённый импорт
from telegram import Bot
from gui_decorations import (
    BG_MAIN, BG_FRAME, HEADER_BG, HEADER_FG, HEADER_FONT,
    BUTTON_BG_SAVE, BUTTON_BG_START, BUTTON_BG_STOP, BUTTON_BG_UPDATE,
    LABEL_FONT, CreateToolTip
)
import webbrowser  # для открытия ссылок

# Глобальные переменные
current_filter = ""
restart_now_event = threading.Event()
ENV_FILE = '.env'
load_dotenv(ENV_FILE)
bot_thread = None
stop_event = threading.Event()

# Логирование
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Остальной код остаётся без изменений, кроме parser.parser() -> parse_tasks()
# (код функции bot_loop и т.д.)