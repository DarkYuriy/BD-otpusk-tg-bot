# database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import logging
import config

logger = logging.getLogger(__name__)

engine = create_engine(config.prod_database_url, echo=True)  # echo=True включает логи SQL
Session = sessionmaker(bind=engine)


def setup_database():
    """Инициализирует базу данных, создавая таблицы."""
    try:
        from models import ProdEmployeesRegistry, ProdVacation, Departments, ProdEmployeeDepartment
        Base.metadata.create_all(engine)  # Создает все таблицы
        logger.info("База данных и таблицы успешно инициализированы.")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        raise
