from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from envparse import env
import openai
# import textwrap
import sys

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
