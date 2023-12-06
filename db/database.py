import asyncio
import sys
from datetime import datetime

import pymysql
import aiomysql
from aiomysql import create_pool

from db.config import HOST, PORT, USER, PASSWORD, DB_NAME


class DataBase:
    def __init__(self):
        self._conn = None

    @property
    def conn(self):
        return self._conn

    @conn.setter
    def conn(self, value):
        self._conn = value

    async def add_user(self, name, email, password):
        query = f"INSERT INTO `user` (`name`, `email`, `password`) VALUES (%(name)s, %(email)s, %(password)s)"
        async with self.conn.acquire() as conn:
            async with  conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"name": name, "email": email, "password": password})
                await conn.commit()

    async def add_token(self, user_id, access_token, second, exp):
        query = f"""INSERT INTO `token` (`access_token`, `user_id`, `created_at`, `exp`) VALUES (%(access_token)s, 
                    %(user_id)s, %(second)s, %(exp)s)"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"access_token": access_token,
                                             "user_id": user_id,
                                             "second": second,
                                             "exp": exp})
                await conn.commit()

    async def select_user_email(self, email):
        query = f"SELECT * FROM `user` WHERE email = %(email)s"
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"email": email})
                row = await cursor.fetchone()
        return row

    async def add_propose(self, name, status, user_id):
        query = f"""INSERT INTO `propose` (`title`, `status`, `user_id`, `created_at`)
                    VALUES (%(name)s, %(status)s, %(user_id)s, %(date)s)"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"name": name,
                                             "status": status,
                                             "user_id": user_id,
                                             "date": datetime.utcnow()})
                await conn.commit()

    async def add_response(self, text, user_id, propose_id):
        query = f"""INSERT INTO `response` (`text`, `user_id`, `propose_id`, `created_at`)
                    VALUES (%(text)s, %(user_id)s, %(propose_id)s, %(date)s)"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"text": text,
                                             "user_id": user_id,
                                             "propose_id": propose_id,
                                             "date": datetime.utcnow()})
                await conn.commit()

    async def add_message(self, text, response_id, user_id):
        query = f"""INSERT INTO `dialog` (`text`, `response_id`, `user_id`, `created_at`)
                    VALUES (%(text)s, %(response_id)s, %(user_id)s, %(date)s)"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"text": text,
                                             "response_id": response_id,
                                             "user_id": user_id,
                                             "date": datetime.utcnow()})
                await conn.commit()

    async def get_user_by_id(self, user_id):
        query = f"SELECT user.id, user.name, user.email FROM `user` WHERE id = %(user_id)s"
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"user_id": user_id})
                row = await cursor.fetchone()
        return row

    async def get_responses(self, propose_id, user_id):
        query = f"""SELECT * FROM (
                    SELECT * FROM `response` WHERE `propose_id` = %(propose_id)s AND user_id = %(user_id)s
                    UNION
                    SELECT `response`.* FROM `response`
                    JOIN `propose` ON `response`.propose_id = `propose`.id
                    WHERE `propose`.user_id = %(user_id)s AND propose_id = %(propose_id)s)
                    AS combined_result
                    ORDER BY created_at DESC"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"user_id": user_id, "propose_id": propose_id})
                rows = await cursor.fetchall()
        return rows

    async def select_propose(self, propose_id):
        query = f"""SELECT propose.id, user.name, propose.status, propose.title,
                    propose.user_id, propose.created_at FROM `propose`
                    JOIN`user` ON `propose`.user_id = `user`.id
                    WHERE `propose`.id = %(propose_id)s """
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"propose_id": propose_id})
                row = await cursor.fetchone()
        return row

    async def select_count_propose(self, limit, offset):
        query = f"""SELECT `propose`.id, `user`.name, `propose`.status, `propose`.title,
                    `propose`.created_at, `propose`.user_id FROM `propose` 
                    JOIN `user` ON `propose`.user_id = `user`.id WHERE `user`.id = `propose`.user_id
                    ORDER BY `propose`.created_at DESC
                    LIMIT %(offset)s, %(limit)s"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"offset": (offset - 1) * limit, "limit": limit})
                rows = await cursor.fetchall()
        return rows

    async def get_dialog_history(self, response_id):
        query = f"""SELECT `dialog`.* FROM `response`
                     JOIN `dialog` ON `response`.id = `dialog`.response_id
                     WHERE `dialog`.response_id = %(response_id)s"""
        async with self.conn.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, {"response_id": response_id})
                rows = await cursor.fetchall()
        return rows
    async def start(self):
        try:
            self.conn = await aiomysql.create_pool(
                host=HOST,
                port=PORT,
                user=USER,
                password=PASSWORD,
                db=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
        except aiomysql.Error as e:
            print(f'Error connecting: {e}')
            sys.exit(1)


# loop = asyncio.get_event_loop()
db = DataBase()

# loop.run_until_complete(db.start())
