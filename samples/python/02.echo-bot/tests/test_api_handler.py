import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from helpers.api_handler import APIHandler  # replace 'your_module' with the name of the file containing the APIHandler class

class TestAPIHandler(unittest.IsolatedAsyncioTestCase):
    @patch("aiohttp.ClientSession.post", new_callable=AsyncMock)  # Mock the aiohttp session post method
    @patch("logging.Logger")  # Mock the logger
    async def test_get_gpa_token_data(self, mock_logger, mock_post):
        # Set up mock_post to return the expected response
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.json = AsyncMock(return_value={"api_token": "test_token"})
        mock_post.return_value.__aenter__.return_value = response_mock
        # Example of setting up an AsyncMock to return a specific value when awaited
        mock_post.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"api_token": "alia-a642b963b50124421a7092c03b6228816728b11b2af6886a52dadc83e44ef8d8"}))
        
        # Initialize APIHandler with a mock logger
        handler = APIHandler(logger=mock_logger)
        
        # Set email
        test_email = "stjepan.perkovic@alkemy.com"
        handler.set_email(test_email)

        # Call the method under test
        token_data = await handler.get_gpa_token_data()

        # Assert the token_data is as expected
        self.assertEqual(token_data, "alia-a642b963b50124421a7092c03b6228816728b11b2af6886a52dadc83e44ef8d8")

        # Verify logging calls if necessary (only an example, adjust according to your needs)
        mock_logger.info.assert_called()  # This only checks it was called; you can be more specific

# This allows running the tests via the command line
if __name__ == "__main__":
    pytest.main()
