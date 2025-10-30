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

# 🔹 Расписание приёма БАДов (по Ташкенту)
SCHEDULE = {
    # 🌅 Утро — Железо + Витамин C
    time(9, 0): (
        "🌅 Доброе утро, Машуля!\n\n"
        "🧲 Время принять **Железо (хелат)** и **Витамин C (500–1000 мг)** 💊\n\n"
        "⚠️ Не запивай кофе или чаем в течение 1 часа — они мешают усвоению.\n"
        "💧 Запей водой или соком ❤️"
    ),
    # 🕛 День — Омега-3 и Витамин D3
    time(13, 0): (
        "🕛 Обеденное напоминание 💛\n\n"
        "🐟 Прими **Омега-3 (1 капсула)** и **Витамин D3** 🌞\n\n"
        "Можно с жирной пищей — так D3 усваивается лучше 💧"
    ),
    # 🌙 Вечер — Магний B6, Кальций + D3, Цинк
    time(20, 0): (
        "🌙 Вечерняя забота о себе 💫\n\n"
        "💆 Прими **Магний B6**, **Кальций + D3** и **Цинк пиколинат (1 капсула)** 💊\n\n"
        "⚠️ Не принимай цинк и железо вместе — поэтому цинк вечером 🌸"
    ),
}

# Храним, приняла ли Машуля витамины
taken_today = {}

# 🔘 Кнопка
def get_vitamin_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Приняла", callback_data="taken"))
    return kb


# 📍 Команда /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    if message.from_user.id == GIRLFRIEND_ID:
        await message.answer(
            "Привет, Машуля ☀️\n"
            "Я буду напоминать тебе принимать витаминки и БАДы вовремя 💊❤️"
        )
    elif message.from_user.id == YOUR_ID:
        await message.answer(
            "Бот запущен 💻\n"
            "Я сообщу тебе, если Машуля не нажмёт «Приняла» ❤️"
        )
    else:
        await message.answer("Этот бот создан для личных напоминаний 💊")


# 📍 Нажатие кнопки
@dp.callback_query_handler(lambda c: c.data == "taken")
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)

    key = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    taken_today[key] = True

    await bot.send_message(user_id, "Моя умница, люблю тебя ❤️")
    await bot.delete_message(user_id, callback_query.message.message_id)


# 📍 Отправка напоминаний
async def send_reminders():
    while True:
        now = datetime.now(tz)
        now_time = now.time().replace(second=0, microsecond=0)

        if now_time in SCHEDULE:
            text = SCHEDULE[now_time]
            key = now.strftime("%Y-%m-%d %H:%M")

            if key not in taken_today:
                try:
                    await bot.send_message(GIRLFRIEND_ID, text, reply_markup=get_vitamin_keyboard())
                    logging.info(f"📤 Напоминание отправлено: {text[:40]}...")

                    # ждём 1 час, если не нажала — отправляем тебе
                    await asyncio.sleep(3600)

                    if key not in taken_today:
                        await bot.send_message(
                            YOUR_ID,
                            f"⚠️ Машуля не нажала «Приняла» на напоминании:\n\n{text}"
                        )
                except Exception as e:
                    logging.error(f"Ошибка при отправке: {e}")

        await asyncio.sleep(60)


# 📍 Запуск
async def on_startup(_):
    asyncio.create_task(send_reminders())
    print("🤖 Бот запущен и ждёт время для напоминаний (по Ташкенту)...")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


