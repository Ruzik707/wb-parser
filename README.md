# WB Product Monitoring Parser

Python-скрипт для мониторинга товарных карточек Wildberries, фильтрации предложений по заданным правилам и отправки уведомлений в Telegram.

Проект не является ML-решением. Его цель — показать навыки парсинга, асинхронных запросов, обработки табличных данных и Telegram-автоматизации.

---

## О проекте

Скрипт собирает данные по товарным карточкам Wildberries, извлекает основные параметры товара и фильтрует предложения по правилу:

```text
cashback > price
```

Найденные товары сохраняются в Excel-файл и могут отправляться в Telegram-канал в виде алертов.

---

## Возможности

* асинхронный сбор данных по категориям Wildberries;
* получение цены, кешбэка, рейтинга, количества отзывов и ссылки на товар;
* фильтрация товаров по соотношению кешбэка и цены;
* сохранение найденных товаров в Excel;
* отправка карточек товаров в Telegram-канал;
* защита от повторной отправки уже найденных товаров через `sent_products.txt`.

---

## Стек

* Python
* asyncio
* aiohttp
* Pandas
* tqdm
* Telegram Bot API
* Excel export

---

## Структура проекта

```text
wb-parser/
├── README.md
├── main.py
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## Как запустить

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Ruzik707/wb-parser.git
cd wb-parser
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
```

Для Windows:

```bash
.venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env`

```bash
cp .env.example .env
```

Пример `.env`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
```

### 5. Запустить скрипт

```bash
python main.py
```

После запуска скрипт собирает товары, фильтрует подходящие предложения, сохраняет результат в Excel и отправляет новые находки в Telegram-канал.

---

## Пример выходных данных

Excel-файл содержит поля:

```text
id, name, price, cashback, rating, feedback_count, link
```

---

## Ограничения

* Проект зависит от внутренней структуры Wildberries и может потребовать обновления при изменении API/страниц.
* Telegram-токен и ID канала должны храниться только в `.env`, а не в коде.
* Результаты фильтрации не являются финансовой рекомендацией.
* Проект создан как дополнительный Python automation / data collection проект.

---

## Что можно улучшить

* разделить код на модули `parser.py`, `filters.py`, `telegram_sender.py`;
* добавить нормальное логирование вместо `print`;
* добавить CLI-аргументы для настройки фильтров;
* добавить Dockerfile;
* добавить расписание запуска через cron/APScheduler;
* добавить тесты для функции фильтрации.
