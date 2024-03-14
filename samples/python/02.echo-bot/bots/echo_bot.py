import json
import logging
import os
import sys
import asyncio
import time

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


class EchoBot(ActivityHandler):
    """
    A template bot that talks to the user:
        - uses a custom LLM API to respond ot user message
        - asks for feedback
        - stores basic user info to internal db
    """

    def __init__(self, token_manager, api_handler):
        self.token_manager = token_manager
        self.api_handler = api_handler

    async def send_feedback_card(self, turn_context: TurnContext):
        """Send a feedback card to the user."""
        card = HeroCard(
            # title="If you want, you can rate your experience",
            text="Click on the thumbs to rate the answer.",
            buttons=[
                CardAction(type=ActionTypes.im_back, title="👍🏽", value="thumbs_up"),
                CardAction(type=ActionTypes.im_back, title="👎🏽", value="thumbs_down"),
                # CardAction(
                #     type=ActionTypes.im_back,
                #     title="⭐⭐⭐",
                #     value="3_stars"
                # ),
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
        ]:  # , '3_stars', '4_stars', '5_stars']:
            rating = feedback  # .split('_')[0]
            logging.info(f"User rated with {rating}.")
            await turn_context.send_activity(
                f"Thank you for your feedback! You rated this experience with {rating}."
            )

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        """Greet the user when they join the conversation and store their email and token."""
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
                    logging.error(
                        f"Failed to find user. Exiting program. Error message:{e}"
                    )
                    sys.exit()

                logging.debug(
                    f"\n\n{ user_info.email=}\n\n{member.id=}\n\n{api_token=}\n\n"
                )
                await turn_context.send_activity(f"Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        """Respond to the user's message."""
        feedback_str = "thumbs_"

        text = turn_context.activity.text

        if feedback_str in text:
            await self.on_message_reaction_activity(turn_context)
        else:
            # Retrieve the api_token using user_id from the database
            api_token = self.token_manager.retrieve_token(
                turn_context.activity.from_property.id
            )

            logging.debug(f"\n{turn_context.activity.from_property.id=}\n")
            logging.debug(f"\n{api_token=}\n")

            # await turn_context.send_activity(f"User: {text}")

            await turn_context.send_activity(Activity(type=ActivityTypes.typing))
            time.sleep(3)  # wait before sending the next activity

            # Send the message and feedback card after getting the response from the API
            await self.api_handler.send_message(api_token, text, turn_context)
            await self.send_feedback_card(turn_context)
