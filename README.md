# Wildberries Price & Review Parser

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.9-green)
![Status](https://img.shields.io/badge/Status-Active-success)

Парсер цен, отзывов WB. Идея: Арбитраж — рубли за отзывы > цена товара (profit hack).

## 🎯 Проблема
Ручной мониторинг 100+ товаров — утомительно. Выявить арбитраж (reviews cashback > cost).

## 🚀 Функции
- Parse: Цены, отзывы, cashback/отзыв.
- Anomaly detect: Фильтр "cashback > price".
- Export: Excel/CSV дашборд.

## 📊 Результаты
- 10k+ товаров parsed.
- Примеры арбитража: +20–50% profit (2025 data).
- Автоматизация: Запуск cron, email alerts.

## 🛠 Стек
- BeautifulSoup/Requests, Pandas.
- Openpyxl (Excel export).

## 📁 Структура
