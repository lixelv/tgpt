import sqlite3

from aiogram.types import Message, CallbackQuery

from url import *


class DB:

    # region Main ðŸ‘¾
    def __init__(self, database):
        self.connect = sqlite3.connect(database)
        self.cursor = self.connect.cursor()
        self.do("""
    CREATE TABLE IF NOT EXISTS user (
      id         INTEGER  UNIQUE
                          NOT NULL
                          PRIMARY KEY,
      name       TEXT     DEFAULT ('Èìÿ íå çàäàíî'),
      date       DATETIME DEFAULT ( (DATETIME('now') ) ) 
                          NOT NULL,
      token_used INTEGER  DEFAULT (0) 
                          NOT NULL,
      block      INTEGER
    );""")
        self.do("""
    CREATE TABLE IF NOT EXISTS chat (
      id          INTEGER  PRIMARY KEY AUTOINCREMENT
                           UNIQUE
                           NOT NULL,
      user_id     INTEGER  NOT NULL
                           REFERENCES user (id),
      name        TEXT,
      active      INTEGER  NOT NULL
                           DEFAULT (1),
      description TEXT     NOT NULL
                           DEFAULT [You are a helpful assistant.],
      hidden      INTEGER  DEFAULT (0) 
                           NOT NULL,
      date        DATETIME NOT NULL
                           DEFAULT (DATETIME('now') ) 
    );""")
        self.do("""
    CREATE TABLE IF NOT EXISTS message (
      id      INTEGER  PRIMARY KEY
                       NOT NULL
                       UNIQUE,
      chat_id INTEGER  NOT NULL
                       REFERENCES chat (id),
      text    TEXT     NOT NULL,
      role    TEXT     NOT NULL,
      hidden  INTEGER  DEFAULT (0) 
                       NOT NULL,
      date    DATETIME DEFAULT (DATETIME('now') ) 
                     NOT NULL
    );""")

    def do(self, sql, values=()) -> None:
        self.cursor.execute(sql, values)
        self.connect.commit()

    def read(self, sql, values=(), one = False) -> tuple:
        self.cursor.execute(sql, values)
        if one:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()
    # endregion
    # region User ðŸ§‘ðŸ»
    def block_user(self, user_id: int):
        self.do('UPDATE user SET block = 1 WHERE id = ?', (user_id,))

    def is_blocked(self, user_id: int) -> bool:
        return bool(self.read('SELECT block FROM user WHERE id = ?', (user_id,), one = True)[0])

    def user_exists(self, user_id: int) -> bool:
        return bool(self.read('SELECT id FROM user WHERE id = ?', (user_id,)))

    def add_user(self, user_id: int, user_name: str):
        self.do('INSERT INTO user(id, name) VALUES(?,?)', (user_id, user_name))

    # endregion
    # region Chat ðŸ“
    def system_message(self, user_id: int) -> str:
        return self.read('SELECT description FROM chat WHERE active = 1 and user_id = ?', (user_id,), one = True)[0]

    def system_message_update(self, args: str, user_id: int):
        self.do('UPDATE chat SET description = ? WHERE active = 1 and user_id = ?', (args, user_id))

    def edit_chat_name(self, args: str, user_id: int):
        chat_id = self.active_chat_id(user_id)
        self.do('UPDATE chat SET name = ? WHERE user_id = ? and active = 1', (args, user_id))

    def add_chat(self, user_id: int, args="start_chat"):
        if self.chat_list_id(user_id):
            self.do('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (user_id,))
        self.do('INSERT INTO chat(user_id, name) VALUES(?,?)', (user_id, args))


    def chat_list_id(self, user_id: int) -> list:
        result = self.read('SELECT id FROM chat WHERE hidden = 0 and user_id = ?', (user_id,))
        return [row[0] for row in result]

    def chat_list_name(self, user_id: int) -> list:
        result = self.read('SELECT name FROM chat WHERE hidden = 0 and user_id = ?', (user_id,))
        return [row[0] for row in result]

    def start_chat(self, user_id: int):
        if not self.chat_list_id(user_id):
            self.add_chat(user_id)

    def active_chat_id(self, user_id: int) -> int:
        self.start_chat(user_id)
        return self.read('SELECT id FROM chat WHERE active = 1 and user_id = ?', (user_id,), one = True)[0]

    def active_chat_name(self, user_id: int) -> str:
        self.start_chat(user_id)
        return self.read('SELECT name FROM chat WHERE active = 1 and user_id = ?', (user_id,), one = True)[0]

    def chat_name_from_id(self, chat_id: int) -> str:
        result = self.read('SELECT name FROM chat WHERE id = ?', (chat_id,), one = True)
        return result[0] if result is not None else None

    def set_chat_active_after_del(self, user_id: int):
        self.do('UPDATE chat SET active = 1 WHERE id = (SELECT MAX(id) FROM chat WHERE user_id = ? and hidden = 0)', (user_id,))

    def change_active_chat(self, user_id: int, chat_id: int):
        self.do('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (user_id,))
        self.do('UPDATE chat SET active = 1  WHERE id = ?', (chat_id,))

    def del_chat(self, user_id: int):
        self.clear_chat(user_id)
        self.do('UPDATE chat SET hidden = 1, active = 0 WHERE id = (SELECT id FROM chat WHERE user_id = ? and active = 1); ', (user_id,))
        self.set_chat_active_after_del(user_id)

    def clear_chat(self, user_id: int):
        self.do('UPDATE message SET hidden = 1 WHERE chat_id = (SELECT id FROM chat WHERE user_id = ? and active = 1)', (user_id,))

    # endregion
    # region Message ðŸ“¨

    def message_count(self, chat_id: int) -> int:
        return len(self.read('SELECT * FROM message WHERE chat_id = ? and hidden = 0', (chat_id,)))

    def add_message(self, chat_id: int, content: str, role='assistant'):
        self.do('INSERT INTO message(chat_id, text, role) VALUES(?,?,?)', (chat_id, content, role))


    def message_list(self, chat_id: int) -> list:
        return [i[0] for i in self.read('SELECT id FROM message WHERE chat_id = ? and hidden = 0', (chat_id,))]

    def message_data(self, user_id: int) -> list:
        result = [{'role': 'system', 'content': self.system_message(user_id)}]
        data = self.read('SELECT text, role FROM (SELECT id, text, role FROM message WHERE chat_id = (SELECT id FROM chat WHERE user_id = ? and active = 1) and hidden = 0 ORDER BY id DESC LIMIT 4) ORDER BY id;', (user_id,))
        for row in data:
            result.append({'role': row[1], 'content': row[0]})
        return result

    def del_message(self, message_id):
        self.cursor.do('UPDATE message SET hidden = 1 WHERE id = ?', (message_id,))

    def token_used(self, user_id: int, tokens: int) -> int:
        self.do('UPDATE user SET token_used = token_used + ? WHERE id = ?', (tokens, user_id))

    def token(self, user_id: int) -> int:
        return self.read('SELECT token_used FROM user WHERE id = ?', (user_id,), one = True)[0]

    # endregion

    def __del__(self):
        self.connect.close()
