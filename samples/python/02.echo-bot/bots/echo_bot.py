# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount


load_dotenv()


class EchoBot(ActivityHandler):
    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        return await turn_context.send_activity(
            MessageFactory.text(f"Echo: {turn_context.activity.text}")
        )
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.core.teams import TeamsInfo
from botbuilder.schema import ChannelAccount
import aiohttp
import logging

class EchoBot(ActivityHandler):

    async def on_turn(self, turn_context: TurnContext):
#        logging.error(f"Received activity: {turn_context.activity}")
        
         await super().on_turn(turn_context)

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):        
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                # Fetch additional information about the user
                user_info = await TeamsInfo.get_member(turn_context, member.id)
                user_email = user_info.email
                user_name = user_info.name
                logging.error(f"\n\n{user_email=}\n\n")
                await turn_context.send_activity("Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        # Extract text from the incoming activity
        text = turn_context.activity.text
 
        async with aiohttp.ClientSession() as session:
            url = os.getenv('GPA_API')
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('GPA_TOKEN')}"
            }
            data = {"q": text}  
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    await turn_context.send_activity(MessageFactory.text(response_data['content']))
                else:
                    await turn_context.send_activity(MessageFactory.text("An error occurred while processing your request"))
                    
