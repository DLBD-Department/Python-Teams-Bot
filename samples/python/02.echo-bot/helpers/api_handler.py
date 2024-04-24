from dotenv import load_dotenv
import os
import aiohttp
import json
import logging
from botbuilder.core import MessageFactory
from botbuilder.schema import Attachment
from helpers.custom_messages import get_adaptive_card


load_dotenv()

URL_GET_TOKEN = os.getenv('GPA_API_KEY')
URL_REGISTER_USER = os.getenv('GPA_API_REGISTER')
URL_ACTIVATE_USER = os.getenv('GPA_API_ACTIVATE')
URL_GPA_API_CHAT = os.getenv('GPA_API_CHAT')
URL_GPA_API_RESET = os.getenv('GPA_API_RESET')
URL_GPA_API_FEEDBACK = os.getenv('GPA_API_FEEDBACK')
GPA_ADMIN_TOKEN = os.getenv('GPA_ADMIN_TOKEN')



class APIHandler:
    """Handles API interactions and user state management for a chat application."""

    def __init__(self, logger: logging.Logger):
        """Initializes the API handler with a logger."""
        self.email = None
        self.logger = logger

    def set_email(self, email):
        """Sets the user's email address."""
        self.logger.info('Setting email...')
        self.email = email

    async def register_user(self):
        """Registers a new user using their email."""
        params = {"email": self.email}
        headers = self.build_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.post(URL_REGISTER_USER, data=json.dumps(params), headers=headers)
        return response

    async def activate_user(self):
        """Activates the user's account."""
        activate_params = {"emails": [self.email]}
        headers = self.build_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.post(URL_ACTIVATE_USER, data=json.dumps(activate_params), headers=headers)
        return response

    async def get_token(self):
        """Retrieves an API token for the user."""
        params = {"email": self.email}
        headers = self.build_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(URL_GET_TOKEN, params=params, headers=headers)
        return response

    async def get_gpa_token_data(self) -> str:
        """Attempts to register, activate, and retrieve a user's GPA API token."""
        token_data = None
        
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

    def build_headers(self):
        """Builds the HTTP headers required for API requests."""
        return {
            'Content-Type': 'application/json',
            "accept": "application/json",
            "Authorization": f"Bearer {GPA_ADMIN_TOKEN}"
        }

    def add_text_to_adaptive_card(self, text:str, content:dict):
        """Creates an adaptive card attachment from the given text and content."""
        card_content=get_adaptive_card(text, content)
        card_attachment = Attachment(
            content_type="application/vnd.microsoft.card.adaptive", 
            content=card_content
            )
        return card_attachment

    async def send_feedback(self, api_token, payload, turn_context):
        """Sends user feedback to the GPA API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            }
            if '👍' in payload['feedback'] or '👎' in payload['feedback']:
                self.logger.info("Handling feedback action.")
                async with session.post(
                    URL_GPA_API_FEEDBACK, headers=headers, json=payload
                ) as response:
                    if response.status == 200:
                        self.logger.info("Feedback was sent.")
                        await turn_context.send_activity(
                            MessageFactory.text(
                                "Thank you for the feedback!"
                            )
                        )
                    else:
                        await turn_context.send_activity(
                            MessageFactory.text(
                                "An error occurred while sending feedback."
                            )
                        )
            else:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "An error occurred while processing feedback"
                        )
                    )

    async def send_message(self, api_token, text, turn_context):
        """Sends a message to the user through the GPA API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            }
            data = {"q": text}

            if text == "/reset":
                self.logger.info("Resetting the conversation history...")

                async with session.post(
                    URL_GPA_API_RESET, headers=headers
                ) as response:
                    if response.status == 200:
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
                        self.logger.info(f"\n{response_data['content']=}\n")
                        if "How can I assist you today?" in response_data['content']:
                            await turn_context.send_activity(
                                MessageFactory.text(response_data['content']))
                        else:
                            await turn_context.send_activity(
                                MessageFactory.attachment(
                                    self.add_text_to_adaptive_card(
                                        response_data['content'],
                                        response_data['content']
                                        )
                                    )
                                )
                    else:
                        await turn_context.send_activity(
                            MessageFactory.text(
                                "An error occurred while processing your request"
                                )
                            )
                            