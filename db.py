import pymysql


class DB:

    # region Main
    def __init__(self, db_config):
        self.connect = pymysql.connect(**db_config)
        self.cursor = self.connect.cursor()
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
    # region User
    def block_user(self, user_id: int):
        self.do('UPDATE user SET block = 1 WHERE id = %s', (user_id,))

    def is_blocked(self, user_id: int) -> bool:
        return bool(self.read('SELECT block FROM user WHERE id = %s', (user_id,), one = True)[0])

    def user_exists(self, user_id: int) -> bool:
        return bool(self.read('SELECT id FROM user WHERE id = %s', (user_id,)))

    def add_user(self, user_id: int, user_name: str):
        self.do('INSERT INTO user(id, name) VALUES(%s,%s)', (user_id, user_name))

    # endregion
    # region Chat
    def system_message(self, user_id: int) -> str:
        return self.read('SELECT description FROM chat WHERE active = 1 and user_id = %s', (user_id,), one = True)[0]

    def system_message_update(self, args: str, user_id: int):
        self.do('UPDATE chat SET description = %s WHERE active = 1 and user_id = %s', (args, user_id))

    def edit_chat_name(self, args: str, user_id: int):
        self.do('UPDATE chat SET name = %s WHERE user_id = %s and active = 1', (args, user_id))

    def add_chat(self, user_id: int, args="start_chat"):
        if self.chat_list_id(user_id):
            self.do('UPDATE chat SET active = 0 WHERE active = 1 and user_id = %s', (user_id,))
        self.do('INSERT INTO chat(user_id, name) VALUES(%s,%s)', (user_id, args))


    def chat_list_id(self, user_id: int) -> list:
        result = self.read('SELECT id FROM chat WHERE user_id = %s', (user_id,))
        return [row[0] for row in result]

    def chat_list_name(self, user_id: int) -> list:
        result = self.read('SELECT name FROM chat WHERE user_id = %s', (user_id,))
        return [row[0] for row in result]

    def start_chat(self, user_id: int):
        if not self.chat_list_id(user_id):
            self.add_chat(user_id)

    def active_chat_id(self, user_id: int) -> int:
        self.start_chat(user_id)
        return self.read('SELECT id FROM chat WHERE active = 1 and user_id = %s', (user_id,), one = True)[0]

    def active_chat_name(self, user_id: int) -> str:
        self.start_chat(user_id)
        return self.read('SELECT name FROM chat WHERE active = 1 and user_id = %s', (user_id,), one = True)[0]

    def chat_name_from_id(self, chat_id: int) -> str:
        result = self.read('SELECT name FROM chat WHERE id = %s', (chat_id,), one = True)
        return result[0] if result is not None else None

    def set_chat_active_after_del(self, user_id: int):
        self.do('UPDATE chat SET active = 1 WHERE id = (SELECT MAX(id) FROM chat WHERE user_id = %s)', (user_id,))

    def change_active_chat(self, user_id: int, chat_id: int):
        self.do('UPDATE chat SET active = 0 WHERE active = 1 and user_id = %s', (user_id,))
        self.do('UPDATE chat SET active = 1  WHERE id = %s', (chat_id,))

    def del_chat(self, user_id: int):
        self.clear_chat(user_id)
        self.do('DELETE FROM chat WHERE id = (SELECT id FROM chat WHERE user_id = %s and active = 1); ', (user_id,))
        self.set_chat_active_after_del(user_id)

    def clear_chat(self, user_id: int):
        self.do('DELETE FROM message WHERE chat_id = (SELECT id FROM chat WHERE user_id = %s and active = 1)', (user_id,))

    # endregion
    # region Message

    def message_count(self, chat_id: int) -> int:
        return len(self.read('SELECT * FROM message WHERE chat_id = %s', (chat_id,)))

    def add_message(self, chat_id: int, content: str, role='assistant'):
        self.do('INSERT INTO message(chat_id, text, role) VALUES(%s,%s,%s)', (chat_id, content, role))


    def message_list(self, chat_id: int) -> list:
        return [i[0] for i in self.read('SELECT id FROM message WHERE chat_id = %s', (chat_id,))]

    def message_data(self, user_id: int) -> list:
        result = [{'role': 'system', 'content': self.system_message(user_id)}]
        data = self.read('SELECT text, role FROM (SELECT id, text, role FROM message WHERE chat_id = (SELECT id FROM chat WHERE user_id = %s and active = 1) ORDER BY id DESC LIMIT 4) AS alias_table ORDER BY id;', (user_id,))
        for row in data:
            result.append({'role': row[1], 'content': row[0]})
        return result

    def del_message(self, message_id):
        self.cursor.do('UPDATE message SET hidden = 1 WHERE id = %s', (message_id,))

    def token_used(self, user_id: int, tokens: int) -> int:
        self.do('UPDATE user SET token_used = token_used + %s WHERE id = %s', (tokens, user_id))

    def token(self, user_id: int) -> int:
        return self.read('SELECT token_used FROM user WHERE id = %s', (user_id,), one = True)[0]

    # endregion

    def __del__(self):
        if hasattr(self, 'connect') and self.connect.is_connected():
            self.cursor.close()
            self.connect.close()
            