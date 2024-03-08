import json
import logging
import os
import sys


from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount
from botbuilder.core.teams import TeamsInfo


class EchoBot(ActivityHandler):

    def __init__(self, token_manager, api_handler):
        self.token_manager = token_manager
        self.api_handler = api_handler

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                api_token = None
                user_info = None
                try:
                    user_info = await TeamsInfo.get_member(turn_context, member.id)

                    self.api_handler.set_email(user_info.email)
                    api_token = self.api_handler.get_gpa_token_data(user_info.email)
                    self.token_manager.store_token(member.id, api_token)

                except Exception as e:
                    logging.error(f'Failed to find user. Exiting program. Error message:{e}')
                    sys.exit()

                logging.debug(
                    f"\n\n{ user_info.email=}\n\n{member.id=}\n\n{api_token=}\n\n"
                    )
                await turn_context.send_activity(f"Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        # Extract text from the incoming activity
        text = turn_context.activity.text

        # Retrieve the api_token using user_id from the database
        api_token = self.token_manager.retrieve_token(turn_context.activity.from_property.id)

        logging.debug(f'\n{turn_context.activity.from_property.id=}\n')
        logging.debug(f'\n{api_token=}\n')

        await self.api_handler.send_message(api_token, text, turn_context)
