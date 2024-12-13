import logging
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import Session as DBSession
from models import ProdEmployeesRegistry, ProdEmployeeDepartment, ProdVacation, Departments
import datetime

BOT_TOKEN = "7788843936:AAGOCBaiWMxh1u2UhARqvfIKqrzSOjb2_0A"
ALLOWED_CHAT_IDS = [1002491105668]
SPECIAL_CHAT_ID = 7788843936

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def get_employees_by_department(department_key: str, include_on_vacation=False):
    try:
        with DBSession() as session:
            query = session.query(ProdEmployeesRegistry).join(
                ProdEmployeeDepartment,
                ProdEmployeesRegistry.id == ProdEmployeeDepartment.user_id
            ).join(
                Departments, ProdEmployeeDepartment.department_id == Departments.id
            ).filter(
                Departments.department_key == department_key,
                ProdEmployeesRegistry.is_deleted == False
            )

            # Исключаем сотрудников в отпуске, если не указано include_on_vacation
            if not include_on_vacation:
                today = datetime.date.today()
                query = query.outerjoin(
                    ProdVacation,
                    ProdEmployeesRegistry.id == ProdVacation.user_id
                ).filter(
                    ~((ProdVacation.date_start <= today) & (ProdVacation.date_end >= today))
                )

            return query.all()
    except Exception as e:
        logger.error(f"Ошибка получения сотрудников для отдела {department_key}: {e}")
        return []


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        if chat_id not in ALLOWED_CHAT_IDS and update.message.text != '/weather':
            await update.message.reply_text("Команда недоступна в этом чате.")
            logger.warning(f"Попытка вызова команды в неразрешенном чате: {chat_id}")
            return

        command = update.message.text.lower().strip("/")
        include_on_vacation = command.endswith("!")
        if include_on_vacation:
            command = command[:-1]

        department_mapping = {
            "all": None,
            "automation": "automation",
            "comments": "comments",
            "tg": "telegram",
            "incident": "incident",
            "monitoring": "monitoring",
            "bigboss": "bigboss",
            "sms": "sms",
            "print": "print",
            "camera": "camera",
            "moscow": "is_moscow",
            "office": "is_office",
            "weather": "weather_warnings",
        }

        if command not in department_mapping:
            await update.message.reply_text("Неизвестная команда.")
            logger.warning(f"Неизвестная команда: {command}")
            return

        department_key = department_mapping[command]

        employees = []
        if command in ["moscow", "office"]:
            with DBSession() as session:
                filter_field = getattr(ProdEmployeesRegistry, department_key)
                employees = session.query(ProdEmployeesRegistry).filter(
                    filter_field == True,
                    ProdEmployeesRegistry.is_deleted == False
                ).all()
        else:
            employees = get_employees_by_department(department_key, include_on_vacation)

        if not employees:
            await update.message.reply_text("Подходящих сотрудников не найдено.")
            logger.info(f"Команда {command}: подходящих сотрудников не найдено.")
            return

        messages = []
        current_message = []
        for employee in employees:
            mention = f"<a href='tg://user?id={employee.telegram_id}'>{employee.fio}</a>"
            current_message.append(mention)
            if len(current_message) == 5:
                messages.append(", ".join(current_message))
                current_message = []

        if current_message:
            messages.append(", ".join(current_message))

        for message in messages:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
        logger.info(f"Команда {command} выполнена успешно. Отправлено {len(messages)} сообщений.")
    except Exception as e:
        logger.error(f"Ошибка обработки команды: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")


def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler([
            "all", "automation", "comments", "tg",
            "incident", "monitoring", "bigboss", "sms",
            "print", "camera", "moscow", "office", "weather"
        ], command_handler))

        logger.info("Бот запущен и ожидает команды.")
        application.run_polling()
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()