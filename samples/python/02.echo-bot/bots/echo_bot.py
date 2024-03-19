import json
import logging
import os
import sys
import asyncio
import time

from dotenv import load_dotenv

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.core.teams import TeamsInfo
from botbuilder.schema import (
    ChannelAccount,
    Activity,
    ActivityTypes,
    Attachment,
    CardAction,
    ActionTypes,
    HeroCard,
    CardImage,
)

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('bot.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)

class EchoBot(ActivityHandler):
    """
    A template bot that talks to the user:
        - uses a custom LLM API to respond ot user message
        - asks for feedback
        - stores basic user info to internal db
    """

    def __init__(self, token_manager, api_handler, hardcoded_user_validator):
        self.token_manager = token_manager
        self.api_handler = api_handler
        self.hardcoded_user_validator = hardcoded_user_validator

    async def send_feedback_card(self, turn_context: TurnContext):
        """Send a feedback card to the user."""
        card = HeroCard(
            # title="If you want, you can rate your experience",
            text="Click on the thumbs to rate the answer.",
            buttons=[
                CardAction(type=ActionTypes.im_back, title="👍🏽", value="thumbs_up"),
                CardAction(type=ActionTypes.im_back, title="👎🏽", value="thumbs_down"),
            ],
        )
        attachment = Attachment(
            content_type="application/vnd.microsoft.card.hero", content=card
        )
        await turn_context.send_activity(MessageFactory.attachment(attachment))

    async def on_message_reaction_activity(self, turn_context: TurnContext):
        """Handle the user's feedback."""
        feedback = turn_context.activity.text

        if feedback in [
            "thumbs_up",
            "thumbs_down",
        ]:
            rating = feedback
            logger.info(f"User rated with {rating}.")
            await turn_context.send_activity(
                f"Thank you for your feedback! You rated this experience with {rating}."
            )

    async def validate_and_store_user_info(self, turn_context: TurnContext, member_id: str):
        """Validate the user and store their email and token."""
        user_info = await TeamsInfo.get_member(turn_context, member_id)
        user_validated= await self.hardcoded_user_validator.validate_user(
            turn_context,
            user_info.email,
            logger
        )
        if user_validated:
            logger.info('Checking if token is in the local database...')
            api_token = self.token_manager.retrieve_token(member_id)
            if api_token:
                logger.info(f'Token found. {api_token=}')
                return api_token
            else:
                logger.info(f'Token not found. Registering user {user_info.email}')   # If the user is not in the database, register and activate them
                api_token = await self.api_handler.get_gpa_token_data()
                self.token_manager.store_token(member_id, api_token)
                return api_token

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        """Greet the user when they join the conversation and store their email and token."""
        logger.info('--- Called on_members_added_activity ---')
        pass
        #TODO: This is not working. The bot is not sending the welcome message to the user.
        # for member in members_added:
        #     if member.id != turn_context.activity.recipient.id:
        #         try:
        #             if await self.validate_and_store_user_info(turn_context, member.id):
        #                 await turn_context.send_activity(f"Hello and welcome!")
        #         except Exception as e:
        #             logger.info(f"Failed to find user. Error message:{e}")

    async def on_message_activity(self, turn_context: TurnContext):
        """Respond to the user's message."""

        logger.info('--- Called on_message_activity ---')
        member_id = turn_context.activity.from_property.id
        user_info = await TeamsInfo.get_member(turn_context, member_id)
        user_validated_token = await self.validate_and_store_user_info(turn_context, member_id)
        if user_validated_token:
            text = turn_context.activity.text
            if "thumbs_" in text:
                await self.on_message_reaction_activity(turn_context)
            else:
                logger.info(f"\n{user_info.email=}\n{member_id=}\n{user_validated_token=}\n")

                await turn_context.send_activity(Activity(type=ActivityTypes.typing))
                logger.info(f"The message was sent to GPA.")

                # Send the message and feedback card after getting the response from the API
                await self.api_handler.send_message(user_validated_token, text, turn_context)
                await self.send_feedback_card(turn_context)
