# config
import os

prod_database_url = os.getenv("PROD_DATABASE_URL", "sqlite:///vacation_database.db")

log_file_path = os.getenv("LOG_FILE_PATH", "app.log")

google_credentials_path = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    "prodmodels-6c6e0bfe9633.json"
)
google_spreadsheet_id = os.getenv(
    "GOOGLE_SPREADSHEET_ID",
    "1Itvx1niNN0lTXBHhHtcxydqygO6x9YrngXhWO5LdTg0"
)
google_sheet_ranges = {
    "fio": "B4:B",
    "start_date": "E4:E",
    "end_date": "F4:F"
}

environment = os.getenv("ENVIRONMENT", "development")
debug_mode = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
