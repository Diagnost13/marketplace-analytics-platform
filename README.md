# Marketplace Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![Metabase](https://img.shields.io/badge/Metabase-0.50-509EE3.svg)](https://www.metabase.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

## 📖 Описание проекта

Платформа для автоматического сбора, хранения и анализа данных о транзакциях маркетплейса.  
Проект решает задачи:
- Ежедневного обновления данных из внешнего API (`http://final-project.simulative.ru/data`) в 10:00 утра.
- Хранения исторических данных в PostgreSQL с оптимизированной структурой и индексами.
- Визуализации ключевых метрик в **Metabase** (дашборды с динамикой продаж, топ-клиентами, ABC-XYZ и RFM-анализом).
- Углублённого анализа в **Jupyter Notebook** для выработки рекомендаций по оптимизации ассортимента и увеличению LTV клиентов.

---

## 🧰 Технологический стек

| Компонент | Инструмент |
|-----------|------------|
| **Язык** | Python 3.12 |
| **База данных** | PostgreSQL 15 |
| **ETL** | Python (requests, psycopg2) |
| **BI‑визуализация** | Metabase (Docker) |
| **Аналитика** | Jupyter Notebook (pandas, numpy, matplotlib, seaborn, scikit‑learn) |
| **Оркестрация** | Docker Compose (Metabase) + Планировщик задач Windows / cron |
| **Виртуальное окружение** | venv |

---

## 📁 Структура репозитория
marketplace-analytics-platform/
├── src/
│ ├── config.py # Параметры подключения к БД
│ ├── init_db.py # Создание таблицы transactions и индексов
│ ├── load_historical.py # Единоразовая загрузка исторических данных
│ ├── daily_update.py # Ежедневное обновление за предыдущий день
│ └── run.bat # Запуск daily_update.py с активацией venv (Windows)
├── notebooks/
│ └── analysis_2023.ipynb # Jupyter‑ноутбук с ABC‑XYZ, RFM, рекомендациями
├── metabase/
│ └── docker-compose.yml # Docker Compose для Metabase + PostgreSQL
├── logs/ # Логи выполнения (создаётся автоматически)
├── .gitignore
├── README.md
└── LICENSE

---
## 📓 Аналитика в Jupyter Notebook
Откройте notebooks/analysis_2023.ipynb и выполните ячейки.
Ноутбук включает:

ABC‑XYZ анализ – оптимизация ассортимента.

RFM‑сегментацию – работа с клиентской базой и увеличение LTV.

Анализ по дням недели и часам – планирование акций.

Конкретные рекомендации по выводу товаров, стимулированию продаж и повышению маржинальности.
## 📊 Дашборды в Metabase
После запуска Metabase дашборд доступен по адресу: 
**[http://localhost:3000/dashboard/1-executive-dashboard](http://localhost:3000/dashboard/1-executive-dashboard)**
На дашборде отображаются:
- **Динамика выручки** (последние 30 дней)
- **Топ-10 товаров по выручке и количеству**
- **Топ-10 клиентов по выручке**
- **Активность по дням недели** (столбцы)
