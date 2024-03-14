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

    def __init__(self, token_manager, api_handler):
        self.token_manager = token_manager
        self.api_handler = api_handler

    async def send_feedback_card(self, turn_context: TurnContext):
        # Create a HeroCard with star rating buttons for feedback
        card = HeroCard(
            title="If you want, rate your experience",
            text="Click on the thumbs to rate.",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    title="👍🏽",
                    value="thumbs_up"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="👎🏽",
                    value="thumbs_down"
                ),
                # CardAction(
                #     type=ActionTypes.im_back,
                #     title="⭐⭐⭐",
                #     value="3_stars"
                # ),
                # CardAction(
                #     type=ActionTypes.im_back,
                #     title="⭐⭐⭐⭐",
                #     value="4_stars"
                # ),
                # CardAction(
                #     type=ActionTypes.im_back,
                #     title="⭐⭐⭐⭐⭐",
                #     value="5_stars"
                # ),
            ]
        )
        attachment = Attachment(content_type="application/vnd.microsoft.card.hero", content=card)
        await turn_context.send_activity(MessageFactory.attachment(attachment))

    async def on_message_reaction_activity(self, turn_context: TurnContext):
        # Handle the feedback when the user clicks on a star rating
        feedback = turn_context.activity.text

        if feedback in ['thumbs_up', 'thumbs_down']:#, '3_stars', '4_stars', '5_stars']:
            # Map the feedback to a numerical rating
            rating = feedback #.split('_')[0]
            # Here you can handle the rating value, e.g., store it, respond to the user, etc.
            logging.info(f"User rated with {rating} thumbs.")
            await turn_context.send_activity(f"Thank you for your feedback! You rated this experience with {rating}.")

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
        feedback_str = "thumbs_"
        text = turn_context.activity.text

        if feedback_str in text:
            await self.on_message_reaction_activity(turn_context)
        # Retrieve the api_token using user_id from the database
        else:
            api_token = self.token_manager.retrieve_token(turn_context.activity.from_property.id)

            logging.debug(f'\n{turn_context.activity.from_property.id=}\n')
            logging.debug(f'\n{api_token=}\n')

            # Send the user message
            # await turn_context.send_activity(f"User: {text}")

            await turn_context.send_activity(Activity(type=ActivityTypes.typing))
            time.sleep(3)  # wait before sending the next activity

            # Send the message and wait for the response
            await self.api_handler.send_message(api_token, text, turn_context)
            await self.send_feedback_card(turn_context)
