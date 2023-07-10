from aiogram import Dispatcher, types
from aiohttp import web

def webhook_pooling(
        dp: Dispatcher = None,
        port: int | str = None,
        link: str = None,
        admin_list: list | int | str = None,
        startup_message: str = 'Бот был запущен! ☠️ ❱ 👾 ❱ 🤖',
        shutdown_message: str = 'Бот был выключен. 🤖 ❱ 👾 ❱ ☠️'
):
    # Create a bot instance with the provided token
    bot = dp.bot
    token = bot._token

    # Create an aiohttp web application
    app = web.Application()

    # Construct the webhook path using the provided link and token
    webhook_path = f'{link}/{token}'
    print(webhook_path)

    # Add a POST route to handle incoming webhooks
    app.router.add_post(f'/{token}', lambda request: handle_webhook(request, token, dp))

    # Register the on_startup and on_shutdown handlers
    app.on_startup.append(lambda _: on_startup(dp, startup_message, admin_list, webhook_path))
    app.on_shutdown.append(lambda _: on_shutdown(dp, shutdown_message, admin_list))

    # Run the web application
    web.run_app(
        app,
        host='0.0.0.0',
        port=port
    )


async def handle_webhook(request, token, dp):
    # Extract the token from the URL
    url = str(request.url)
    index = url.rfind('/')
    token_ = url[index + 1:]

    # Verify if the extracted token matches the provided token
    if token_ == token:
        # Process the incoming update using the Dispatcher
        update = types.Update(**await request.json())
        await dp.process_update(update)

        # Return a success response
        return web.Response()
    else:
        # Return a forbidden response if the tokens do not match
        return web.Response(status=403)


async def start_shutdown(bot, text: str = None, admin_list: tuple | set | list | str | int = None):
    # Check if the text and admin_list parameters are provided
    if text is not None and admin_list is not None:
        # Check the type of admin_list and send a message accordingly
        if isinstance(admin_list, (tuple, set, list)):
            for admin_id in admin_list:
                await bot.send_message(chat_id=admin_id, text=text)
        elif isinstance(admin_list, (str, int)):
            await bot.send_message(chat_id=admin_list, text=text)


async def on_startup(dp, startup_message, admin_list, webhook_path):
    # Set the webhook path for the bot
    await dp.bot.set_webhook(webhook_path)

    # Send the startup message to the specified admin_list
    await start_shutdown(dp.bot, startup_message, admin_list)


async def on_shutdown(dp, shutdown_message, admin_list):
    # Send the shutdown message to the specified admin_list
    await start_shutdown(dp.bot, shutdown_message, admin_list)
