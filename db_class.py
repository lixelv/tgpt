import sqlite3
from aiogram.types import Message, CallbackQuery
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

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

class DB:

    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    # region User 🧑🏻
    def user_exists(self, message: Message):
        result = self.cursor.execute('SELECT `id` FROM user WHERE id = ?', (message.from_user.id,))
        return bool(len(result.fetchall()))

    def add_user(self, message: Message):
        self.cursor.execute('INSERT INTO user(id, name) VALUES(?,?)', (message.from_user.id, message.from_user.username))
        self.connect.commit()
        pprint(f'{slash}`\n`\n`\nПользователь {message.from_user.username} добавлен\n`\n`\n`{sla_d}')

    def max_token(self, message: Message):
        self.cursor.execute('SELECT max_token FROM user WHERE id = ?', (message.from_user.id,))
        return self.cursor.fetchone()[0] if self.cursor.fetchone()[0] != 0 else None

    def edit_max_token(self, message: Message):
        try:
            self.cursor.execute('UPDATE user SET max_token=? WHERE id = ?', (message.get_args() if message.get_args() != '' else None, message.from_user.id))
            self.connect.commit()
            pprint(f'{slash}max_token изменен на {message.get_args()}, {message.from_user.username}{sla_d}')
        except Exception:
            pprint(Exception)

    def system_message(self, message: Message):
        self.cursor.execute('SELECT bot_description FROM user WHERE id = ?', (message.from_user.id,))
        return self.cursor.fetchone()[0]

    def system_message_update(self, message: Message):
        args = message.get_args() if message.get_args() != '' else 'You are a smart, helpful, kind, nice, good and very friendly assistant.'
        self.cursor.execute('UPDATE user SET bot_description = ? WHERE id = ?', (args, message.from_user.id))
        self.connect.commit()
        pprint(f'{slash}Пользователь {message.from_user.username} изменил описание бота на {args}{sla_d}')

    # endregion
    # region Chat 📝

    def edit_chat_name(self, message: Message, chat_id):
        self.cursor.execute('UPDATE chat SET name = ? WHERE id = ?', (message.get_args(), chat_id))
        self.connect.commit()
        pprint(f'{slash}\nЧат {self.chat_name_from_id(chat_id)} переименован в {message.get_args()}, {message.from_user.username}{sla_d}')

    def add_chat(self, message: Message, start_chat=True):
        if self.chat_list_id(message) != []:
            self.cursor.execute('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (message.from_user.id,),)
        if start_chat:
            self.cursor.execute('INSERT INTO chat(user_id, name) VALUES(?,?)', (message.from_user.id, message.get_args()))
            pprint(f'{slash}Создан чат {message.get_args()}, {message.from_user.username}{sla_d}')
        else:
            self.cursor.execute('INSERT INTO chat(user_id, name) VALUES(?,?)', (message.from_user.id, 'start_chat'))
        self.connect.commit()

    def chat_list_id(self, message: Message = None, id = None):
        result = self.cursor.execute('SELECT id FROM chat WHERE user_id = ?', (message.from_user.id,) if id == None else (id,))
        return [row[0] for row in result.fetchall()]

    def chat_list_name(self, message: Message):
        result = self.cursor.execute('SELECT name FROM chat WHERE user_id = ?', (message.from_user.id,))
        return [row[0] for row in result.fetchall()]

    def start_chat(self, message: Message):
        if self.chat_list_id(message) == []:
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

    def add_message(self, chat_id, content = None, role='assistant', message: Message = None):
        if self.message_count(chat_id) >= 4:
            self.cursor.execute('SELECT MIN(id) FROM message WHERE chat_id = ?', (chat_id,))
            to_del_id = self.cursor.fetchone()[0]
            self.cursor.execute('DELETE FROM message WHERE id = (SELECT MIN(id) FROM message WHERE chat_id = ?)', (chat_id,))
            print(f'{slash}Сообщение {to_del_id} было удалено{sla_d}')
        self.cursor.execute('INSERT INTO message(chat_id, text, role) VALUES(?,?,?)', (chat_id, content['choices'][0]['message']['content'], role) if message is None else (chat_id, message.text, 'user'))
        self.connect.commit()
        print(f"\n{slash}\n\nСообщение, содержание:\n```\n{warp(str(content['choices'][0]['message']['content']))}\n``` {role}, used: {content['usage']['total_tokens']}\n{sla_d}\n\n" if message is None else f"\n{slash}\n\nСообщение, содержание:\n```\n{warp(str(message.text))}\n``` user: {message.from_user.username}\n{sla_d}")

    def message_list(self, chat_id):
        result = self.cursor.execute('SELECT id FROM message WHERE chat_id = ?', (chat_id,))
        return [row[0] for row in result]

    def message_data(self, message: Message = None, chat_id = None):
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

    # endregion
    def select(self, sql, tur, many=False):
        self.cursor.execute(sql, tur)
        return self.cursor.fetchone() if many else self.cursor.fetchone()[0]

    def close(self):
        self.connect.close()
