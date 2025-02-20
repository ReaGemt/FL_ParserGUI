# FL Parser GUI

FL Parser GUI – это приложение на Python с графическим интерфейсом (Tkinter), которое выполняет парсинг RSS-ленты с сайта fl.ru для поиска новых заказов и задач. Приложение может:

- Отправлять уведомления о новых задачах в Telegram.
- Сохранять полученные данные в Excel (`tasks.xlsx`).
- Позволять настраивать фильтр для отбора задач в реальном времени.
- Управлять интервалом обновления (в минутах) с обратным отсчетом до следующего запуска.
- Предоставлять гибкую настройку логирования (уровень, запись в файл) через GUI.

## Особенности

### Графический интерфейс:
- Настройки (`TOKEN`, `TELEGRAM_CHAT_ID`, фильтр, RSS URL, период обновления, уровень логирования, включение логирования в файл и функций бота) задаются через удобный GUI.

### Динамический фильтр:
- Возможность изменять фильтр для отбора задач "на лету" без перезапуска бота.

### Статус и таймер:
- Отображение статуса бота (запущен/остановлен) и текущего времени работы.
- После парсинга выводится сообщение с обратным отсчетом до следующего запуска.

### Кнопки для быстрого доступа:
- Возможность открыть Telegram (например, чат бота) и Excel-файл `tasks.xlsx` непосредственно из интерфейса.

### Гибкое логирование:
- Настройка уровня логирования и выбор записи логов в файл.

### Немедленный перезапуск:
- При повторном нажатии кнопки «Запуск бота» бот запускается сразу, прерывая оставшийся период ожидания.

## Установка и запуск

### Клонирование репозитория
```bash
git clone https://github.com/ReaGemt/FL_ParserGUI.git
cd FL_ParserGUI
```

### Создание виртуального окружения и его активация
```bash
python -m venv .venv
# Для Windows:
.venv\Scripts\activate
# Для Unix/macOS:
source .venv/bin/activate
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка `.env` файла
Создайте или отредактируйте файл `.env` в корне проекта. Пример содержимого:
```ini
TOKEN=7513840223:YourBotTokenHere
TELEGRAM_CHAT_ID=421541175
TASK_FILTER=Скрипт
RSS_URL=https://www.fl.ru/rss/all.xml?subcategory=297&category=5
PERIOD=1
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=1
ENABLE_TELEGRAM=1
ENABLE_EXCEL=1
```
> **Важно:** Значения записываются без лишних кавычек.

### Запуск приложения
Запустите файл `main.py`:
```bash
python main.py
```

## Использование

### Настройки:
- В окне настроек укажите токен Telegram-бота, ID чата, фильтр для отбора задач, URL RSS-ленты и интервал обновления (в минутах).
- Также можно выбрать уровень логирования и включить или выключить логирование в файл.

### Управление ботом:
- **Запуск бота**: Нажмите кнопку «Запуск бота» – бот начнёт парсить RSS-ленту и выполнять заданные действия (отправка сообщений, сохранение в Excel).
- **Остановка бота**: Кнопка «Остановить бота» останавливает работу бота с обратным вызовом для обновления статуса.
- **Повторный запуск**: Если бот уже запущен, повторное нажатие кнопки «Запуск бота» прерывает ожидание до следующей итерации, что позволяет мгновенно запустить новый цикл.

### Дополнительные функции:
- Кнопки «Перейти в Telegram» и «Открыть tasks.xlsx» позволяют быстро открыть Telegram (например, чат бота) и Excel-файл с заказами.

## Структура проекта
```
FL_ParserGUI/
├── main.py              # Основной файл приложения
├── parser.py            # Модуль для парсинга RSS-ленты с сайта fl.ru
├── gui_decorations.py   # Модуль для оформления GUI
├── .env                 # Файл с настройками окружения
├── requirements.txt     # Список зависимостей проекта
├── app.log              # Лог-файл (если включено логирование в файл)
└── tasks.xlsx           # Файл с выгруженными заказами
```

## Отладка и логи
- Логи выводятся в консоль и, при включенном файловом логировании, сохраняются в файле `app.log`.
- Уровень логирования можно настроить через GUI.

## Вклад и улучшения
Если у вас есть предложения по улучшению или вы хотите внести изменения, пожалуйста, создайте Pull Request или откройте Issue.

