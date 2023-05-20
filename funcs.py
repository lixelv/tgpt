import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
# token_op = os.environ['OPENAI']
# token_tg = os.environ['TELEGRAM']
token_op = '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'
token_tg = '5993940494:AAGY389dHNMIM1MrcwkBzTMJWkeDXtjIMV8'

def inlinekeyboard(list_1, list_2) -> object:
    kb = InlineKeyboardMarkup(row_width=1)
    for btn, data in zip(list_1, list_2):
        kb.insert(InlineKeyboardButton(text = btn, callback_data=data))
    return kb

def pprint(str):
    str_ = textwrap.wrap(str, width=len(slash))
    for line in str_:
        print(line)

def warp(text):
    wrapped_text = textwrap.wrap(text, width=len(slash)-2)
    result = ''
    for i in wrapped_text:
        result += i + '\n'
    return result[:-2]