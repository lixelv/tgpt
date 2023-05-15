import sqlite3


class DB:

    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    def edit_chat_name(self, chat_id, new_name):
      self.cursor.execute('UPDATE chat SET name = ? WHERE id = ?', (new_name, chat_id))
      self.connect.commit()

  

    def user_exists(self, user_id):
        result = self.cursor.execute('SELECT `id` FROM user WHERE id = ?', (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id, name):
        self.cursor.execute('INSERT INTO user(id, name) VALUES(?,?)', (user_id, name))
        self.connect.commit()

    def chat_from_id(self, id):
        data = []
        if isinstance(id, list):
            for id_ in id:
                result = self.cursor.execute('SELECT name FROM chat WHERE id = ?', (id_,))
                row = result.fetchone()
                if row[0] != '':
                    data.append(row[0])
                else:
                    data.append('-')
            return data
        else:
            result = self.cursor.execute('SELECT name FROM chat WHERE id = ?', (id,))
            return result.fetchone()[0]

    def add_chat(self, user_id, name):
        self.cursor.execute('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (user_id,))
        self.cursor.execute('INSERT INTO chat(user_id, name) VALUES(?,?)', (user_id, name))
        self.connect.commit()

    def chat_list(self, user_id):
        result = self.cursor.execute('SELECT id FROM chat WHERE user_id = ?', (user_id,))
        return [row[0] for row in result.fetchall()]

    def chat_is_empty(self, chat_id):
        result = self.cursor.execute('SELECT name FROM chat WHERE id = ?', (chat_id,))
        if result.fetchone()[0] is None:
            return True
        else:
            return False

    def active_chat_id(self, user_id):
        data = self.cursor.execute('SELECT id FROM chat WHERE user_id = ? and active = 1', (user_id,))
        return data.fetchone()[0]

    def set_chat_active(self, chat_id):
        self.cursor.execute('UPDATE chat SET active = 1 WHERE id = ?', (chat_id,))
        self.connect.commit()

    def last_chat(self, user_id):
        result = self.cursor.execute('SELECT MAX(id) FROM chat WHERE user_id = ?', (user_id,))
        return result.fetchone()[0]

    def change_active_chat(self, chat_id, user_id):
        self.cursor.execute('UPDATE chat SET active = 0 WHERE active = 1 and user_id = ?', (user_id,))
        self.cursor.execute('UPDATE chat SET active = 1  WHERE user_id = ? and id = ?', (user_id, chat_id))
        self.connect.commit()

    def del_chat(self, chat_id):
        self.cursor.execute('DELETE FROM CHAT WHERE id = ?', (chat_id,))
        self.connect.commit()

    def edit_chat_name(self, chat_id, new_name):
        self.cursor.execute('UPDATE chat SET name = ? WHERE id = ?', (new_name, chat_id))
        self.connect.commit()

    def add_message(self, chat_id, text, role):
        self.cursor.execute('INSERT INTO message(chat_id, text, role) VALUES(?,?,?)', (chat_id, text, role))
        self.connect.commit()

    def message_list(self, chat_id):
        result = self.cursor.execute('SELECT id FROM message WHERE chat_id = ?', (chat_id,))
        return [row[0] for row in result]

    def message_data(self, chat_id):
        data = self.cursor.execute('SELECT text, role FROM message WHERE chat_id = ?', (chat_id,))
        result = [{'role': 'system', 'content': 'You are a smart, helpful, kind, nice, good and very friendly assistant.'}]
        for row in data.fetchall():
            result.append({'role': row[1], 'content': row[0]})
        return result

    def del_message(self, id):
        if isinstance(id, list):
            for id_ in id:
                self.cursor.execute('DELETE FROM message WHERE id = ?', (id_,))
        else:
            self.cursor.execute('DELETE FROM message WHERE id = ?', (id,))
        self.connect.commit()

    def select(self, response, params):
        result = self.cursor.execute(response, params)
        return result.fetchall()

    def close_cursor(self):
        self.cursor.close()

    def close(self):
        self.connect.close()
