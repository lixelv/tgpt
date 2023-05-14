from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

token_op = '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'
token_tg = '5993940494:AAGY389dHNMIM1MrcwkBzTMJWkeDXtjIMV8'

def inlinekeyboard(list_1, list_2) -> object:
    kb = InlineKeyboardMarkup(row_width=1)
    for btn, data in zip(list_1, list_2):
        kb.insert(InlineKeyboardButton(text = btn, callback_data=data))
    return kb