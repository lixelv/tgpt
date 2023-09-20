from aiogram import Dispatcher, types, executor
from aiohttp import web
from asyncio import get_event_loop

def webhook_pooling(
        dp: Dispatcher = None,
        port: int | str = None,
        link: str = None,
        loop = None
):

    if not port:
        port = 8080

    if not loop:
        loop = get_event_loop()

    bot = dp.bot

    api_token = bot._token

    async def on_startup():
        await bot.set_webhook(f'{link}/{api_token}')

    async def on_shutdown():
        await bot.delete_webhook()

    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/' + api_token,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host='0.0.0.0',
        port=port
    )
