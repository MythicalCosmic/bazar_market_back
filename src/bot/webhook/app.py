from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request
from core.config import settings
from bot.handlers import register_all_handlers

app = FastAPI()
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

register_all_handlers(dp)


@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://yourdomain.com/webhook"
    await bot.set_webhook(webhook_url)


@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await dp.feed_raw_update(bot=bot, update=update)
    return {"ok": True}


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
