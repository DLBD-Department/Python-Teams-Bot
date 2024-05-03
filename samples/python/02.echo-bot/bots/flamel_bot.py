import json
import logging
import os
import sys
import asyncio
import time
import datetime

from dotenv import load_dotenv
from typing import Callable
from asyncio import Future

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
    ConversationReference,
    SuggestedActions,
)
from helpers.custom_messages import get_en_welcome_message, get_it_welcome_message, custom_actions_card, send_feedback_card

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("bot.log")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)
c_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
f_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)


class FlamelBot(ActivityHandler):
    """
    A template bot that talks to the user:
        - uses a custom LLM API to respond ot user message
        - asks for feedback
        - stores basic user info to internal db
        - tracks last_active date for each user
    """

    def __init__(
        self,
        adapter,
        token_manager=None,
        api_handler=None,
        hardcoded_user_validator=None,
        presence_recorder=None,
    ):
        self.token_manager = token_manager
        self.api_handler = api_handler
        self.hardcoded_user_validator = hardcoded_user_validator
        self.adapter = adapter
        self.presence_recorder = presence_recorder
        try:
            with open("conversation_references.json", "r") as f:
                data = json.load(f)
                logger.info(f"{data=}")
                self.conversation_references = {
                    key: ConversationReference().from_dict(value)
                    for key, value in data.items()
                }
        except FileNotFoundError:
            self.conversation_references = {}

    def check_and_record_user_activity_date(self, member_id: str) -> None:
        """Check the current date matches the one in the PresenceRecorder for the current member_id.
        If the dates do not match, or if there is no activity in the database, record a new activity date.
        """
        current_date_str = datetime.datetime.now().strftime("%d-%m-%Y")
        last_active_date_str = self.presence_recorder.retrieve_activity(member_id)
        logger.info(f"{last_active_date_str=}")
        if not last_active_date_str or current_date_str != last_active_date_str:
            self.presence_recorder.store_activity(member_id)
            logger.info("Stored last_activity date.")

    async def send_proactive_message(self, message, bot_id):
        """Send a proactive message to all users"""
        logger.info("--- Called send_proactive_message ---")
        for key, conversation_reference in self.conversation_references.items():
            await self.adapter.continue_conversation(
                conversation_reference,
                lambda turn_context: turn_context.send_activity(message),
                bot_id,
            )
    async def _send_suggested_actions(self, turn_context: TurnContext):
        """
        Creates and sends an activity with suggested actions to the user. When the user
        clicks one of the buttons the text value from the "CardAction" will be displayed
        in the channel just as if the user entered the text. There are multiple
        "ActionTypes" that may be used for different situations.
        """

        reply = MessageFactory.text("\u200B")
        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Start New Session",
                    type=ActionTypes.im_back,
                    value="/reset",
                    image="https://via.placeholder.com/20/FF0000?text=R",
                    image_alt_text="R",
                ),
            ]
        )

        return await turn_context.send_activity(reply)

    async def _send_proactive_message(self, message: str) -> Callable[[TurnContext], Future]:
        """Generates a lambda to send a proactive message. The lambda accepts a TurnContext and returns a Future."""
        return lambda turn_context: turn_context.send_activity(message)

    async def validate_and_store_user_info(
        self, turn_context: TurnContext, member_id: str
    ) -> str:
        """Validate the user and store their email and token."""
        user_info = await TeamsInfo.get_member(turn_context, member_id)
        # user_validated= await self.hardcoded_user_validator.validate_user(
        #     turn_context,
        #     user_info.email,
        #     logger
        # )
        # if user_validated:
        logger.info("Checking if token is in the local database...")
        api_token = self.token_manager.retrieve_token(member_id)
        if api_token:
            logger.info(f"Token found. {api_token=}")
            return api_token
        else:
            logger.info(f"Token not found. Registering user {user_info.email}")
            self.api_handler.set_email(
                user_info.email
            )  # If the user is not in the database, register and activate them
            api_token = await self.api_handler.get_gpa_token_data()
            self.token_manager.store_token(member_id, api_token)
            return api_token

    async def send_welcome_message(self, turn_context: TurnContext) ->None:
        """Send a welcome message to new members."""
        user_info = await self.get_member_info(turn_context)
        user_name = user_info.name
        locale = await self.detect_locale(turn_context)
        logger.info(f"Welcome message was sent to the user {user_name}.")
        logger.info(f"Using locale: {locale}.")
        if "en" in locale:
            await turn_context.send_activity(get_en_welcome_message(user_name))
            await custom_actions_card(turn_context, locale)
        else:
            await turn_context.send_activity(get_it_welcome_message(user_name))
            await custom_actions_card(turn_context, locale)

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ) -> None:
        """Greet the user when they join the conversation and store their email and token."""

        logger.info("--- Called on_members_added_activity ---")
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                try:
                    if await self.validate_and_store_user_info(
                        turn_context, turn_context.activity.recipient.id
                    ):
                        await self.send_welcome_message(turn_context)
                        self.store_conversation_references(turn_context)
                except Exception as e:
                    logger.info(f"Failed to find user. Error message:{e}")
            else:
                logger.info(
                    "User is the bot itself and it was being added to the existing conversation."
                )
                await self.send_welcome_message(turn_context)

    def store_conversation_references(self, turn_context: TurnContext) ->None:
        """Store the conversation reference."""
        logger.info(f"--- Called store_conversation_references ---")
        conversation_reference = turn_context.activity.get_conversation_reference()
        self.conversation_references[conversation_reference.conversation.id] = (
            conversation_reference
        )
        with open("conversation_references.json", "w") as f:
            json.dump(
                {
                    key: value.serialize()
                    for key, value in self.conversation_references.items()
                },
                f,
            )

    async def get_member_info(self, turn_context: TurnContext):
        member_id = turn_context.activity.from_property.id
        user_info = await TeamsInfo.get_member(turn_context, member_id)
        return user_info

    def thumbs_in_text(self, text:str) -> str:
        return "thumbs_" in text

    def log_user_info(self, user_info, user_validated_token=None) -> None:
        logger.info(f"\n{user_info.email=}\n{user_info.id=}\n{user_validated_token=}\n")

    async def send_typing_indicator(self, turn_context: TurnContext) -> None:
        logger.info("Typing indicator was activated.")
        await turn_context.send_activity(Activity(type=ActivityTypes.typing))

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """Respond to the user's message."""

        logger.info("--- Called on_message_activity ---")
        user_info = await self.get_member_info(turn_context)
        user_validated_token = await self.validate_and_store_user_info(
            turn_context, user_info.id
        )

        if user_validated_token:
            logger.info(f"--- User {user_info.name} validated ---")
            self.check_and_record_user_activity_date(user_info.id)

            if turn_context.activity.value:
                action_value = turn_context.activity.value
                logger.info(f"\n{action_value=}\n\n")
                try:
                    await self.handle_feedback_and_reset_actions(
                        turn_context, user_info, user_validated_token, action_value
                    )
                except Exception as e:
                    logger.error(f"An error occured: {e}")
                    pass
            else:
                text = turn_context.activity.text
                await self.handle_message(
                    turn_context, user_info, user_validated_token, text
                )

    async def detect_locale(self, turn_context: TurnContext) -> str:
        """Detect the user's locale."""
        default_locale = "en-us"  # Define your default locale
        locale = (
            turn_context.activity.locale
            if turn_context.activity.locale
            else default_locale
        )
        return locale

    async def handle_feedback_and_reset_actions(
        self, turn_context: TurnContext, user_info, user_validated_token, payload
    ) -> None:
        """Handle feedback."""
        if "feedback" in payload:
            await self.api_handler.send_feedback(
                user_validated_token, payload, turn_context
            )
        else:
            logger.info("Resetting the conversation.")
            await self.handle_message(
                turn_context, user_info, user_validated_token, payload["action"]
            )

    async def handle_message(
        self, turn_context: TurnContext, user_info, user_validated_token, text
    ) -> None:
        """Handle messages."""
        self.log_user_info(user_info, user_validated_token)
        await self.send_typing_indicator(turn_context)
        logger.info(f"The message was sent to GPA.")
        await self.send_message_with_feedback(user_validated_token, text, turn_context)
        await self._send_suggested_actions(turn_context)

    async def send_message_with_feedback(
        self, user_validated_token, text, turn_context
    ) -> None:
        """Send a message with feedback and reset_buttons."""
        await self.api_handler.send_message(user_validated_token, text, turn_context)

    # async def on_conversation_update_activity(self, turn_context: TurnContext):
    #     """
    #     Respond to conversation update activities - can be used to send welcome messages.
    #     """
    #     logger.info('--- Called on_conversation_update_activity ---')
    #     # If the bot is added to the conversation, send a welcome message
    #     if any(member.id == turn_context.activity.recipient.id for member in turn_context.activity.members_added):
    #         await self.send_welcome_message(turn_context)
    #     # # Alternatively, to send a welcome message to each user that gets added (not the bot)
    #     # for member in turn_context.activity.members_added:
    #     #     if member.id != turn_context.activity.recipient.id:  # Make sure it's not the bot being added
    #     #         # You might want to create a personalized welcome message
    #     #         welcome_text = f"Welcome, {member.name}!"
    #     #         await turn_context.send_activity(MessageFactory.text(welcome_text))

    #     # Make sure to include other types of conversation updates as needed
    #     await super().on_conversation_update_activity(turn_context)
