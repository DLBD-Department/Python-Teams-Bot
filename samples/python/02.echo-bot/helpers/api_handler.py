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
URL_GPA_API_RESET = os.getenv('GPA_API_RESET')
GPA_ADMIN_TOKEN = os.getenv('GPA_ADMIN_TOKEN')


class APIHandler:
    def __init__(self, logger: logging.Logger):
        self.email = None
        self.logger = logger

    def set_email(self, email):
        self.logger.info('Setting email...')
        self.email = email

    async def register_user(self):
        params = {"email": self.email}
        headers = self.build_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.post(URL_REGISTER_USER, data=json.dumps(params), headers=headers)
        return response

    async def activate_user(self):
        activate_params = {"emails": [self.email]}
        headers = self.build_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.post(URL_ACTIVATE_USER, data=json.dumps(activate_params), headers=headers)
        return response

    async def get_token(self):
        params = {"email": self.email}
        headers = self.build_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(URL_GET_TOKEN, params=params, headers=headers)
        return response

    async def get_gpa_token_data(self) -> str:
        token_data = None
        # self.logger.info(f"\n{'email': self.email}\n")

        try:
            self.logger.info("Registering user...")
            response = await self.register_user()
            if response.status == 200:
                token_data = await response.json()
                self.logger.info(f"\n{token_data=}\n")

                self.logger.info("Activating user...")
                response = await self.activate_user()
                if response.status == 200:
                    data = await response.json()
                    self.logger.info(f"{token_data['api_token']=}")
                    return token_data['api_token']

            self.logger.info("User already has a token, getting the token...")
            response = await self.get_token()
            if response.status == 200:
                data = await response.json()
                self.logger.info(f"{data['api_token']=}")
                return data['api_token']

        except Exception as e:
            self.logger.error(f"Failed to get or set user token. Error: {e}")
            # Potentially handle or re-raise exception

    def build_headers(self):
        return {
            'Content-Type': 'application/json',
            "accept": "application/json",
            "Authorization": f"Bearer {GPA_ADMIN_TOKEN}"
        }

    async def send_message(self, api_token, text, turn_context):

        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            }
            data = {"q": text}

            if text == "/reset":
                async with session.post(
                    URL_GPA_API_RESET, headers=headers, json=data
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        await turn_context.send_activity(
                            MessageFactory.text("Conversation has been reset successfully.")
                        )
                    else:
                        await turn_context.send_activity(
                            MessageFactory.text(
                                "An error occurred while resetting the conversation."
                            )
                        )

            else:
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

    # async def get_gpa_token_data(self) -> str:

    #     token_data = None
    #     activate_params = {"emails": [self.email]}
    #     params = {"email": self.email}
    #     self.logger.info(f"\n{params=}\n")
    #     headers = {
    #         'Content-Type': 'application/json',
    #         "accept": "application/json",
    #         "Authorization": f"Bearer {GPA_ADMIN_TOKEN}"
    #     }

    #     async with aiohttp.ClientSession() as session:
    #         try:
    #             self.logger.info("Registering user...")
    #             async with session.post(
    #                 URL_REGISTER_USER, data=json.dumps(params), headers=headers
    #                 ) as response:
    #                 if response.status == 200:
    #                     token_data = await response.json()
    #                     self.logger.info(f"\n{token_data=}\n")
    #             self.logger.info("Activating user...")
    #             async with session.post(
    #                 URL_ACTIVATE_USER, data=json.dumps(activate_params), headers=headers
    #                 ) as response:
    #                 if response.status == 200:
    #                     data = await response.json()
    #                     self.logger.info(f"{token_data['api_token']=}")
    #                     return token_data['api_token']
    #         except Exception as e:
    #             self.logger.info(f"User already has a token, getting the token...")
    #             async with session.get(
    #                 URL_GET_TOKEN, params=params, headers=headers
    #                 ) as response:
    #                 if response.status == 200:
    #                     data = await response.json()
    #                     self.logger.info(f"{data['api_token']=}")
    #                     return data['api_token']

