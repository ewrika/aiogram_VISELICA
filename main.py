from aiogram import Bot,Dispatcher,executor

import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import *
from middlewares import setup_middlewares
from sql import create_dbx

loop = asyncio.new_event_loop()

bot = Bot(token,parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot,loop=loop,storage=storage)

async def shutdown(dp):
    await storage.close()
    await bot.close()

async def on_startup(dp:Dispatcher):
    print("Bot on")


if __name__ == '__main__':
    print("Bot was started")
    from handlers import *
    create_dbx()
    setup_middlewares(dp)

    executor.start_polling(dp,on_startup=send_hello,on_shutdown=shutdown)

