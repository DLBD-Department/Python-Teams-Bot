
# Teams Python Bot

Teams bot is an advanced template-based bot that engages users through conversational interfaces with special frontend features, integrates with custom APIs for dynamic responses, and incorporates feedback mechanisms for future improvements. 
## Features

- **Custom API Integration:** Leverages a custom API to generate responses, enhancing user interactions with dynamic content.
- **Feedback Mechanism:** Collects user feedback to gauge satisfaction and guide future improvements.
- **User Activity Tracking:** Maintains records of user interactions, including activity dates, to personalize the experience.
- **Proactive Messaging:** Capable of initiating conversations with users, ensuring engagement even when not directly prompted.

## Technical Setup

### Prerequisites

- Python 3.7 or newer.
- `git` for cloning the repository.
- A configured `.env` file with necessary environment variables.

### Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory and install requirements using `pip install -r requirements.txt`.
3. Configure the `.env` file with your bot's credentials and other necessary variables.

### Configuration

Logging is set up to record both to the console and a file (`bot.log`) for easy monitoring and debugging. The logging level is INFO by default but can be adjusted as needed.

## Running the Bot

To start the bot, run:

```python app.py```
## Usage

Once the bot is running, it can be interacted with through Microsoft Teams. Users can receive welcome messages, ask questions to receive information about specific topics like Alkemy projects, collect and store feedback through thumbs up/down reactions, get links and information from LLM's Knowledge Base (or Long-Term Memory).

## Extending the Bot

- **Custom LLM API:** Implement your own LLM API by modifying the `api_handler` logic.
- **User Validation:** Add or modify user validation logic within the `validate_and_store_user_info` method.


## Troubleshooting

- **Logging:** Check the `bot.log` file and console output for any errors or warnings.
- **Dependencies:** Ensure all dependencies are correctly installed and compatible with your Python version.

## Documentation and practices

- [Microsoft Teams Bot Framework](https://docs.microsoft.com/en-us/microsoftteams/platform/bots/what-are-bots)
- This code tries to adhere to SOLID principles, uses docstrings and typehints wherever possible according to PEP 8 guidelines.