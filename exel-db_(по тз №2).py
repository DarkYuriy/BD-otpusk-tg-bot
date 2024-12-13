import logging
from sqlalchemy.exc import SQLAlchemyError
from database import Session as DBSession
from models import ProdEmployeesRegistry, ProdEmployeeDepartment, Departments
import pandas as pd

EXCEL_FILE_PATH = "departments (1).csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("db_loader.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def load_data_to_database(file_path):
    """Загрузка данных из CSV/Excel файла в базу данных."""
    try:
        data = pd.read_csv(file_path)

        required_columns = {"fio", "department_name", "department_key", "telegram_id"}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Файл должен содержать следующие колонки: {required_columns}")

        with DBSession() as session:
            departments_cache = {}
            for _, row in data.iterrows():
                department_key = row["department_key"]
                department_name = row["department_name"]

                if department_key not in departments_cache:
                    department = session.query(Departments).filter_by(department_key=department_key).first()
                    if not department:
                        department = Departments(
                            department_name=department_name,
                            department_key=department_key
                        )
                        session.add(department)
                        session.flush()
                    departments_cache[department_key] = department.id

            for _, row in data.iterrows():
                fio = row["fio"]
                telegram_id = row["telegram_id"]
                department_key = row["department_key"]

                employee = session.query(ProdEmployeesRegistry).filter_by(fio=fio).first()
                if not employee:
                    employee = ProdEmployeesRegistry(
                        fio=fio,
                        telegram_id=telegram_id,
                        is_deleted=False
                    )
                    session.add(employee)
                    session.flush()

                department_id = departments_cache[department_key]
                employee_department = session.query(ProdEmployeeDepartment).filter_by(
                    user_id=employee.id, department_id=department_id
                ).first()
                if not employee_department:
                    employee_department = ProdEmployeeDepartment(
                        user_id=employee.id,
                        department_id=department_id,
                        is_deleted=False
                    )
                    session.add(employee_department)

            session.commit()
            logger.info("Данные успешно загружены в базу данных.")
    except (SQLAlchemyError, ValueError, FileNotFoundError) as e:
        logger.error(f"Ошибка при загрузке данных в базу: {e}")


if __name__ == "__main__":
    try:
        logger.info("Начало загрузки данных из файла в базу...")
        load_data_to_database(EXCEL_FILE_PATH)
        logger.info("Загрузка завершена.")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")