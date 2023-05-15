import openai

from dck import keep_alive
from aiogram import Bot, Dispatcher, executor, types, utils
from config import *
from db_class import DB
from asyncio import to_thread

bot = Bot(token_tg)
dp = Dispatcher(bot)
d = DB('asset.sqlite3')
openai.api_key = token_op


@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
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
    if not d.user_exists(message.from_user.id):
        d.add_user(message.from_user.id, message.from_user.username)
        print('Добавлен пользователь:', message.from_user.username)
        d.add_chat(message.from_user.id, 'start_chat')


@dp.message_handler(commands=['a', 'active', 'ac', 'activechat', 'a_c', 'active_chat'])
async def active_chat(message: types.Message):
    if d.chat_list(message.from_user.id) == []:
        d.add_chat(message.from_user.id, 'start_chat')
        print('Cоздан стандартный чат для ' + message.from_user.username)
    a_c = d.chat_from_id(d.active_chat_id(message.from_user.id))
    print(f'У пользователя {message.from_user.username} активный чат - {a_c}')
    await message.answer(f'Ваш активный чат: {a_c}')


@dp.message_handler(commands=['new_chat', 'n_c', 'nc', 'newchat'])
async def new_chat(message: types.Message):
    args = message.get_args()
    print(f'Создан чат {args} пользователем {message.from_user.username}, его id-{message.from_user.id}')
    d.add_chat(message.from_user.id, args)
    await message.answer(f'Добавлен чат: {args}')
  
@dp.message_handler(commands=['r', 'rc', 'r_c', 'rename_chat', 'renamechat', 'rename'])
async def rename_chat(message: types.Message):
  if d.chat_list(message.from_user.id) == []:
      d.add_chat(message.from_user.id, 'start_chat')
      print('Cоздан стандартный чат для ' + message.from_user.username)
  args = message.get_args()
  active_chat_id = d.active_chat_id(message.from_user.id)
  active_chat = d.chat_from_id(active_chat_id)
  print('Чат '+active_chat+' переиминован в '+args, message.from_user.username)
  d.edit_chat_name(d.active_chat_id(message.from_user.id), args)
  await message.answer('Чат '+active_chat+' переиминован в '+args)


@dp.message_handler(commands=['c', 'clear', 'cc', 'c_c', 'clearchat', 'clear_chat'])
async def clear_chat(message: types.Message):
    if d.chat_list(message.from_user.id) == []:
        d.add_chat(message.from_user.id, 'start_chat')
        print('Cоздан стандартный чат для ' + message.from_user.username)
    active_chat_id = d.active_chat_id(message.from_user.id)
    active_chat = d.chat_from_id(active_chat_id)
    print(f'Чат {active_chat} очищен {message.from_user.username}')
    d.del_message(d.message_list(active_chat_id))
    await message.answer(f'Чат {active_chat} очищен')


@dp.message_handler(commands=['delete_chat', 'del_chat', 'd_c', 'deletechat', 'delchat', 'dc', 'delete', 'del', 'd'])
async def del_chat(message: types.Message):
    try:
        active_chat = d.active_chat_id(message.from_user.id)
        chat_name = d.chat_from_id(active_chat)
        print(f'Чат {chat_name} был удален пользователем {message.from_user.username}')
        await message.answer('Чат ' + chat_name + ' был удален')
        d.del_chat(active_chat)
        d.del_message(d.message_list(active_chat))
        d.set_chat_active(d.last_chat(message.from_user.id))
    except:
        print('Ошибка чат не существует', message.from_user.username)
        await message.answer('Ошибка, чата не существует')


@dp.message_handler(commands=['select_chat', 's_c', 'sc', 'selectchat', 'select', 's'])
async def choose_chat(message: types.Message):
    chat_list = d.chat_list(message.from_user.id)
    chat_name_list = d.chat_from_id(chat_list)
    kb = inlinekeyboard(chat_name_list, chat_list)
    await bot.send_message(message.from_user.id, 'Выберите чат:', reply_markup=kb)


@dp.message_handler(content_types='text')
async def message(message: types.Message):
    if d.chat_list(message.from_user.id) == []:
        d.add_chat(message.from_user.id, 'start_chat')
        print('Cоздан стандартный чат для ' + message.from_user.username)
    print(message.text, message.from_user.username, 'user')
    d.add_message(d.active_chat_id(message.from_user.id), message.text, 'user')
    msg = await message.answer('Генерация ответа 🔄')
    print(f'Генерация ответа 🔄 для {message.from_user.username}')
    content = await to_thread(openai.ChatCompletion.create,
                              model="gpt-3.5-turbo",
                              messages=d.message_data(d.active_chat_id(message.from_user.id))
                              )
    print(content['choices'][0]['message']['content'], message.from_user.username, 'assistant')
    await msg.edit_text(content['choices'][0]['message']['content'])
    d.add_message(d.active_chat_id(message.from_user.id), content['choices'][0]['message']['content'], 'assistant')


@dp.callback_query_handler(lambda callback_query: int(callback_query.data) in d.chat_list(callback_query.from_user.id))
async def callback_handler(callback_query: types.CallbackQuery):
    d.change_active_chat(callback_query.data, callback_query.from_user.id)
    print(f'Выбран чат: {d.chat_from_id(callback_query.data)} Пользователем: {callback_query.from_user.username}')
    await callback_query.message.edit_text(f'Выбран чат: {d.chat_from_id(callback_query.data)}')

keep_alive()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
dp, skip_updates=True)
