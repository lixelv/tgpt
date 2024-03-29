parse_weather.py:
```py
import requests
from url import weather
import datetime


def get_weather(lat: float, lon: float):
    try:
        r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=RU&appid={weather}')
        data = r.json()
        return f'Погода: {data["weather"][0]["description"]}\n' \
               f'Сейчас температура: {data["main"]["temp"]}C°\n' \
               f'Скорость ветра: {data["wind"]["speed"]} м/с\n' \
               f'Влажность: {data["main"]["humidity"]}%\n' \
               f'Давление: {data["main"]["pressure"]} мм\n' \
               f'Восход: {datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S")}\n' \
               f'Закат: {datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")}'
    except Exception as err:
        return f'Ошибка: {err}'

```
url.py:
```py
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from envparse import env
from asyncio import get_event_loop
import random
# import textwrap

hello = """
Привет я <strong>ChatGPT_3.5</strong> был разработан @simeonlimon
при возникновении проблем обращайся к нему

Чтобы узнать о командах напишите <strong>/help</strong>
        """

help_ = """
Создайте новый чат командой <strong>/new (название чата)
Варианты: /n /nc /n_c /new /newchat /new_chat </strong>

Переименуйте активный чат командой <strong>/rename (новое имя)
Варианты: /r /rc /r_c /rename /renamechat /rename_chat </strong>

Узнайте название активного чата командой <strong>/active
Варианты: /a /ac /a_c /activechat /active_chat </strong> 

Узнайте историю чата командой <strong>/history
Варианты: /h /ch /c_h /history /chat_history </strong>

Выберете чат с помощью команды <strong>/select
Варианты: /s /sc /s_c /select /selectchat /select_chat </strong>

Удалите активный чат с командой <strong>/delete
Варианты: /d /dc /d_c /del /delete /delchat /del_chat /deletechat /delete_chat </strong>

Чтобы очистить чат введите команду <strong>/clear
Варианты: /c /cc /c_c /clear /clearchat /clear_chat </strong>

Чтобы изменить описание бота напишите <strong>/description (описание бота)
Варианты: /cd /c_d /desc /description /chatdescripion /chat_description </strong>

Узнайте количество потраченных токенов введя <strong>/token
Варианты: /t /tok /token </strong>



Чтобы использовать ChatGPT 3.5 просто напишите текстовый
запрос боту например '<strong>Расскажи интересный факт о космосе</strong>'
        """

histor = [{'role': 'user', 'content': 'What we was talking about? Please answer me on russian language, your answer need to be short'}]

sticker_s = {
    'Hi': 'CAACAgIAAxkBAAIGsmRk5s_MYBOcUS6ItUTHXF417syzAAJxKwACQo3ASjypfvfFuI3SLwQ',
    'Loading': 'CAACAgIAAxkBAAIGuGRk5tAuE9s_TyADgQvd2rJioqIVAAItMAAC-cm5SlL0u9sCgWBtLwQ',
    'Error': 'CAACAgIAAxkBAAIGu2Rk55a7GlI9CY4yHDerKIpwwhWSAAKsKgAClR64SlmLYAGBoLH7LwQ'
}

phrases = [
    "Ничего себе! Я не ожидал такого!",
    "Удивительно, что такое произошло.",
    "Вот это поворот! Я не знал, что это возможно.",
    "Произошла ошибка... Я должен узнать, что произошло.",
    "Я ошеломлен! Я никогда не встречал такую ошибку.",
    "Йой! Я не знал, что это может произойти.",
    "Вот это сюрприз! Я не ожидал таких проблем.",
    "Как же так? Я не могу понять, в чем проблема.",
    "Невероятно! Я должен изучить этот случай детальнее.",
    "О-о-очень необычно! Я никогда не знал, что это возможно."
]

slash = '░░░░▒▒▒▒▒▒▓▓▓▓▓▓▓▓████████████████████████████████████████████████████▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░░\n'

sla_d = ''

loop = get_event_loop()

env.read_envfile('.env')
db_config = {
    "host": env('HOST_'),
    "user": env('USER_'),
    "password": env('PASSWORD_'),
    "database": env('DB_')
}
op = env('OPENAI').split(',')
n = random.randint(0, len(op))
op = [n, tuple(op)]
token = env('TELEGRAM')
my_id = env('MYID')
port = env('PORT')
link = env('LINK')
weather = env('WEATHER')
bot = Bot(token)
Bot.set_current(bot)
dp = Dispatcher(bot)


def inline(list_keys: list, list_data: list,
           width: int = 2):
    kb: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=width)
    buttons: list = []
    for key, data in zip(list_keys, list_data):
        buttons.append(InlineKeyboardButton(key, callback_data=data))
    kb.add(*buttons)
    return kb


# def pprint(str):
#     str_ = textwrap.wrap(str, width=len(slash))
#     for line in str_:
#         print(line)
#
#
# def warp(text):
#     wrapped_text = textwrap.wrap(text, width=len(slash) - 2)
#     result = ''
#     for i in wrapped_text:
#         result += i + '\n'
#     return result[:-2]

```
webhook.py:
```py
from aiogram import Dispatcher, types
from aiohttp import web
from asyncio import ProactorEventLoop, get_event_loop

def webhook_pooling(
        dp: Dispatcher = None,
        port: int | str = None,
        link: str = None,
        admin_list: list | int | str = None,
        loop=None,
        startup_message: str = 'Бот был запущен! ☠️ ❱ 👾 ❱ 🤖',
        shutdown_message: str = 'Бот был выключен. 🤖 ❱ 👾 ❱ ☠️'
):

    if not port:
        port = 8080

    if not loop:
        loop = get_event_loop()


    # Create a bot instance with the provided token
    token = dp.bot._token

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
        port=port,
        loop=loop
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

```
