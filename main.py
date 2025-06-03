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

# ... (весь остальной код остаётся без изменений, кроме вызова parse_tasks)
# заменим parser.parser() на parse_tasks()

# Найди и замени внутри bot_loop():
# tasks_list = parser.parser() --> tasks_list = parse_tasks()

# Предполагается, что весь остальной код main.py корректный и остаётся без изменений.