from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.echo import router as echo_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(echo_router)
