from aiogram import Router
from aiogram.types import Message

router = Router(name="echo")


@router.message()
async def echo_handler(message: Message):
    if message.text:
        await message.answer(message.text)
    else:
        await message.answer("I can only echo text messages.")
