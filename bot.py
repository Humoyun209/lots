import asyncio
import logging
from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from database import DataBase
from parsers import FunBay


env = Env()
env.read_env()


bot = Bot(token=env.str("TOKEN"))
dp = Dispatcher()
db = DataBase("db.sqlite3")
fb = FunBay("https://funpay.com/lots/545/", "data/index.html", "data/lots.json")


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s - [%(asctime)s] - %(name)s - %(message)s"
)


@dp.message(Command(commands=["start"]))
async def process_start(message: Message):
    while True:
        fb.get_html_page()
        fb.parse_data_to_json()
        new_lots = db.insert_lots()

        print("Updating...", len(new_lots))
        if new_lots:
            for i, lot in enumerate(new_lots):
                await message.answer(
                    f'\n✅ <b>{"Старый" if lot.is_changed else "Новый"} лот! </b> {"<i>(Цена изменилась)</i>" if lot.is_changed else ""}\n\n{lot.description.replace("<", "").replace(">", "")}\n\n💰 Цена: {lot.price}\n\n👤 Автор: {lot.author}\n\n<b><a href="{lot.url}">❕Перейти по ссылке</a></b>',
                    parse_mode="HTML",
                )

                await asyncio.sleep(1)
        await asyncio.sleep(60)


@dp.message()
async def get_echo(message: Message):
    await message.answer("Бот ничего не понимает")


if __name__ == "__main__":
    dp.run_polling(bot)
