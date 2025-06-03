import os
import time
import asyncio
import threading
import logging
import logging.handlers  # для RotatingFileHandler
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv, set_key
from rss_parser import parse_tasks
from telegram import Bot
from gui_decorations import (
    BG_MAIN, BG_FRAME, HEADER_BG, HEADER_FG, HEADER_FONT,
    BUTTON_BG_SAVE, BUTTON_BG_START, BUTTON_BG_STOP, BUTTON_BG_UPDATE,
    LABEL_FONT, CreateToolTip
)
import webbrowser  # для открытия ссылок

# Остальной код, как ранее, использует parse_tasks() вместо parser.parser()
# Все импорты и логика остались без изменений