import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
from transformers import BertTokenizer, BertForTokenClassification

bot_token = ""
chat_id = ""
data_file = ""

# Загрузка предобученной модели BERT
model_name = "bert-base-multilingual-cased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForTokenClassification.from_pretrained(model_name)

bot = Bot(token=bot_token)
dp = Dispatcher(bot)


def analyze_text(file_path):
    # Чтение данных из текстового файла
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()

    # Обработка текста с использованием модели BERT
    encoded_input = tokenizer.encode_plus(data, add_special_tokens=True, return_tensors="pt")
    input_ids = encoded_input["input_ids"]
    attention_mask = encoded_input["attention_mask"]
    outputs = model(input_ids, attention_mask=attention_mask)
    predictions = outputs.logits.argmax(dim=2).squeeze().tolist()

    # Извлечение предсказанных меток и заполнение формы
    labels = tokenizer.convert_ids_to_tokens(predictions)
    machine = labels[1]  # Спецтехника
    duration = labels[2]  # Число
    address = labels[3]  # Адрес
    contact = labels[4]  # Контакт

    # Формирование результата в формате строки
    result = f"1. Спецтехника: {machine}\n" \
             f"2. Число: {duration}\n" \
             f"3. Адрес: {address}\n" \
             f"4. Контакт: {contact}"

    return result


async def check_data_file():
    last_data = None
    while True:
        data = analyze_text(data_file)
        if data != last_data:  # Проверка на наличие новых данных
            await bot.send_message(chat_id, data)
            last_data = data
        await asyncio.sleep(5)  # Интервал проверки файла (в секундах)


@dp.message_handler()
async def handle_message(message: types.Message):
    data = analyze_text(data_file)
    await bot.send_message(chat_id, data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(check_data_file())
    executor.start_polling(dp, skip_updates=True)
