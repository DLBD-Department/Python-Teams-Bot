import os
import logging

class HardcodedUserValidator():

    async def validate_user(self, turn_context, user_email: str, logger: logging.Logger) -> bool:
        """Validate the user and store their email and token."""
        try:
            logger.info(f'Trying to validate user {user_email}...')
            allowed_users = os.getenv("ALLOWED_USERS").split(",")
            logger.info(f"Allowed users: {allowed_users}")
            if user_email not in allowed_users:
                await turn_context.send_activity(
                    f"Hello! The bot is in the testing phase and usage is limited only to developers. Thank you for your patience."
                    )
                logger.info(f"User {user_email} is not allowed to use the bot.")
                return False
            else:
                return True
        except Exception as e:
            logger.error(f"Failed to validate user. Error= {e}")
