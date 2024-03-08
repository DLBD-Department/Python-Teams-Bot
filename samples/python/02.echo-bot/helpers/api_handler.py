from dotenv import load_dotenv
import os
import aiohttp
import json
import logging
from botbuilder.core import MessageFactory


load_dotenv()

URL_GET_TOKEN = os.getenv('GPA_API_KEY')
URL_REGISTER_USER = os.getenv('GPA_API_REGISTER')
URL_ACTIVATE_USER = os.getenv('GPA_API_ACTIVATE')
URL_GPA_API_CHAT = os.getenv('GPA_API_CHAT')
GPA_ADMIN_TOKEN = os.getenv('GPA_ADMIN_TOKEN')


class APIHandler:
    def __init__(self):
        self.email = None

    def set_email(self, email):
        self.email = email

    async def get_gpa_token_data(self, user_email) -> str:

        token_data = None
        activate_params = {"emails": [self.email]}
        params = {"email": f"{self.email}"}
        headers = {
            'Content-Type': 'application/json',
            "accept": "application/json",
            "Authorization": f"Bearer {GPA_ADMIN_TOKEN}"
        }

        async with aiohttp.ClientSession() as session:
            try:
                logging.error("Registering user...")
                async with session.post(
                    URL_REGISTER_USER, data=json.dumps(params), headers=headers
                    ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        logging.error(f"\n{token_data=}\n")
                logging.error("Activating user...")
                async with session.post(
                    URL_ACTIVATE_USER, data=json.dumps(activate_params), headers=headers
                    ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return token_data['api_token']
            except Exception as e:
                async with session.get(
                    URL_GET_TOKEN, data=json.dumps(params), headers=headers
                    ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['api_token']

    async def send_message(self, api_token, text, turn_context):

        async with aiohttp.ClientSession() as session:

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            }
            data = {"q": text}

            async with session.post(
                URL_GPA_API_CHAT, headers=headers, json=data
                ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    await turn_context.send_activity(
                        MessageFactory.text(response_data['content'])
                        )
                else:
                    await turn_context.send_activity(
                        MessageFactory.text(
                            "An error occurred while processing your request"
                            )
                        )