import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime, time, timedelta
import pytz
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
# 🔹 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
# 🔹 ID пользователей
GIRLFRIEND_ID = 1380413600  # 👩‍🦰 Машуля
YOUR_ID = 397100539          # 👦 Твой ID

# 🔹 Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 🔹 Часовой пояс Ташкента
tz = pytz.timezone("Asia/Tashkent")

# 🔹 Расписание приёма витаминов
SCHEDULE = {
    time(9, 0): "🌞 Утро!\nПора принять D3 + Омега-3 + Цинк + Витамин C 💊",
    time(13, 0): "🍽 Время принять Кальций + D3 💊",
    time(16, 0): "🩸 Не забудь про Железо 💊",
    time(20, 0): "🌙 Перед сном — Магний + В6 💊",
}

# Храним состояние: приняла ли Машуля витамины в конкретное время
taken_today = {}

# 📍 Кнопка
def get_vitamin_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="✅ Приняла", callback_data="taken"))
    return keyboard


# 📍 Команда /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    if message.from_user.id == GIRLFRIEND_ID:
        await message.answer("Привет, Машуля ☀️\nЯ буду напоминать тебе принимать витаминки вовремя 💊❤️")
    elif message.from_user.id == YOUR_ID:
        await message.answer("Бот запущен! 💻 Я буду сообщать тебе, если Машуля не примет витамины.")
    else:
        await message.answer("Этот бот создан для личных напоминаний 💊")


# 📍 Обработка кнопки
@dp.callback_query_handler(lambda c: c.data == "taken")
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)

    # Отметим, что Машуля приняла витамины
    taken_today[datetime.now(tz).strftime("%Y-%m-%d %H:%M")] = True

    await bot.send_message(user_id, "Моя умница, люблю тебя ❤️")
    await bot.delete_message(user_id, callback_query.message.message_id)


# 📍 Функция напоминаний
async def send_reminders():
    while True:
        now = datetime.now(tz)
        now_time = now.time().replace(second=0, microsecond=0)

        if now_time in SCHEDULE:
            text = SCHEDULE[now_time]
            date_key = now.strftime("%Y-%m-%d %H:%M")

            if date_key not in taken_today:  # Чтобы не дублировать напоминание
                try:
                    await bot.send_message(GIRLFRIEND_ID, text, reply_markup=get_vitamin_keyboard())
                    logging.info(f"Отправлено напоминание: {text}")

                    # Ждём 1 час и проверяем, нажала ли она "Приняла"
                    await asyncio.sleep(3600)

                    if date_key not in taken_today:
                        await bot.send_message(
                            YOUR_ID,
                            f"⚠️ Машуля не нажала 'Приняла' на напоминании:\n\n{text}"
                        )
                except Exception as e:
                    logging.error(f"Ошибка при отправке: {e}")

        await asyncio.sleep(60)


# 📍 Запуск
async def on_startup(_):
    asyncio.create_task(send_reminders())
    print("Бот запущен и ждёт время для напоминаний (по Ташкенту)...")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

