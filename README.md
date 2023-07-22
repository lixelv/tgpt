db.py:
```python
import sqlite3
from aiogram.types import Message, CallbackQuery
from url import *

class DB:

    def __init__(self, database):
        self.connect = sqlite3.connect(database)
        self.cursor = self.connect.cursor()
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id      INTEGER  PRIMARY KEY AUTOINCREMENT
                     UNIQUE
                     NOT NULL,
    user_id INTEGER  NOT NULL,
    name    TEXT,
    active  INTEGER  NOT NULL
                     DEFAULT (1),
    date    DATETIME NOT NULL
                     DEFAULT (DATETIME('now') ) 
);""")
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS message (
    id      INTEGER  PRIMARY KEY
                     NOT NULL
                     UNIQUE,
    chat_id INTEGER  NOT NULL,
    text    TEXT     NOT NULL,
    role    TEXT     NOT NULL,
    date    DATETIME DEFAULT (DATETIME('now') ) 
                     NOT NULL
);""")
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id              INTEGER  UNIQUE
                             NOT NULL
                             PRIMARY KEY,
    name            TEXT     DEFAULT ('Имя не задано'),
    date            DATETIME DEFAULT ( (DATETIME('now') ) ) 
                             NOT NULL,
    bot_description TEXT     NOT NULL
                             DEFAULT ('You are a helpful assistant.'),
    token_used      INTEGER  DEFAULT (0) 
                             NOT NULL,
    block           INTEGER
);""")
        self.connect.commit()

    # region User 🧑🏻
    def user_exists(self, message: Message):
        result = self.cursor.execute('SELECT `id` FROM user WHERE id = ?', (message.from_user.id,))
        return bool(result.fetchall())

    def add_user(self, message: Message):
        self.cursor.execute('INSERT INTO user(id, name) VALUES(?,?)', (message.from_user.id, message.from_user.username))
        self.connect.commit()
        pprint(f'{slash}`\n`\n`\nПользователь {message.from_user.username} добавлен\n`\n`\n`{sla_d}')

    def system_message(self, message: Message):
        self.cursor.execute('SELECT bot_description FROM user WHERE id = ?', (message.from_user.id,))
        return self.cursor.fetchone()[0]

    def system_message_update(self, message: Message):
        args = message.get_args() if message.get_args() != '' else 'You are a smart, helpful, kind, nice, good and very friendly assistant.'
        self.cursor.execute('UPDATE user SET bot_description = ? WHERE id = ?', (args, message.from_user.id))
        self.connect.commit()
        pprint(f'{slash}Пользователь {message.from_user.username} изменил описание бота на {args}{sla_d}')
        
    def block_user(self, message: Message):
        self.cursor.execute('UPDATE user SET block = 1 WHERE id = ?', (message.get_args(),))
        self.connect.commit()
        pprint(f'{slash}Пользователь {message.from_user.username} заблокирован{sla_d}')

    def is_blocked(self, message: Message):
        self.cursor.execute('SELECT block FROM user WHERE id = ?', (message.from_user.id,))
        return bool(self.cursor.fetchone()[0])

    # endregion
    # region Chat 📝

    def edit_chat_name(self, message: Message, chat_id):
        self.cursor.execute('UPDATE chat SET name = ? WHERE id = ?', (message.get_args(), chat_id))
        self.connect.commit()
        pprint(f'{slash}\nЧат {self.chat_name_from_id(chat_id)} переименован в {message.get_args()}, {message.from_user.username}{sla_d}')

    def add_chat(self, message: Message, start_chat=True):
        if self.chat_list_id(message):
            self.cursor.execute('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (message.from_user.id,),)
        if start_chat:
            self.cursor.execute('INSERT INTO chat(user_id, name) VALUES(?,?)', (message.from_user.id, message.get_args()))
            pprint(f'{slash}Создан чат {message.get_args()}, {message.from_user.username}{sla_d}')
        else:
            self.cursor.execute('INSERT INTO chat(user_id, name) VALUES(?,?)', (message.from_user.id, 'start_chat'))
        self.connect.commit()

    def chat_list_id(self, message: Message = None, id=None):
        result = self.cursor.execute('SELECT id FROM chat WHERE user_id = ?', (message.from_user.id,) if id is None else (id,))
        return [row[0] for row in result.fetchall()]

    def chat_list_name(self, message: Message):
        result = self.cursor.execute('SELECT name FROM chat WHERE user_id = ?', (message.from_user.id,))
        return [row[0] for row in result.fetchall()]

    def start_chat(self, message: Message):
        if not self.chat_list_id(message):
            self.add_chat(message, False)
            pprint(f'{slash}Cоздан стандартный чат для {message.from_user.username}{sla_d}')

    def active_chat_id(self, message: Message):
        self.start_chat(message)
        data = self.cursor.execute('SELECT id FROM chat WHERE user_id = ? and active = 1', (message.from_user.id,))
        return data.fetchone()[0]

    def active_chat_name(self, message: Message):
        self.start_chat(message)
        data = self.cursor.execute('SELECT name FROM chat WHERE user_id = ? and active = 1', (message.from_user.id,))
        return data.fetchone()[0]

    def chat_name_from_id(self, id):
        result = self.cursor.execute('SELECT name FROM chat WHERE id = ?', (id,))
        return result.fetchone()[0] if result is not None else None

    def set_chat_active_after_del(self, message: Message):
        self.cursor.execute('SELECT MAX(id) FROM chat WHERE user_id = ?', (message.from_user.id,))
        chat_id = self.cursor.fetchone()[0]
        self.cursor.execute('UPDATE chat SET active = 1 WHERE id = ?', (chat_id,))
        self.connect.commit()

    def change_active_chat(self, callback_query: CallbackQuery):
        self.cursor.execute('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (callback_query.from_user.id,))
        self.cursor.execute('UPDATE chat SET active = 1  WHERE id = ?', (callback_query.data,))
        self.connect.commit()
        pprint(f'{slash}Выбран чат: {self.chat_name_from_id(callback_query.data)}, {callback_query.from_user.username}{sla_d}')

    def del_chat(self, chat_id):
        self.cursor.execute('DELETE FROM CHAT WHERE id = ?', (chat_id,))
        self.connect.commit()

    def clear_chat(self, chat_id):
        self.cursor.execute('DELETE FROM message WHERE chat_id = ?', (chat_id,))
        self.connect.commit()
    # endregion
    # region Message 📨

    def message_count(self, chat_id):
        self.cursor.execute('SELECT * FROM message WHERE chat_id = ?', (chat_id,))
        return len(self.cursor.fetchall())

    def add_message(self, chat_id, content=None, role='assistant', message: Message = None):
        if self.message_count(chat_id) >= 4:
            self.cursor.execute('SELECT MIN(id) FROM message WHERE chat_id = ?', (chat_id,))
            to_del_id = self.cursor.fetchone()[0]
            self.cursor.execute('DELETE FROM message WHERE id = (SELECT MIN(id) FROM message WHERE chat_id = ?)', (chat_id,))
            print(f'{slash}Сообщение {to_del_id} было удалено{sla_d}')
        self.cursor.execute('INSERT INTO message(chat_id, text, role) VALUES(?,?,?)', (chat_id, content['choices'][0]['message']['content'], role) if message is None else (chat_id, message.text, 'user'))
        self.connect.commit()
        print(f"{slash}Сообщение, содержание:\n```\n{warp(str(content['choices'][0]['message']['content']))}\n``` {role}, used: {content['usage']['total_tokens']}{sla_d}" if message is None else f"{slash}Сообщение, содержание:\n```\n{warp(str(message.text))}\n``` user: {message.from_user.username}{sla_d}")

    def message_list(self, chat_id):
        result = self.cursor.execute('SELECT id FROM message WHERE chat_id = ?', (chat_id,))
        return [row[0] for row in result]

    def message_data(self, message: Message = None, chat_id=None):
        result = [{'role': 'system', 'content': self.system_message(message)}]
        data = self.cursor.execute('SELECT text, role FROM message WHERE chat_id = ?', (chat_id,))
        for row in data.fetchall():
            result.append({'role': row[1], 'content': row[0]})
        return result

    def del_message(self, id):
        self.cursor.execute('DELETE FROM message WHERE id = ?', (id,))
        self.connect.commit()
        pprint(f'{slash}Сообщение с id: {id} было удалено{sla_d}')

    def token_used(self, message: Message, content):
        self.cursor.execute('UPDATE user SET token_used = token_used + ? WHERE id = ?', (content['usage']['total_tokens'], message.from_user.id))
        self.connect.commit()

    def token(self, message: Message):
        self.cursor.execute('SELECT token_used FROM user WHERE id = ?', (message.from_user.id,))
        return self.cursor.fetchone()[0]

    # endregion
    def select(self, sql, tur, many=False):
        self.cursor.execute(sql, tur)
        return self.cursor.fetchone() if many else self.cursor.fetchone()[0]

    def close(self):
        self.connect.close()

```
main.py:
```python
from db import *
from parse_weather import get_weather
from aiogram import types, exceptions, executor
from webhook import webhook_pooling
from random import choice
from functools import partial
import asyncio
import openai

d = DB('gpt.sqlite3')

# region Admin
# @dp.message_handler(lambda message: message.from_user.id in ADMIN_ID, commands=['start'])
# async def admin_start(message: types.Message):
# endregion
# region User

@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
    if message.get_command() == '/start':
        await message.answer_sticker(sticker_s['Hi'])
    await bot.send_message(
        message.from_user.id,
        hello if message.get_command() == '/start' else help_,
        parse_mode='HTML'
    )
    if not d.user_exists(message):
        d.add_user(message)

@dp.message_handler(lambda message: d.is_blocked(message))
async def love(message: types.Message):
    await message.answer('Вы заблокированы!')

@dp.message_handler(commands=['b', 'block'])
async def set_block(message: types.Message):
    if message.from_user.id == int(my_id):
        d.block_user(message)
        await message.answer(f'Пользователь с id {message.get_args()} заблокирован')
    else:
        await message.answer('Ты не админ!')

@dp.message_handler(commands=['t', 'token', 'tok'])
async def token(message: types.Message):
    await message.answer(f'Вы использовали {d.token(message)} токенов')


@dp.message_handler(commands=['description', 'cd', 'chat_description', 'c_d', 'chatdescripion'])
async def bot_description(message: types.Message):
    d.system_message_update(message)
    await message.answer(f'Описание бота было изменено на {message.get_args() if message.get_args() != "" else "You are a smart, helpful, kind, nice, good and very friendly assistant."}')


@dp.message_handler(commands=['a', 'active', 'ac', 'activechat', 'a_c', 'active_chat'])
async def active_chat(message: types.Message):
    active_chat_name = d.active_chat_name(message)
    print(f'{slash}У пользователя {message.from_user.username} активный чат - {active_chat_name}{sla_d}')
    await message.answer(f'Ваш активный чат: {active_chat_name}')


@dp.message_handler(commands=['new_chat', 'n_c', 'nc', 'newchat', 'new', 'n'])
async def new_chat(message: types.Message):
    args = message.get_args()
    d.add_chat(message)
    await message.answer(f'Создан чат: {args}')


@dp.message_handler(commands=['r', 'rc', 'r_c', 'rename_chat', 'renamechat', 'rename'])
async def rename_chat(message: types.Message):
    args = message.get_args()
    active_chat_id = d.active_chat_id(message)
    active_chat_name = d.active_chat_name(message)
    d.edit_chat_name(message, active_chat_id)
    await message.answer(f'Чат {active_chat_name} переименован в {args}')


@dp.message_handler(commands=['c', 'clear', 'cc', 'c_c', 'clearchat', 'clear_chat'])
async def clear_chat(message: types.Message):
    active_chat_id = d.active_chat_id(message)
    active_chat_name = d.active_chat_name(message)
    print(f'{slash}Чат {active_chat_name} очищен, {message.from_user.username}{sla_d}')
    d.clear_chat(active_chat_id)
    await message.answer(f'Чат {active_chat_name} очищен')


@dp.message_handler(commands=['delete_chat', 'del_chat', 'd_c', 'deletechat', 'delchat', 'dc', 'delete', 'del', 'd'])
async def del_chat(message: types.Message):
    active_chat_id = d.active_chat_id(message)
    active_chat_name = d.active_chat_name(message)
    d.clear_chat(active_chat_id)
    d.del_chat(active_chat_id)
    d.set_chat_active_after_del(message)
    print(f'{slash}Чат {active_chat_name} был удален пользователем {message.from_user.username}{sla_d}')
    await message.answer(f'Чат {active_chat_name} был удален')


@dp.message_handler(commands=['select_chat', 's_c', 'sc', 'selectchat', 'select', 's'])
async def choose_chat(message: types.Message):
    chat_list_id = d.chat_list_id(message)
    chat_list_name = d.chat_list_name(message)
    kb = inline(chat_list_name, chat_list_id)
    await message.answer('Выберите чат:', reply_markup=kb)


@dp.message_handler(commands=['chat_history', 'history', 'c_h', 'ch', 'h'])
async def chat_history(message: types.Message):
    asyncio.create_task(handle_chat_history(message))

async def handle_chat_history(message: types.Message):
    global op
    active_chat_id = d.active_chat_id(message, active_chat_id)
    d.add_message(active_chat_id, message=message)
    msg = await message.answer('Генерация ответа 🔄', disable_notification=True)
    print(f'{slash}Генерация ответа 🔄 для {message.from_user.username}{sla_d}')

    content = await get_chat_history(message)
    d.add_message(active_chat_id, content)
    d.token_used(message, content)
    await msg.delete()
    await message.reply(content['choices'][0]['message']['content'], parse_mode='Markdown')

async def get_chat_history(message: types.Message, active_chat_id):
    global op
    try:
        content = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=d.message_data(chat_id=active_chat_id, message=message) + [{'role': 'user', 'content': 'What we was talking about? Please answer me on russian language, your answer need to be short'}],
            api_key=op[0])
        op = onetoto(op)
        return content
    except:
        content = await get_chat_history(message, active_chat_id)
        return content

@dp.message_handler(content_types=['text'])
async def message(message: types.Message):
    asyncio.create_task(handle_message(message))

async def handle_message(message: types.Message):
    global op
    active_chat_id = d.active_chat_id(message)
    d.add_message(active_chat_id, message=message)
    msg = await message.answer('Генерация ответа 🔄', disable_notification=True)
    print(f'{slash}Генерация ответа 🔄 для {message.from_user.username}{sla_d}')

    content = await get_message(message, active_chat_id)
    d.add_message(active_chat_id, content)
    d.token_used(message, content)
    await msg.delete()
    await message.reply(content['choices'][0]['message']['content'], parse_mode='Markdown')

async def get_message(message: types.Message, active_chat_id):
    global op
    try:
        content = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=d.message_data(chat_id=active_chat_id, message=message),
            api_key=op[0])
        op = onetoto(op)
        return content
    except:
        content = await get_message(message, active_chat_id)
        return content


@dp.message_handler(content_types=["sticker"])
async def send_sticker(message: Message):
    await message.answer_sticker(message.sticker.file_id)
    await message.answer(message.sticker.file_id)
    print(message.content_type)

@dp.message_handler(content_types=["location"])
async def weather(message: Message):
    await message.answer(get_weather(message.location.latitude, message.location.longitude))

# endregion
# region Other

@dp.message_handler(
    content_types=[
        'audio',
        'contact',
        'document',
        'game',
        'invoice',
        'photo',
        'poll',
        'sticker',
        'venue',
        'video',
        'video_note',
        'voice'
    ]
)
async def else_(message: Message):
    await message.answer_sticker(sticker_s['Error'])
    await message.answer(choice(phrases))
    print(message.content_type)

# endregion
# region Callback

@dp.callback_query_handler(lambda callback_query: int(callback_query.data) in d.chat_list_id(id=callback_query.from_user.id))
async def callback_handler(callback_query: types.CallbackQuery):
    d.change_active_chat(callback_query)
    await callback_query.message.edit_text(f'Выбран чат: {d.chat_name_from_id(callback_query.data)}')

# endregion


if __name__ == "__main__":
    #  webhook_pooling(dp, port, link, [my_id])
    executor.start_polling(dp, skip_updates=True)
    

```
parse_weather.py:
```python
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
```python
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from envparse import env
import openai
import textwrap
import sys

hello = """
Привет я <strong>ChatGPT_3.5</strong> был разработан @simeonlimon
при возникновении проблем обращайся к нему

Чтобы узнать о командах напишите <strong>/help</strong>
        """

help = """
Создайте новый чат командой <strong>/new_chat (название чата)</strong>
Переименуйте активный чат командой <strong>/rename (новое имя)</strong>
Узнайте название активного чата командой <strong>/active</strong>
Выберете чат с помощью команды <strong>/select</strong>
Удалите активный чат с командой <strong>/delete</strong>
Чтобы очистить чат введите команду <strong>/clear</strong>
Узнайте количество потраченных токенов введя <strong>/token</strong>
Чтобы изменить описание бота напишите <strong>/description (описание бота)</strong> 

Чтобы использовать ChatGPT 3.5 просто напишите текстовый
запрос боту например '<strong>Расскажи интересный факт о космосе</strong>'
        """

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


env.read_envfile('.env')
op = env('OPENAI').split(',')
token = env('TELEGRAM')
my_id = env('MYID')
port = env('PORT')
link = env('LINK')
weather = env('WEATHER')
bot = Bot(token)
Bot.set_current(bot)
dp = Dispatcher(bot)

with open('output.txt', 'w') as f:
    sys.stdout = f
sys.stdout = sys.__stdout__

def create_chat_completion(api_key, messages):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        api_key=api_key
    )


def inline(list_keys: list, list_data: list,
           width: int = 2):
    kb: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=width)
    buttons: list = []
    for key, data in zip(list_keys, list_data):
        buttons.append(InlineKeyboardButton(key, callback_data=data))
    kb.add(*buttons)
    return kb


def onetoto(lis: list):
    lis.append(lis[0])
    lis.remove(lis[0])
    return lis


def pprint(str):
    str_ = textwrap.wrap(str, width=len(slash))
    for line in str_:
        print(line)


def warp(text):
    wrapped_text = textwrap.wrap(text, width=len(slash) - 2)
    result = ''
    for i in wrapped_text:
        result += i + '\n'
    return result[:-2]

```
webhook.py:
```python
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

```
