import aiomysql
import asyncio


class DB:
    def __init__(self, loop, host='localhost', port=3306, user='user', password='password', db='dbname'):
        self.loop = loop
        self.loop.create_task(self.initialize(host, port, user, password, db))

    async def initialize(self, host, port, user, password, db):
        self.pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            loop=self.loop
        )
        self.loop.create_task(self.keep_alive())

    async def keep_alive(self):
        while True:
            await self.read('SELECT 1;')
            await asyncio.sleep(14400)

    async def do(self, sql, values=()):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, values)
                await conn.commit()

    async def read(self, sql, values=(), one=False):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, values)
                if one:
                    return await cur.fetchone()
                else:
                    return await cur.fetchall()


    # endregion
    # region User
    async def block_user(self, user_id: int):
        await self.do('UPDATE user SET block = 1 WHERE id = %s', (user_id,))

    async def is_blocked(self, user_id: int) -> bool:
        result = await self.read('SELECT block FROM user WHERE id = %s', (user_id,), one = True)
        return bool(result[0])

    async def user_exists(self, user_id: int) -> bool:
        return bool(await self.read('SELECT id FROM user WHERE id = %s', (user_id,)))

    async def add_user(self, user_id: int, user_name: str):
        await self.do('INSERT INTO user(id, name) VALUES(%s,%s)', (user_id, user_name))

    # endregion
    # region Chat
    async def system_message(self, user_id: int) -> str:
        result = await self.read('SELECT description FROM chat WHERE active = 1 and user_id = %s', (user_id,), one = True)
        return result[0]

    async def system_message_update(self, args: str, user_id: int):
        await self.do('UPDATE chat SET description = %s WHERE active = 1 and user_id = %s', (args, user_id))

    async def edit_chat_name(self, args: str, user_id: int):
        await self.do('UPDATE chat SET name = %s WHERE user_id = %s and active = 1', (args, user_id))

    async def add_chat(self, user_id: int, args="start_chat"):
        if await self.chat_list_id(user_id):
            await self.do('UPDATE chat SET active = 0 WHERE active = 1 and user_id = %s', (user_id,))
        await self.do('INSERT INTO chat(user_id, name) VALUES(%s,%s)', (user_id, args))


    async def chat_list_id(self, user_id: int) -> list:
        result = await self.read('SELECT id FROM chat WHERE user_id = %s', (user_id,))
        return [row[0] for row in result]

    async def chat_list_name(self, user_id: int) -> list:
        result = await self.read('SELECT name FROM chat WHERE user_id = %s', (user_id,))
        return [row[0] for row in result]

    async def start_chat(self, user_id: int):
        if not await self.chat_list_id(user_id):
            await self.add_chat(user_id)

    async def active_chat_id(self, user_id: int) -> int:
        await self.start_chat(user_id)
        result = await self.read('SELECT id FROM chat WHERE active = 1 and user_id = %s', (user_id,), one = True)
        return result[0]

    async def active_chat_name(self, user_id: int) -> str:
        await self.start_chat(user_id)
        result = await self.read('SELECT name FROM chat WHERE active = 1 and user_id = %s', (user_id,), one = True)
        return result[0]

    async def chat_name_from_id(self, chat_id: int) -> str:
        result = await self.read('SELECT name FROM chat WHERE id = %s', (chat_id,), one = True)
        return result[0] if result is not None else None

    async def set_chat_active_after_del(self, user_id: int):
        await self.do('UPDATE chat SET active = 1 WHERE id = (SELECT MAX(id) FROM chat WHERE user_id = %s)', (user_id,))

    async def change_active_chat(self, user_id: int, chat_id: int):
        await self.do('UPDATE chat SET active = 0 WHERE active = 1 and user_id = %s', (user_id,))
        await self.do('UPDATE chat SET active = 1  WHERE id = %s', (chat_id,))

    async def del_chat(self, user_id: int):
        await self.clear_chat(user_id)
        await self.do('UPDATE chat SET hidden = 1 WHERE user_id = %s and active = 1; ', (user_id,))
        await self.set_chat_active_after_del(user_id)

    async def clear_chat(self, user_id: int):
        chat_id = await self.active_chat_id(user_id)
        await self.do('UPDATE message WHERE id = &s;', (chat_id,))

    # endregion
    # region Message

    async def default_system_message(self) -> str:
        result = await self.do('SELECT description FROM chat WHERE id = 119')

    async def message_count(self, chat_id: int) -> int:
        return len(await self.read('SELECT * FROM message WHERE chat_id = %s', (chat_id,)))

    async def add_message(self, user_id: int, content: str, role='assistant'):
        await self.start_chat(user_id)
        await self.do('INSERT INTO message(chat_id, text, role) VALUES((SELECT id FROM chat WHERE user_id = %s AND active = 1),%s,%s)', (user_id, content, role))


    async def message_list(self, chat_id: int) -> list:
        return [i[0] for i in await self.read('SELECT id FROM message WHERE chat_id = %s', (chat_id,))]

    async def message_data(self, user_id: int) -> list:
        system_message = await self.system_message(user_id)

        result = [{'role': 'system', 'content': system_message}]

        limit = await self.read('SELECT `limit` FROM user WHERE id = %s', (user_id,), one = True)
        limit = limit[0]

        data = await self.read("""SELECT text, role FROM (SELECT id, text, role FROM message WHERE chat_id = (SELECT id FROM chat WHERE user_id = %s and active = 1) and hidden = 0
                         ORDER BY id DESC LIMIT %s) AS alias_table ORDER BY id;""", (user_id, limit))

        for row in data:
            result.append({'role': row[1], 'content': row[0]})
        return result

    async def del_message(self, message_id):
        await self.do('UPDATE message SET hidden = 1 WHERE id = %s', (message_id,))

    async def token_used(self, user_id: int, tokens: int) -> int:
        await self.do('UPDATE user SET token_used = token_used + %s WHERE id = %s', (tokens, user_id))

    async def token(self, user_id: int) -> int:
        result = await self.read('SELECT token_used FROM user WHERE id = %s', (user_id,), one = True)
        return result[0]

    # endregion
