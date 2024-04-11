 
import sys
import traceback
from datetime import datetime
from http import HTTPStatus
import requests
import logging
import json

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    TurnContext,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.core import ShowTypingMiddleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.schema import Activity, ActivityTypes
 
from bots import EchoBot
from helpers import APIHandler, TokenManager, HardcodedUserValidator, PresenceRecorder
from config import DefaultConfig
 
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



CONFIG = DefaultConfig()
 
# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))
 
# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
 
    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)
 
 
ADAPTER.on_turn_error = on_error
ADAPTER.use(ShowTypingMiddleware(delay=0, period=10))

 
# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
        # logger.info(f"Payload: {json.dumps(body)}")
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
 
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""
    # logger.info(f'{auth_header=}')
 
    try:
        response = await ADAPTER.process_activity(auth_header, activity, BOT.on_turn)
    except Exception as error:
        raise error
        logger.error(f'{error=}')

    if response:
        response_dict = response.__dict__
        logger.info(f"\n[Bot Response]: {response_dict}\n")
         
        if response.status_code == 200:
            return web.json_response(data=response.body, status=response.status)
        else:
            return Response(status=web.HTTPInternalServerError.status_code)
    return Response(status=HTTPStatus.OK)
 
APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
 
if __name__ == "__main__":
    token_manager = TokenManager(logger=logger)
    api_handler = APIHandler(logger=logger)
    hardcoded_user_validator = HardcodedUserValidator()
    presence_recorder = PresenceRecorder()
    BOT = EchoBot(
        ADAPTER, 
        token_manager, 
        api_handler, 
        hardcoded_user_validator,
        presence_recorder)
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
