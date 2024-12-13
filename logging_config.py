# logging_config
import logging
import config


class SimplifiedSQLAlchemyLogHandler(logging.StreamHandler):
    def emit(self, record):
        translations = {
            "BEGIN (implicit)": "Начало транзакции (неявно)",
            "COMMIT": "Фиксация изменений",
            "ROLLBACK": "Откат транзакции",
            "SELECT": "Выборка данных",
            "INSERT INTO": "Добавление данных",
            "UPDATE": "Обновление данных",
            "DELETE FROM": "Удаление данных",
        }

        for english, russian in translations.items():
            if english in record.msg:
                record.msg = record.msg.replace(english, russian)

        if "[raw sql]" in record.msg or "[generated in" in record.msg:
            return

        record.msg = f"[SQLAlchemy] {record.msg}"
        super().emit(record)


log_format = "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s"
logging.basicConfig(
    level=logging.DEBUG if config.debug_mode else logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.log_file_path, encoding="utf-8"),
    ],
)

sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.addHandler(SimplifiedSQLAlchemyLogHandler())