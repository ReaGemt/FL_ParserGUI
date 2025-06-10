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
import sys
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

current_filter = ""  # Глобальная переменная для динамического фильтра
restart_now_event = threading.Event()  # Новое событие для немедленного запуска

# Загружаем переменные окружения
ENV_FILE = 'dist/.env'
load_dotenv(ENV_FILE)

# Глобальные переменные для управления потоком бота
bot_thread = None
stop_event = threading.Event()

# Настройка базового логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def update_logging_config(log_level, enable_file_logging):
    """Обновляет настройки логгера: уровень и наличие файлового обработчика."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    # Удаляем существующие файловые обработчики
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    if enable_file_logging:
        file_handler = logging.handlers.RotatingFileHandler("dist/app.log", maxBytes=5 * 1024 * 1024, backupCount=3,
                                                            encoding="utf-8")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    logger.info(
        f"Логирование обновлено: уровень {log_level}, запись в файл {'включена' if enable_file_logging else 'выключена'}")


def save_config(token, chat_id, task_filter, rss_url, period, log_level, file_logging, telegram_enabled, excel_enabled):
    """Сохраняет/обновляет настройки в файле .env."""
    if os.path.exists(ENV_FILE):
        set_key(ENV_FILE, 'TOKEN', token, quote_mode='never')
        set_key(ENV_FILE, 'TELEGRAM_CHAT_ID', chat_id, quote_mode='never')
        set_key(ENV_FILE, 'TASK_FILTER', task_filter, quote_mode='never')
        set_key(ENV_FILE, 'RSS_URL', rss_url, quote_mode='never')
        set_key(ENV_FILE, 'PERIOD', period, quote_mode='never')  # период в минутах
        set_key(ENV_FILE, 'LOG_LEVEL', log_level, quote_mode='never')
        set_key(ENV_FILE, 'ENABLE_FILE_LOGGING', '1' if file_logging else '0', quote_mode='never')
        set_key(ENV_FILE, 'ENABLE_TELEGRAM', '1' if telegram_enabled else '0', quote_mode='never')
        set_key(ENV_FILE, 'ENABLE_EXCEL', '1' if excel_enabled else '0', quote_mode='never')
    else:
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(f'TOKEN={token}\n')
            f.write(f'TELEGRAM_CHAT_ID={chat_id}\n')
            f.write(f'TASK_FILTER={task_filter}\n')
            f.write(f'RSS_URL={rss_url}\n')
            f.write(f'PERIOD={period}\n')
            f.write(f'LOG_LEVEL={log_level}\n')
            f.write(f'ENABLE_FILE_LOGGING={"1" if file_logging else "0"}\n')
            f.write(f'ENABLE_TELEGRAM={"1" if telegram_enabled else "0"}\n')
            f.write(f'ENABLE_EXCEL={"1" if excel_enabled else "0"}\n')
    messagebox.showinfo("Сохранено", "Настройки сохранены успешно!")
    update_logging_config(log_level, file_logging)


def load_config():
    """Загружает настройки из файла .env с значениями по умолчанию."""
    config = {
        'TOKEN': '',
        'TELEGRAM_CHAT_ID': '',
        'TASK_FILTER': '',
        'RSS_URL': '',
        'PERIOD': '1',  # период по умолчанию в минутах
        'LOG_LEVEL': 'INFO',
        'ENABLE_FILE_LOGGING': '',
        'ENABLE_TELEGRAM': '',
        'ENABLE_EXCEL': ''
    }
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, val = line.split('=', 1)
                    config[key.strip()] = val.strip()
    return config


async def bot_loop(telegram_enabled, excel_enabled, task_filter, timer_callback, status_callback, stop_event):
    """
    Асинхронный цикл работы бота: парсинг задач, отправка сообщений в Telegram,
    сохранение данных в Excel, обновление таймера и статуса.

    После обработки задач статус обновляется на:
      "Парсинг окончен. Следующий запуск через X мин."
    И далее, в течение задержки, происходит обратный отсчет.
    """
    start_time = time.time()
    if telegram_enabled:
        try:
            token_value = os.getenv('TOKEN')
            if not token_value:
                logger.error("TOKEN не указан в .env")
                telegram_enabled = False
            else:
                bot = Bot(token=token_value)
        except Exception as e:
            logger.exception(f"Ошибка инициализации Telegram Bot: {e}")
            telegram_enabled = False
    else:
        bot = None

    try:
        period_min = float(os.getenv('PERIOD', 1))  # период в минутах
    except ValueError:
        period_min = 1
    period_sec = period_min * 60  # преобразуем в секунды

    loop = asyncio.get_running_loop()
    while not stop_event.is_set():
        tasks_list = parse_tasks()
        if tasks_list:
            logger.info(f"Получены задачи: {tasks_list}")
            if telegram_enabled and bot:
                chat_id = os.getenv('TELEGRAM_CHAT_ID')
                for task in tasks_list:
                    logger.debug(f"Задача: '{task['Задача']}', Фильтр: '{current_filter}'")
                    if current_filter.lower() in task['Задача'].lower():
                        logger.debug(f"Текущий фильтр: '{current_filter}'")
                        message = f"{task['Задача']}\n{task['Ссылка']}"
                        # Отправка сообщения...
                        try:
                            result = await loop.run_in_executor(None, bot.send_message, chat_id, message)
                            logger.info(f"Отправлено сообщение: {result.text}")
                            await asyncio.sleep(5)
                        except Exception as e:
                            logger.exception(f"Ошибка отправки сообщения: {e}")
            if excel_enabled:
                try:
                    import pandas as pd
                    df = pd.DataFrame(tasks_list)
                    df.to_excel('tasks.xlsx', index=False, engine='openpyxl')
                    logger.info("Данные сохранены в tasks.xlsx")
                except Exception as e:
                    logger.exception(f"Ошибка сохранения в Excel: {e}")
        else:
            logger.info("Нет новых задач.")

        # Устанавливаем статус: парсинг окончен и обратный отсчет до следующего запуска
        if status_callback:
            status_callback(f"Парсинг окончен. Следующий запуск через {period_min:.1f} мин.")
        remaining = period_sec
        while remaining > 0 and not stop_event.is_set():
            await asyncio.sleep(1)
            if restart_now_event.is_set():
                restart_now_event.clear()  # сбросим событие, чтобы оно не сработало повторно
                break
            remaining -= 1
            if timer_callback:
                elapsed = int(time.time() - start_time)
                timer_callback(elapsed)
            if status_callback:
                next_run = remaining / 60.0
                status_callback(f"Парсинг окончен. Следующий запуск через {next_run:.1f} мин.")
    logger.info("Бот остановлен.")


def run_bot_async(telegram_enabled, excel_enabled, task_filter, timer_callback, status_callback, stop_event):
    asyncio.run(bot_loop(telegram_enabled, excel_enabled, task_filter, timer_callback, status_callback, stop_event))


def start_bot(telegram_enabled, excel_enabled, task_filter, timer_callback, status_callback):
    """Запускает бота в отдельном потоке, если он не запущен."""
    global bot_thread, stop_event
    if bot_thread is not None and bot_thread.is_alive():
        logger.info("Бот уже запущен.")
    else:
        stop_event = threading.Event()
        bot_thread = threading.Thread(
            target=run_bot_async,
            args=(telegram_enabled, excel_enabled, task_filter, timer_callback, status_callback, stop_event)
        )
        bot_thread.start()


def stop_bot():
    """Останавливает работу бота и сбрасывает переменную bot_thread."""
    global stop_event, bot_thread
    stop_event.set()
    if bot_thread:
        # Используем join с таймаутом, чтобы не блокировать GUI слишком долго
        bot_thread.join(timeout=5)
        if bot_thread.is_alive():
            logger.warning("Бот не остановился полностью после ожидания.")
        else:
            bot_thread = None


def open_telegram():
    """Открывает ссылку на Telegram (например, страницу вашего бота)."""
    webbrowser.open("https://t.me/fl_parser1_bot")


def open_tasks_file():
    """Открывает файл tasks.xlsx с помощью стандартного приложения."""
    try:
        os.startfile("tasks.xlsx")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл tasks.xlsx: {e}")


def open_log_file():
    """Открывает файл app.log с помощью стандартного приложения."""
    try:
        os.startfile("dist/app.log")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл app.log: {e}")


def create_gui():
    config = load_config()

    def enable_shortcuts(widget):
        widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
        widget.bind("<Control-x>", lambda e: widget.event_generate("<<Cut>>"))
        widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))

    root = tk.Tk()
    root.title("FL Parser GUI")
    root.configure(bg=BG_MAIN)
    header = tk.Label(root, text="FL Parser GUI", font=HEADER_FONT, bg=HEADER_BG, fg=HEADER_FG)
    header.pack(pady=10)

    # Добавляем метку статуса бота
    status_label = tk.Label(root, text="Статус бота: остановлен", bg=BG_MAIN, font=LABEL_FONT, fg="red")
    status_label.pack(pady=5)

    config_frame = tk.LabelFrame(root, text="Настройки", bg=BG_FRAME, padx=10, pady=10)
    config_frame.pack(padx=10, pady=10, fill="x")

    tk.Label(config_frame, text="TOKEN:", bg=BG_FRAME).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    token_entry = tk.Entry(config_frame, width=50)
    token_entry.insert(0, config.get('TOKEN', ''))
    token_entry.grid(row=0, column=1, padx=5, pady=5)
    enable_shortcuts(token_entry)
    CreateToolTip(token_entry, "Введите токен вашего Telegram-бота.")

    tk.Label(config_frame, text="TELEGRAM_CHAT_ID:", bg=BG_FRAME).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    chat_entry = tk.Entry(config_frame, width=50)
    chat_entry.insert(0, config.get('TELEGRAM_CHAT_ID', ''))
    chat_entry.grid(row=1, column=1, padx=5, pady=5)
    enable_shortcuts(chat_entry)
    CreateToolTip(chat_entry, "Введите ID чата для отправки сообщений.")

    tk.Label(config_frame, text="Фильтр задачи:", bg=BG_FRAME).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    filter_entry = tk.Entry(config_frame, width=50)
    filter_entry.insert(0, config.get('TASK_FILTER', 'Скрипт'))
    filter_entry.grid(row=2, column=1, padx=5, pady=5)
    enable_shortcuts(filter_entry)
    CreateToolTip(filter_entry, "Введите фильтр для отбора задач (например, 'Скрипт').")

    tk.Label(config_frame, text="RSS URL:", bg=BG_FRAME).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    rss_entry = tk.Entry(config_frame, width=50)
    rss_entry.insert(0, config.get('RSS_URL'))
    rss_entry.grid(row=3, column=1, padx=5, pady=5)
    enable_shortcuts(rss_entry)
    CreateToolTip(rss_entry, "Введите URL RSS-ленты.")

    tk.Label(config_frame, text="Период (мин):", bg=BG_FRAME).grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
    period_entry = tk.Entry(config_frame, width=50)
    period_entry.insert(0, config.get('PERIOD', '1'))
    period_entry.grid(row=4, column=1, padx=5, pady=5)
    enable_shortcuts(period_entry)
    CreateToolTip(period_entry, "Введите интервал обновления в минутах.")

    tk.Label(config_frame, text="Уровень логирования:", bg=BG_FRAME).grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    selected_level = tk.StringVar(value=config.get('LOG_LEVEL', 'INFO'))
    log_level_menu = tk.OptionMenu(config_frame, selected_level, *log_levels)
    log_level_menu.config(width=20)
    log_level_menu.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
    enable_shortcuts(token_entry)
    CreateToolTip(log_level_menu, "Выберите уровень логирования.")

    enable_file_logging = tk.BooleanVar(value=(config.get('ENABLE_FILE_LOGGING', '1') == '1'))
    file_logging_checkbox = tk.Checkbutton(config_frame, text="Логирование в файл", variable=enable_file_logging,
                                           bg=BG_FRAME)
    file_logging_checkbox.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    CreateToolTip(file_logging_checkbox, "Включите для записи логов в файл app.log.")

    enable_telegram = tk.BooleanVar(value=(config.get('ENABLE_TELEGRAM', '1') == '1'))
    enable_excel = tk.BooleanVar(value=(config.get('ENABLE_EXCEL', '1') == '1'))

    telegram_checkbox = tk.Checkbutton(config_frame, text="Отправка сообщений в Telegram", variable=enable_telegram,
                                       bg=BG_FRAME)
    telegram_checkbox.grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    CreateToolTip(telegram_checkbox, "Включите для отправки уведомлений в Telegram.")

    excel_checkbox = tk.Checkbutton(config_frame, text="Сохранение в Excel", variable=enable_excel, bg=BG_FRAME)
    excel_checkbox.grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    CreateToolTip(excel_checkbox, "Включите для сохранения данных в Excel.")

    timer_label = tk.Label(root, text="Время работы: 0 сек", bg=BG_MAIN, font=LABEL_FONT)
    timer_label.pack(pady=5)

    buttons_frame = tk.Frame(root, bg=BG_MAIN)
    buttons_frame.pack(pady=10)

    def ctrl_v(event):
        event.widget.event_generate("<<Paste>>")
        return "break"

    token_entry.bind("<Control-v>", ctrl_v)
    chat_entry.bind("<Control-v>", ctrl_v)
    filter_entry.bind("<Control-v>", ctrl_v)
    rss_entry.bind("<Control-v>", ctrl_v)
    period_entry.bind("<Control-v>", ctrl_v)

    def sanitize_input(value: str) -> str:
        return value.strip().strip("'").strip('"')

    def on_save():
        token_val = sanitize_input(token_entry.get())
        chat_id = sanitize_input(chat_entry.get())
        task_filter_val = sanitize_input(filter_entry.get())
        rss_url = sanitize_input(rss_entry.get())
        period_val = sanitize_input(period_entry.get())
        log_level = selected_level.get()
        file_logging = enable_file_logging.get()
        if not token_val or not chat_id or not rss_url:
            messagebox.showwarning(
                "Недостаточно данных",
                "Поля TOKEN, TELEGRAM_CHAT_ID и RSS URL должны быть заполнены",
            )
            return
        if not period_val.isdigit():
            messagebox.showwarning(
                "Неверный период",
                "Значение периода должно быть числом в минутах",
            )
            return
        save_config(token_val, chat_id, task_filter_val, rss_url, period_val, log_level, file_logging,
                    enable_telegram.get(), enable_excel.get())
        os.environ['TOKEN'] = token_val
        os.environ['TELEGRAM_CHAT_ID'] = chat_id
        os.environ['TASK_FILTER'] = task_filter_val
        os.environ['RSS_URL'] = rss_url
        os.environ['PERIOD'] = period_val
        os.environ['LOG_LEVEL'] = log_level
        os.environ['ENABLE_FILE_LOGGING'] = '1' if file_logging else '0'
        os.environ['ENABLE_TELEGRAM'] = '1' if enable_telegram.get() else '0'
        os.environ['ENABLE_EXCEL'] = '1' if enable_excel.get() else '0'

    save_button = tk.Button(buttons_frame, text="Сохранить настройки", command=on_save, bg=BUTTON_BG_SAVE)
    save_button.grid(row=0, column=0, padx=5)
    CreateToolTip(save_button, "Сохранить все текущие настройки в .env.")

    # Обработчик изменения фильтра
    def on_filter_change(event):
        global current_filter, enable_shortcuts
        current_filter = sanitize_input(filter_entry.get())
        logger.debug(f"Фильтр изменён: '{current_filter}'")

    filter_entry.bind("<KeyRelease>", on_filter_change)
    current_filter = sanitize_input(filter_entry.get())

    def on_update_logging():
        update_logging_config(selected_level.get(), enable_file_logging.get())

    update_logging_button = tk.Button(buttons_frame, text="Обновить логирование", command=on_update_logging,
                                      bg=BUTTON_BG_UPDATE)
    update_logging_button.grid(row=0, column=1, padx=5)
    CreateToolTip(update_logging_button, "Применить выбранный уровень логирования и запись в файл.")

    def on_start():
        task_filter_val = sanitize_input(filter_entry.get())
        # Если бот уже запущен, немедленно прерываем ожидание
        global bot_thread, restart_now_event
        if bot_thread is not None and bot_thread.is_alive():
            restart_now_event.set()
            status_label.config(text="Статус бота: запущен (перезапуск)", fg="green")
        else:
            start_bot(enable_telegram.get(), enable_excel.get(), task_filter_val,
                      lambda elapsed: timer_label.config(text=f"Время работы: {elapsed} сек"),
                      lambda msg: status_label.config(text=f"Статус бота: {msg}",
                                                      fg="green" if "запущен" in msg else "red"))
            status_label.config(text="Статус бота: запущен", fg="green")

    start_button = tk.Button(buttons_frame, text="Запуск бота", command=on_start, bg=BUTTON_BG_START)
    start_button.grid(row=0, column=2, padx=5)
    CreateToolTip(start_button, "Запустить работу бота.")

    # Внутри create_gui() после определения всех виджетов:
    def stop_bot_callback():
        # Этот callback вызывается в главном потоке после остановки бота
        stop_button.config(state=tk.NORMAL)
        status_label.config(text="Статус бота: остановлен", fg="red")
        timer_label.config(text="Время работы: 0 сек")
        logger.info("Бот полностью остановлен.")

    def stop_bot_with_callback():
        global stop_event, bot_thread
        stop_event.set()
        if bot_thread:
            bot_thread.join(timeout=5)
            if bot_thread.is_alive():
                logger.warning("Бот не остановился полностью после ожидания.")
            else:
                bot_thread = None
        # Обновляем GUI в главном потоке:
        root.after(0, stop_bot_callback)

    def on_stop():
        stop_button.config(state=tk.DISABLED)  # Отключаем кнопку сразу после нажатия
        threading.Thread(target=stop_bot_with_callback, daemon=True).start()

    stop_button = tk.Button(buttons_frame, text="Остановить бота", command=on_stop, bg=BUTTON_BG_STOP)
    stop_button.grid(row=0, column=3, padx=5)
    CreateToolTip(stop_button, "Остановить работу бота.")

    extra_frame = tk.Frame(root, bg=BG_MAIN)
    extra_frame.pack(pady=10)

    def on_open_telegram():
        open_telegram()

    telegram_button = tk.Button(extra_frame, text="Перейти в Telegram", command=on_open_telegram, bg="#66d9ef")
    telegram_button.grid(row=0, column=0, padx=5)
    CreateToolTip(telegram_button, "Открыть Telegram (например, чат бота).")

    def on_open_tasks():
        open_tasks_file()

    tasks_button = tk.Button(extra_frame, text="Открыть tasks.xlsx", command=on_open_tasks, bg="#fd971f")
    tasks_button.grid(row=0, column=1, padx=5)
    CreateToolTip(tasks_button, "Открыть файл tasks.xlsx в стандартном приложении.")

    def on_open_log():
        open_log_file()

    log_button = tk.Button(extra_frame, text="Открыть log-файл", command=on_open_log, bg="#f0ad4e")
    log_button.grid(row=0, column=2, padx=5)
    CreateToolTip(log_button, "Открыть файл app.log в стандартном приложении.")

    root.mainloop()


if __name__ == '__main__':
    create_gui()
