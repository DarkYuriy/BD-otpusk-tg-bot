# main
from database import setup_database, Session
from google_api import fetch_google_sheet_data
from sync import update_vacation_data
from logging_config import logging


def main():
    logging.info("Инициализация базы данных...")
    setup_database()

    logging.info("Запуск синхронизации данных с Google Sheets...")
    fio_dates = fetch_google_sheet_data()

    with Session() as session:
        update_vacation_data(fio_dates, session)

    logging.info("Синхронизация завершена успешно.")


if __name__ == "__main__":
    main()
