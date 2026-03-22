import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from core.config import settings
from bot.handlers import register_all_handlers


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    register_all_handlers(dp)

    logging.info("Bot starting in polling mode...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
