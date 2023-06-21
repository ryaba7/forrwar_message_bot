import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio

bot_token = "token"
chat_id = "chat_id"
data_file = "file"



polling_interval = 5  # Интервал проверки файла (в секундах)

bot = Bot(token=bot_token)
dp = Dispatcher(bot)


def analyze_text(text):
    # Инициализация значений по умолчанию
    machine = "-"
    duration = "-"
    address = "-"
    contact = "-"

    # Поиск и извлечение информации из текста
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("Спецтехника("):
            machine = line.replace("Спецтехника(", "").replace("):", "").strip()
        elif line.startswith("Число("):
            duration = line.replace("Число(", "").replace("):", "").strip()
        elif line.startswith("Адрес:"):
            address = line.replace("Адрес:", "").strip()
        elif line.startswith("Контакт:"):
            contact = line.replace("Контакт:", "").strip()

    # Формирование результата в формате строки
    result = f"1. Спецтехника: {machine}\n" \
             f"2. Число: {duration}\n" \
             f"3. Адрес: {address}\n" \
             f"4. Контакт: {contact}"

    return result


def read_data_file(filename):
    # Чтение данных из текстового файла
    with open(filename, "r") as file:
        text = file.read()
    return text


async def check_data_file():
    last_data = None
    while True:
        data = read_data_file(data_file)
        if data != last_data:  # Проверка на наличие новых данных
            filled_form = analyze_text(data)
            await bot.send_message(chat_id, filled_form)
            last_data = data
        await asyncio.sleep(polling_interval)


@dp.message_handler()
async def handle_message(message: types.Message):
    # Чтение данных из файла
    data = read_data_file(data_file)

    # Получение текста из сообщения
    text = message.text

    # Анализ текста и заполнение формы
    filled_form = analyze_text(text)

    # Отправка заполненной формы в другой чат
    await bot.send_message(chat_id, filled_form)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(check_data_file())
    executor.start_polling(dp, skip_updates=True)