# google_api
import datetime
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import logging
import config


def fetch_google_sheet_data():
    """Получает данные из Google Sheets."""
    logging.info("Загрузка данных из Google Sheets...")

    credentials = Credentials.from_service_account_file(
        config.google_credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=credentials)

    data = {}
    for key, range_name in config.google_sheet_ranges.items():
        result = service.spreadsheets().values().get(
            spreadsheetId=config.google_spreadsheet_id, range=range_name
        ).execute()
        data[key] = result.get('values', [])

    df = pd.DataFrame({
        "FIO": [row[0] if row else None for row in data["fio"]],
        "Start Date": [row[0] if row else None for row in data["start_date"]],
        "End Date": [row[0] if row else None for row in data["end_date"]],
    })

    df = df.dropna(subset=["Start Date", "End Date"], how="all")
    df["FIO"] = df["FIO"].ffill()
    df = df.drop_duplicates(subset=["FIO", "Start Date", "End Date"])

    fio_dates = {}
    for _, row in df.iterrows():
        fio = row["FIO"]
        start_date = datetime.datetime.strptime(row["Start Date"], "%d.%m.%Y").date()
        end_date = datetime.datetime.strptime(row["End Date"], "%d.%m.%Y").date()

        if fio not in fio_dates:
            fio_dates[fio] = []
        fio_dates[fio].append((start_date, end_date))

    logging.info("Данные успешно загружены из Google Sheets.")
    return fio_dates