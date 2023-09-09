from db import DB
from url import *
from parse_weather import get_weather
from aiogram import types, executor
#  from webhook import webhook_pooling
from random import choice
import asyncio
import openai

d = DB(db_config)


# region Admin
@dp.message_handler(commands=['b', 'block'])
async def set_block(message: types.Message):
    if message.from_user.id == int(my_id):
        d.block_user(message.from_user.id)
        await message.answer(f'Пользователь с id {message.get_args()} заблокирован')
    else:
        await message.answer('Ты не админ!')
# endregion
# region User

@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
    if message.get_command() == '/start':
        await message.answer_sticker(sticker_s['Hi'])
    await bot.send_message(message.from_user.id, hello if message.get_command() == '/start' else help_, parse_mode='HTML')
    if not d.user_exists(message.from_user.id):
        d.add_user(message.from_user.id, message.from_user.username)

@dp.message_handler(lambda message: not d.user_exists(message.from_user.id))
async def user_exists(message: types.Message):
    await message.answer('Напишите команду /start')

@dp.message_handler(lambda message: d.is_blocked(message.from_user.id))
async def love(message: types.Message):
    await message.answer('Вы заблокированы!')


@dp.message_handler(commands=['new_chat', 'n_c', 'nc', 'newchat', 'new', 'n'])
async def new_chat(message: types.Message):
    args = message.get_args()
    d.add_chat(message.from_user.id, args=args)
    await message.answer(f'Создан новый чат {args}')


@dp.message_handler(commands=['r', 'rc', 'r_c', 'rename_chat', 'renamechat', 'rename'])
async def rename_chat(message: types.Message):
    args = message.get_args()
    d.edit_chat_name(args, message.from_user.id)
    await message.answer(f'Имя активного чата изменено на: {args}')


@dp.message_handler(commands=['a', 'active', 'ac', 'activechat', 'a_c', 'active_chat'])
async def active_chat(message: types.Message):
    await message.answer(f'Активный чат: <strong>{d.active_chat_name(message.from_user.id)}</strong>, \n'
        f'Описание чата: <strong>{d.system_message(message.from_user.id)}</strong>', parse_mode='HTML')


@dp.message_handler(commands=['chat_history', 'history', 'c_h', 'ch', 'h'])
async def chat_history(message: types.Message):
    asyncio.create_task(handle_chat_history(message))


@dp.message_handler(commands=['select_chat', 's_c', 'sc', 'selectchat', 'select', 's'])
async def choose_chat(message: types.Message):
    chat_list_id = d.chat_list_id(message.from_user.id)
    chat_list_name = d.chat_list_name(message.from_user.id)
    kb = inline(chat_list_name, chat_list_id)
    await message.answer('Выберите чат:', reply_markup=kb)


@dp.message_handler(commands=['delete_chat', 'del_chat', 'd_c', 'deletechat', 'delchat', 'dc', 'delete', 'del', 'd'])
async def del_chat(message: types.Message):
    active_chat_name = d.active_chat_name(message.from_user.id)
    d.del_chat(message.from_user.id)
    await message.answer(f'Чат {active_chat_name} был удален')


@dp.message_handler(commands=['c', 'clear', 'cc', 'c_c', 'clearchat', 'clear_chat'])
async def clear_chat(message: types.Message):
    active_chat_name = d.active_chat_name(message.from_user.id)
    d.clear_chat(message.from_user.id)
    await message.answer(f'Чат {active_chat_name} очищен')


@dp.message_handler(commands=['description', 'cd', 'chat_description', 'c_d', 'chatdescripion', 'desc'])
async def bot_description(message: types.Message):
    args = message.get_args()
    args = args if args != '' else 'You are a smart, helpful, kind, nice, good and very friendly assistant.'
    sys_m = d.system_message(message.from_user.id)
    d.system_message_update(args, message.from_user.id)
    await message.answer(f'Описание бота было изменено на <strong>{args}</strong>, \nПрошлое описание: <strong>{sys_m}</strong>', parse_mode="HTML")


@dp.message_handler(commands=['t', 'token', 'tok'])
async def token(message: types.Message):
    tokens = d.token(message.from_user.id)
    await message.answer(f'Вы использовали {tokens} токенов, что эквивалентно {tokens*0.000002}$')


async def handle_chat_history(message: types.Message):
    msg = await message.answer('Генерация ответа 🔄', disable_notification=True)

    content = await get_chat_history(message)
    d.token_used(message.from_user.id, content['usage']['total_tokens'])
    await msg.delete()
    await message.reply(content['choices'][0]['message']['content'], parse_mode='Markdown')


async def get_chat_history(message: types.Message):
    global op
    try:
        content = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo",
                                                          messages=d.message_data(message.from_user.id) + histor,
                                                          api_key=choice(op))
        return content

    except:
        content = await get_chat_history(message)
        return content


@dp.message_handler(content_types=['text'])
async def message(message: types.Message):
    asyncio.create_task(handle_message(message))


async def handle_message(message: types.Message):
    active_chat_id = d.active_chat_id(message.from_user.id)
    d.add_message(active_chat_id, message.text, role='user')
    msg = await message.answer('Генерация ответа 🔄', disable_notification=True)

    content = await get_message(message)
    d.add_message(active_chat_id, content['choices'][0]['message']['content'])
    d.token_used(message.from_user.id, content['usage']['total_tokens'])
    await msg.delete()
    await message.reply(content['choices'][0]['message']['content'], parse_mode='Markdown')


async def get_message(message: types.Message):
    global op
    try:
        content = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo",
                                                          messages=d.message_data(message.from_user.id),
                                                          api_key=choice(op))
        return content

    except:
        content = await get_message(message)
        return content


@dp.message_handler(content_types=["sticker"])
async def send_sticker(message: types.Message):
    await message.answer_sticker(message.sticker.file_id)
    await message.answer(message.sticker.file_id)
    print(message.content_type)


@dp.message_handler(content_types=["location"])
async def weather(message: types.Message):
    await message.answer(get_weather(message.location.latitude, message.location.longitude))


# endregion
# region Other

@dp.message_handler(content_types=['audio', 'contact', 'document', 'game', 'invoice', 'photo', 'poll', 'sticker', 'venue', 'video', 'video_note', 'voice'])
async def else_(message: types.Message):
    await message.answer_sticker(sticker_s['Error'])
    await message.answer(choice(phrases))
    print(message.content_type)


# endregion
# region Callback

@dp.callback_query_handler(lambda callback_query: int(callback_query.data) in d.chat_list_id(callback_query.from_user.id))
async def callback_handler(callback_query: types.CallbackQuery):
    d.change_active_chat(callback_query.from_user.id, callback_query.data)
    await callback_query.message.edit_text(f'Выбран чат: <strong>{d.chat_name_from_id(callback_query.data)}</strong>, \n'
        f'Описание чата: <strong>{d.system_message(callback_query.from_user.id)}</strong>',
                                           parse_mode='HTML')


# endregion


if __name__ == "__main__":
    #  webhook_pooling(dp, port, link, [my_id])
    executor.start_polling(dp, skip_updates=True)
