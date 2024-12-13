# sync
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import ProdEmployeesRegistry, ProdVacation
import logging


def update_vacation_data(fio_dates, session: Session):
    """Обновление данных о сотрудниках и отпусках в базе данных."""
    logging.info("Начало обновления базы данных...")

    try:
        from database import Base, engine
        Base.metadata.create_all(engine)

        existing_users = session.query(ProdEmployeesRegistry).filter_by(is_deleted=False).all()
        db_users = {user.fio: user.id for user in existing_users}

        for fio, dates in fio_dates.items():
            if fio not in db_users:
                new_user = ProdEmployeesRegistry(fio=fio)
                session.add(new_user)
                session.flush()
                db_users[fio] = new_user.id

            user_id = db_users[fio]
            google_periods = set(dates)

            existing_vacations = session.query(ProdVacation).filter_by(user_id=user_id).all()
            existing_vacations_map = {(vac.date_start, vac.date_end): vac for vac in existing_vacations}

            for (date_start, date_end), vacation in existing_vacations_map.items():
                if (date_start, date_end) not in google_periods:
                    vacation.is_deleted = True
                    logging.info(f"Удалён отпуск: {fio}, {date_start} - {date_end}")

            for date_start, date_end in google_periods:
                if (date_start, date_end) in existing_vacations_map:
                    vacation = existing_vacations_map[(date_start, date_end)]
                    if vacation.is_deleted:
                        vacation.is_deleted = False
                        logging.info(f"Восстановлен отпуск: {fio}, {date_start} - {date_end}")
                else:
                    new_vacation = ProdVacation(
                        user_id=user_id,
                        date_start=date_start,
                        date_end=date_end,
                        is_deleted=False
                    )
                    session.add(new_vacation)
                    logging.info(f"Добавлен отпуск: {fio}, {date_start} - {date_end}")

        session.commit()
        logging.info("Обновление базы данных завершено.")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Ошибка при обновлении базы данных: {e}")
        raise