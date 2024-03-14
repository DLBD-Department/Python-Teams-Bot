import json
import logging
import os
import sys

import duckdb
import aiohttp
from dotenv import load_dotenv
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount
from botbuilder.core.teams import TeamsInfo

load_dotenv()

# Initialize DuckDB
conn = duckdb.connect('database.db')
c = conn.cursor()

# Create a table to store user_id and api_token
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR,
        api_token VARCHAR
    )
""")

if os.path.exists('users.csv'):
    conn.execute("COPY users FROM 'users.csv' (HEADER)")
else:
    print("File 'users.csv' does not exist.")


class EchoBot(ActivityHandler):

    async def get_gpa_token_data(self, user_email:str) -> str:
        url_get_token = os.getenv('GPA_API_KEY')
        url_register_user = os.getenv('GPA_API_REGISTER')
        url_activate_user = os.getenv('GPA_API_ACTIVATE')
        activate_params = {"emails": [user_email]}
        params = {"email": f"{user_email}"}
        headers = {
            'Content-Type': 'application/json',
            "accept": "application/json",
            "Authorization": f"Bearer {os.getenv('GPA_ADMIN_TOKEN')}"
        }
        token_data = None

        async with aiohttp.ClientSession() as session:
            try:
                logging.error("Registering user...")
                async with session.post(url_register_user, data=json.dumps(params), headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        logging.error(f"\n{token_data=}\n")                         
                logging.error("Activating user...")
                async with session.post(url_activate_user, data=json.dumps(activate_params), headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return token_data['api_token']
            except Exception as e:
                async with session.get(url_get_token, data=json.dumps(params), headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['api_token']
    
    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                user_email = None
                user_name = None
                api_token = None
                # Fetch additional information about the user
                try:
                    user_info = await TeamsInfo.get_member(turn_context, member.id)
                    user_email = user_info.email
                    user_name = user_info.name
                    api_token = await self.get_gpa_token_data(user_email)
                    
                except Exception as e:
                    logging.error(f'Failed to find user. Exiting program. Error message:{e}')
                    sys.exit()


                logging.error(
                    f"\n\n{user_email=}\n\n{member.id=}\n\n{api_token=}\n\n"
                    )
                
                # Store the user_id and api_token into the database
                # api_token = os.getenv('GPA_TOKEN')
                c.execute(f"INSERT OR IGNORE INTO users (user_id, api_token) VALUES ('{member.id}', '{api_token}')")
                conn.commit()
                conn.execute("COPY users TO 'users.csv' (HEADER)")

                await turn_context.send_activity(f"Hello and welcome user with email: {user_email}!")

    async def on_message_activity(self, turn_context: TurnContext):
        # Extract text from the incoming activity
        text = turn_context.activity.text

        # Retrieve the api_token using user_id from the database
        c.execute(f"SELECT api_token FROM users WHERE user_id = '{turn_context.activity.from_property.id}'")
        row = c.fetchone()
        if row is None:
            await turn_context.send_activity(MessageFactory.text("User not found"))
            return
        api_token = row[0]
        logging.error(f'\n{turn_context.activity.from_property.id=}\n')
        logging.error(conn.sql(f"SELECT api_token FROM users WHERE user_id = '{turn_context.activity.from_property.id}'").show())

        async with aiohttp.ClientSession() as session:
            url = os.getenv('GPA_API_CHAT')
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            }
            data = {"q": text}
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    await turn_context.send_activity(MessageFactory.text(response_data['content']))
                else:
                    await turn_context.send_activity(MessageFactory.text("An error occurred while processing your request"))
