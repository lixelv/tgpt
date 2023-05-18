import openai

from db_class import *
from asyncio import to_thread
from random import choice
from webhook import webhook_pooling
from aiogram import Bot, Dispatcher, types

OWNER_ID: int = 1689863728
ADMIN_LIST: list = [OWNER_ID]

d = DB('asset.sqlite3')

bot = Bot(token_tg)
Bot.set_current(bot)  # in some cases you might get exception that your current bot instance is not defined so this will solve your problem
dp = Dispatcher(bot)

openai.api_key = token_op

# region Admin
# @dp.message_handler(lambda message: message.from_user.id in ADMIN_ID, commands=['start'])
# async def admin_start(message: types.Message):
# endregion
# region User

@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
    if message.get_command() == 'start':
        await message.answer_sticker(sticker_s['Hi'])
    await bot.send_message(
        message.from_user.id,
        """
Привет я <strong>ChatGPT_3.5</strong>
Я был разработан @simeonlimon, при возникновении проблем обращайтесь

Создайте новый чат с помощью команды <strong>/nc (название бота)</strong>

Выберете чат с помощью команды <strong>/s</strong>

Удалите активный чат с помощью команды <strong>/d</strong>

Чтобы узнать активный чат введите команду <strong>/a</strong>

Чтобы очистить активный чат введите команду <strong>/c</strong>

Чтобы переименовать активный чат введите <strong>/r (новое имя)</strong>

Чтобы использовать ChatGPT 3.5 просто напишите текстовый
запрос боту например 'Расскажи интересный факт о космосе'
        """,
        parse_mode='HTML'
    )
    if not d.user_exists(message):
        d.add_user(message)


@dp.message_handler(commands=['t', 'mt', 'tokens', 'token', 'm_t', 'max_tokens'])
async def max_tokens(message: types.Message):
    d.edit_max_token(message)
    await message.answer(f'max кол-во токенов изменено на {message.get_args()}')


@dp.message_handler(commands=['desc', 'cd', 'chat_description', 'c_d', 'chatdescripion'])
async def bot_description(message: types.Message):
    d.system_message_update(message)
    await message.answer(f'Описание бота было изменено на {message.get_args() if message.get_args() != "" else "You are a smart, helpful, kind, nice, good and very friendly assistant."}')


@dp.message_handler(commands=['a', 'active', 'ac', 'activechat', 'a_c', 'active_chat'])
async def active_chat(message: types.Message):
    active_chat_name = d.active_chat_name(message)
    print(f'{slash}У пользователя {message.from_user.username} активный чат - {active_chat_name}{sla_d}')
    await message.answer(f'Ваш активный чат: {active_chat_name}')


@dp.message_handler(commands=['new_chat', 'n_c', 'nc', 'newchat'])
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
    kb = inlinekeyboard(chat_list_name, chat_list_id)
    await message.answer('Выберите чат:', reply_markup=kb)


@dp.message_handler(commands=['chat_history', 'history', 'c_h', 'ch', 'h'])
async def choose_chat(message: types.Message):
    active_chat_id = d.active_chat_id(message)
    msg = await message.answer('Обработка истории 🔄')
    content = await to_thread(openai.ChatCompletion.create,
                              model="gpt-3.5-turbo",
                              messages=d.message_data(chat_id=active_chat_id, message=message) + [{'role': 'user', 'content': 'What we was talking about? Please answer me on russian language, your answer need to be short'}],
                              max_tokens=None
                              )
    print(f'{slash}Обработка истории 🔄 для {message.from_user.username}, использовано {sla_d}')
    await msg.delete()
    d.token_used(message, content)
    await message.reply(content['choices'][0]['message']['content'])


@dp.message_handler(content_types='text')
async def message(message: types.Message):
    active_chat_id = d.active_chat_id(message)
    d.add_message(active_chat_id, message=message)
    msg = await message.answer('Генерация ответа 🔄')
    print(f'{slash}Генерация ответа 🔄 для {message.from_user.username}{sla_d}')
    content = await to_thread(openai.ChatCompletion.create,
                              model="gpt-3.5-turbo",
                              messages=d.message_data(chat_id=active_chat_id, message=message),
                              max_tokens=d.max_token(message)
                              )
    d.add_message(active_chat_id, content)
    await msg.delete()
    d.token_used(message, content)
    await message.reply(content['choices'][0]['message']['content'])


@dp.message_handler(content_types=["sticker"])
async def send_sticker(message: Message):
    await message.answer_sticker(message.sticker.file_id)
    await message.answer(message.sticker.file_id)
    print(message.content_type)

# endregion
# region Other

@dp.message_handler(
    content_types=[
        'audio',
        'contact',
        'document',
        'game',
        'invoice',
        'location',
        'photo',
        'poll',
        'sticker',
        'text',
        'venue',
        'video',
        'video_note',
        'voice'
    ]
)
async def else_(message: Message):
    print(f'{slash}Ошибка{sla_d}')
    await message.answer(choice(phrases))
    await message.answer_sticker(sticker_s['Error'])
    print(message.content_type)

# endregion
# region Callback

@dp.callback_query_handler(lambda callback_query: int(callback_query.data) in d.chat_list_id(id=callback_query.from_user.id))
async def callback_handler(callback_query: types.CallbackQuery):
    d.change_active_chat(callback_query)
    await callback_query.message.edit_text(f'Выбран чат: {d.chat_name_from_id(callback_query.data)}')

# endregion


if __name__ == "__main__":
    webhook_pooling(dp, token_tg, 8080, ADMIN_LIST)
