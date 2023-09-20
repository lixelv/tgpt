from aiogram import Dispatcher, executor
import logging

logging.basicConfig(level=logging.INFO)

def webhook_pooling(
        dp: Dispatcher = None,
        port: int | str = None,
        link: str = None,
        loop=None
):

    bot = dp.bot
    api_token = dp.bot._token

    async def on_startup(dp):
        logging.info("Setting up webhook...")
        await bot.set_webhook(f'{link}/{api_token}')
        logging.info("Webhook setup complete.")

    async def on_shutdown(dp):
        logging.info("Deleting webhook...")
        await bot.delete_webhook()
        logging.info("Webhook deleted.")

    executor.start_webhook(
        dispatcher=dp,
        loop=loop,
        webhook_path='/' + api_token,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host='0.0.0.0',
        port=port
    )
