#!/usr/bin/env python3
import argparse
import datetime
import sys
import logging
import requests
import psycopg2
from config import DB_CONFIG, API_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            logger.warning(f"Неожиданный формат для {date_str}")
            return []
    except Exception as e:
        logger.error(f"Ошибка запроса: {e}")
        return None

def update_day(conn, date_str):
    data = fetch_data(date_str)
    if data is None:
        return False
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE date = %s", (date_str,))
    inserted = 0
    for tx in data:
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
            logger.error(f"Ошибка вставки: {e}")
    conn.commit()
    cur.close()
    logger.info(f"Для {date_str} загружено {inserted} записей")
    return True

def main():
    parser = argparse.ArgumentParser(description="Ежедневное обновление")
    parser.add_argument("--date", help="Дата для загрузки (YYYY-MM-DD), по умолчанию вчера")
    # Переопределение параметров БД
    parser.add_argument("--db-host", help="Переопределить хост БД")
    parser.add_argument("--db-port", type=int, help="Переопределить порт")
    parser.add_argument("--db-name", help="Переопределить имя БД")
    parser.add_argument("--db-user", help="Переопределить пользователя")
    parser.add_argument("--db-password", help="Переопределить пароль")
    args = parser.parse_args()

    if args.date:
        target_date = args.date
    else:
        target_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"Запуск обновления за {target_date}")

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

    conn = psycopg2.connect(**db_config)
    success = update_day(conn, target_date)
    conn.close()
    if success:
        logger.info("Обновление завершено успешно")
    else:
        logger.error("Обновление не удалось")
        sys.exit(1)

if __name__ == '__main__':
    main()