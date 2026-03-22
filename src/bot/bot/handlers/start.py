from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome, <b>{message.from_user.full_name}</b>!\n\n"
        "I am an echo bot. Send me any message and I will repeat it back.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/about - About this bot",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Help</b>\n\n"
        "Just send me any text message and I will echo it back to you.\n"
        "This is a starter template -- customize it to build your bot!"
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        "<b>About</b>\n\n"
        f"Project: <code>bot</code>\n"
        "Built with Boundless + Aiogram 3.x"
    )
