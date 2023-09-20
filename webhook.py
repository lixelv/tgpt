from aiogram import Dispatcher, executor

def webhook_pooling(
        dp: Dispatcher = None,
        port: int | str = None,
        link: str = None,
        loop=None
):

    api_token = dp.bot._token

    async def on_shutdown(dp):
        await dp.bot.delete_webhook()

    executor.start_webhook(
        dispatcher=dp,
        loop=loop,
        webhook_path='/' + api_token,
        on_shutdown=on_shutdown,
        host='0.0.0.0',
        port=port
    )
