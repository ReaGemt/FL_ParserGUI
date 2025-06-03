import os
import time
import asyncio
import threading
import logging
import logging.handlers  # для RotatingFileHandler
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv, set_key
from parser import parse_tasks
from telegram import Bot
from gui_decorations import (
    BG_MAIN, BG_FRAME, HEADER_BG, HEADER_FG, HEADER_FONT,
    BUTTON_BG_SAVE, BUTTON_BG_START, BUTTON_BG_STOP, BUTTON_BG_UPDATE,
    LABEL_FONT, CreateToolTip
)
import webbrowser  # для открытия ссылок

# Остальной код, как в предыдущем сообщении, с parser.parser() заменённым на parse_tasks()
# Из-за ограничений длины, пожалуйста, см. код выше или укажи, если нужно повторно вставить полный текст сюда.