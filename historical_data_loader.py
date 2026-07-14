#!/usr/bin/env python3
import argparse
import datetime
import sys
import time
import logging
import requests
import psycopg2
from config import DB_CONFIG, API_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REQUEST_DELAY = 1.0

def get_date_range(start_str, end_str=None):
    start = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else (datetime.date.today() - datetime.timedelta(days=1))
    if start > end:
        raise ValueError("Начальная дата позже конечной")
    dates = []
    cur = start
    while cur <= end:
        dates.append(cur.strftime("%Y-%m-%d"))
        cur += datetime.timedelta(days=1)
    return dates

def fetch_data(date_str):
    try:
        resp = requests.get(API_URL, params={'date': date_str}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'data' in data:
            return data['data']
        else:
            logger.warning(f"Неожиданный формат для {date_str}: {type(data)}")
            return []
    except Exception as e:
        logger.error(f"Ошибка запроса {date_str}: {e}")
        return None

def insert_transactions(conn, date_str, transactions):
    if not transactions:
        return 0
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE date = %s", (date_str,))
    inserted = 0
    for tx in transactions:
        try:
            cur.execute("""
                INSERT INTO transactions (
                    client_id, gender, purchase_datetime,
                    purchase_time_as_seconds_from_midnight,
                    product_id, quantity, price_per_item,
                    discount_per_item, total_price, date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                tx.get('client_id'),
                tx.get('gender'),
                tx.get('purchase_datetime'),
                tx.get('purchase_time_as_seconds_from_midnight'),
                tx.get('product_id'),
                tx.get('quantity'),
                tx.get('price_per_item'),
                tx.get('discount_per_item'),
                tx.get('total_price'),
                date_str
            ))
            inserted += 1
        except Exception as e:
            logger.error(f"Ошибка вставки: {e}, данные: {tx}")
    conn.commit()
    cur.close()
    return inserted

def main():
    parser = argparse.ArgumentParser(description="Загрузка исторических данных")
    parser.add_argument("--start-date", default="2022-01-01", help="Дата начала (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Дата окончания (YYYY-MM-DD), по умолчанию вчера")
    # Для удобства можно оставить возможность переопределить параметры БД через аргументы
    parser.add_argument("--db-host", help="Переопределить хост БД")
    parser.add_argument("--db-port", type=int, help="Переопределить порт")
    parser.add_argument("--db-name", help="Переопределить имя БД")
    parser.add_argument("--db-user", help="Переопределить пользователя")
    parser.add_argument("--db-password", help="Переопределить пароль")
    args = parser.parse_args()

    # Формируем конфиг с учётом возможных переопределений из командной строки
    db_config = DB_CONFIG.copy()
    if args.db_host:
        db_config['host'] = args.db_host
    if args.db_port:
        db_config['port'] = args.db_port
    if args.db_name:
        db_config['dbname'] = args.db_name
    if args.db_user:
        db_config['user'] = args.db_user
    if args.db_password:
        db_config['password'] = args.db_password

    try:
        dates = get_date_range(args.start_date, args.end_date)
    except ValueError as e:
        logger.error(f"Ошибка диапазона: {e}")
        sys.exit(1)

    logger.info(f"Всего дней для загрузки: {len(dates)}")
    if not dates:
        logger.info("Нет дат.")
        return

    conn = psycopg2.connect(**db_config)
    total_loaded = 0
    failed_dates = []

    for i, date_str in enumerate(dates, 1):
        logger.info(f"[{i}/{len(dates)}] Загрузка {date_str}...")
        data = fetch_data(date_str)
        if data is None:
            failed_dates.append(date_str)
            continue
        count = insert_transactions(conn, date_str, data)
        total_loaded += count
        logger.info(f"  Загружено {count} записей")
        if i < len(dates):
            time.sleep(REQUEST_DELAY)

    conn.close()
    logger.info(f"\n=== ИТОГ ===")
    logger.info(f"Всего вставлено записей: {total_loaded}")
    if failed_dates:
        logger.warning(f"Не удалось загрузить даты: {', '.join(failed_dates)}")
    else:
        logger.info("Все даты успешно загружены.")

if __name__ == '__main__':
    main()