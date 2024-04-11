import os
import logging
from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter
from botbuilder.schema import Activity
from bots.echo_bot import EchoBot  # replace with the actual location of your bot class
from helpers import HardcodedUserValidator
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('proactive_messaging.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)


APP_ID = os.environ.get("MicrosoftAppId", os.getenv('APP_ID'))
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", os.getenv('APP_PASSWORD'))


# Initialize the bot and adapter
settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)
token_manager = None
api_handler = None
hardcoded_user_validator = HardcodedUserValidator()
bot = EchoBot(adapter)

app = web.Application()


# Define the function that runs on startup
async def on_startup(app):
    """
    Function that runs on startup of the app. It sends a proactive message and then stops the app.
    """
    proactive_message = Activity(
        type="message",
        text="This is a proactive message.",
        channel_id="msteams",  # Ensure to specify the channel ID
    )

    # Send the proactive message
    await bot.post_activity(proactive_message)
    
    # Exit the app after sending the proactive message
    raise web.GracefulExit()


# Add the on_startup function to the app startup handlers
app.on_startup.append(on_startup)

# Run the app
web.run_app(app)