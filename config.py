from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def inlinekeyboard(list_1, list_2) -> object:
    kb = InlineKeyboardMarkup(row_width=1)
    for btn, data in zip(list_1, list_2):
        kb.insert(InlineKeyboardButton(text = btn, callback_data=data))
    return kb