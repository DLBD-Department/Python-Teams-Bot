import duckdb
import aiohttp
import json
import os
import logging


class TokenManager:
    def __init__(self):
        self.conn = duckdb.connect('database.db')
        self.c = self.conn.cursor()
        if os.path.exists('users.csv'):
            self.conn.execute("COPY users FROM 'users.csv' (HEADER)")
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR,
                api_token VARCHAR
            )
        """)

    def store_token(self, user_id, api_token) -> None:
        self.c.execute(
            f"INSERT OR IGNORE INTO users (user_id, api_token) VALUES ('{user_id}', '{api_token}')"
            )
        self.conn.commit()
        self.conn.execute("COPY users TO 'users.csv' (HEADER)")

    def retrieve_token(self, user_id) -> str:
        self.c.execute(f"SELECT api_token FROM users WHERE user_id = '{user_id}'")
        row = self.c.fetchone()
        return row[0] if row else None

    def show_info(self, turn_context):
        logging.debug(self.conn.sql(
            f"SELECT api_token FROM users WHERE user_id = '{turn_context.activity.from_property.id}'"
            ).show())
