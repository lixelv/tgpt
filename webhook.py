from aiogram import Bot, Dispatcher, types
from aiohttp import web
from os import environ


def webhook_pooling(
        dp: Dispatcher = None, token: str = None, port: int = None,  # these parameters are really important
        admin_list=None,  # in case you didn't write parameter admin_list nothing scary, same with startup and shutdown messages
        startup_message: str = 'Бот ChatGPT 3.5 был запущен! ☠️ ❱ 👾 ❱ 🤖',
        shutdown_message: str = 'Бот ChatGPT 3.5 был выключен. 🤖 ❱ 👾 ❱ ☠️'
):
    if admin_list is None:
        admin_list: list = []
    bot = Bot(token=token)
    Bot.set_current(bot)  # in some cases you might get exception that your current bot instance is not defined so this will solve your problem
    app = web.Application()  # that's our web-server AIOHTTP for handling concurrent requests from ngrok-Telegram API

    webhook_path = f'{environ["LINK"]}/{token}'  # this is the path for your TOKEN_API 'URI'

    async def set_webhook():
        webhook_uri = webhook_path
        await bot.set_webhook(
            webhook_uri  # here we are telling our Telegram API to use the WEBHOOK
        )

    async def on_startup(_):
        await set_webhook()
        if isinstance(admin_list, list) and admin_list is not None:
            for admin_id in admin_list:
                await bot.send_message(chat_id=admin_id, text=startup_message)
        elif isinstance(admin_list, (str, int)):
            await bot.send_message(chat_id=admin_list, text=startup_message)

        else:
            pass

    async def on_shutdown(_):
        if isinstance(admin_list, list) and admin_list != []:
            for admin_id in admin_list:
                await bot.send_message(chat_id=admin_id, text=shutdown_message)
        elif isinstance(admin_list, (str, int)):
            await bot.send_message(chat_id=admin_list, text=shutdown_message)

    async def handle_webhook(request):
        url = str(request.url)
        index = url.rfind('/')
        token_ = url[index + 1:]  # this method is used because in some cases request object can't be correctly interpreted and match_info will return empty object
        if token_ == token:
            update = types.Update(**await request.json())  # we just parse our bytes into dictionary
            await dp.process_update(update)  # this will just process update using the appropriate handler
            return web.Response()  # construct the response object
        else:
            return web.Response(status=403)  # if our TOKEN is not authenticated

    app.router.add_post(f'/{token}', handle_webhook)  # here we set router for process each webhook http request through our handler_

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(
        app,
        host='0.0.0.0',
        port=port
    )
