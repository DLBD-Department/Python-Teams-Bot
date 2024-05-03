from botbuilder.core import TurnContext, MessageFactory
from botbuilder.schema import Attachment, ActionTypes, CardAction, HeroCard

def get_en_welcome_message(user:str) -> str:
    message = f"""👋 Hey there, I'm Flamel, your trusted virtual colleague. \n\
\n\n&nbsp;\n\n
I'm here to assist you with any questions or tasks you may have. Whether you're seeking information, 
looking for assistance, or trying to find an old document that seems to have vanished into thin air, 
I've got you covered. \n\
\n\n&nbsp;\n\n
Feel free to ask me anything, and I'll do my best to find the answer within Alkemy's knowledge base and provide you with the answers you need.
\n\n&nbsp;\n\n
Here are some suggestions to get started!"""
    return message

def get_it_welcome_message(user:str) -> str:
    message = """👋 Ciao, sono Flamel, il tuo fidato collega virtuale.\n\
\n\n&nbsp;\n\n
Sono qui per aiutarti con qualsiasi domanda o compito di cui potresti avere bisogno.\n\
Che tu stia cercando informazioni, assistenza o un vecchio documento che sembra essere svanito nel nulla, sono qui per darti una mano.\n\
\n\n&nbsp;\n\n
Sentiti libero di chiedermi qualsiasi cosa e farò del mio meglio per trovare la risposta all'interno della knowledge base e fornirti le informazioni di cui hai bisogno.
\n\n&nbsp;\n\n
Ecco alcuni suggerimenti per iniziare!"""
    return message

def get_en_welcome_message_old(user:str) -> str:
    message = f"""Welcome to our chat, {user}!\n
I'm Flamel, your personal assistant. \n
Here are some examples of what I can do:\n\
- tell you more about specific Alkemy projects 
- offer links to Alia X MyLake documents 
- provide information from Alkemy web pages\n\
\n\
Note: As an LLM based chatbot, I'm still prone to hallucination.\n\
That's why I ask you for your understanding."""
    return message

# def get_en_welcome_message(user:str) -> str:
#     message = f"""Welcome to our chat, {user}!\n
# I'm Flamel, your personal assistant. \n
# Here are some examples of what I can do:\n\
# - tell you more about specific Alkemy projects 
# - offer links to Alia X MyLake documents 
# - provide information from Alkemy web pages\n\
# \n\
# Note: As an LLM based chatbot, I'm still prone to hallucination.\n\
# That's why I ask you for your understanding."""
#     return message


def get_it_welcome_message_old(user:str) -> str:
    message = f"""Benvenuto nella nostra chat, {user}!\n
Sono Flamel, il tuo assistente personale. \n
Ecco alcuni esempi di ciò che posso fare:\n\
- raccontarti di più su progetti specifici di Alkemy 
- offrire link ai documenti Alia X MyLake 
- fornire informazioni dalle pagine web di Alkemy\n\
\n\
Nota: come chatbot basato su LLM, sono ancora incline alle allucinazioni.\n\
Ecco perché vi chiedo la vostra comprensione."""
    return message


def get_adaptive_card(text, content:str):
    return {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.5",
    "body": [
        {
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": text,
                    "wrap": True,
                    "spacing": "ExtraLarge",
                    "height": "stretch",
                    "size": "Medium",
                    "weight": "Default",
                    "fontType": "Default",
                    "style": "default",
                    "isSubtle": False,
                    "color": "Default"
                }
            ]
        }
    ],
    "msteams": {  
        "width": "Full"  
    }, 
    "actions": [
        {
            "type": "Action.Submit",
            "title": "👍",
            "data": { "feedback": "👍", 'content': content}
        },
        {
            "type": "Action.Submit",
            "title": "👎",
            "data": { "feedback": "👎", 'content': content}
        },
        {
            "type": "Action.Submit",
            "title": "New Session",
            "data": { "action": "/reset", 'content': content} 
        }
    ]
}


async def custom_actions_card(turn_context: TurnContext, locale: str) -> None:
    """Send a custom actions card to the user."""
    en_card = HeroCard(
    # title="If you want, you can rate your experience",
    buttons=[
        CardAction(
            type=ActionTypes.post_back,
            title="I want to learn more about Flamel.",
            value="I want to learn more about Flamel.",
        ),
        CardAction(
            type=ActionTypes.post_back,
            title="Give me some offers of projects about improving customer care",
            value="Give me some offers of projects about improving customer care",
        ),
        CardAction(
            type=ActionTypes.post_back,
            title="Give me credential of projects on telco",
            value="Give me credential of projects on telco",
        ),
        CardAction(
            type=ActionTypes.post_back,
            title="What are the Alkemy's conventions and benefits?",
            value="What are the Alkemy's conventions and benefits?",
        ),
    ]
    )
    it_card = HeroCard(
        # title="Se sei interessato, puoi valutare la tua esperienza",
        buttons=[
            CardAction(
                type=ActionTypes.post_back,
                title="Voglio saperne di più su Flamel",
                value="Voglio saperne di più su Flamel",
            ),
            CardAction(
                type=ActionTypes.post_back,
                title="Dammi delle offerte di progetti riguardanti il miglioramento della customer care",
                value="Dammi delle offerte di progetti riguardanti il miglioramento della customer care",
            ),
            CardAction(
                type=ActionTypes.post_back,
                title="Dammi delle credentials di progetti di telco",
                value="Dammi delle credentials di progetti di telco",
            ),
            CardAction(
                type=ActionTypes.post_back,
                title="Di cosa si è parlato nel Town Hall del 19/12/2023?",
                value="Di cosa si è parlato nel Town Hall del 19/12/2023?",
            ),
            CardAction(
                type=ActionTypes.post_back,
                title="Quali sono le convenzioni e i benefit di Alkemy?",
                value="Quali sono le convenzioni e i benefit di Alkemy?",
            )
        ]
    )
    if "en" in locale:
        attachment = Attachment(
            content_type="application/vnd.microsoft.card.hero", content=en_card
        )
        await turn_context.send_activity(MessageFactory.attachment(attachment))
    else:
        attachment = Attachment(
            content_type="application/vnd.microsoft.card.hero", content=it_card
        )
        await turn_context.send_activity(MessageFactory.attachment(attachment))

async def send_feedback_card(turn_context: TurnContext) -> None:
    """Send a feedback card to the user."""
    card = HeroCard(
        # title="If you want, you can rate your experience",
        # text="Click on the thumbs to rate the answer.",
        buttons=[
            CardAction(type=ActionTypes.post_back, title="👍", value="thumbs_up"),
            CardAction(type=ActionTypes.post_back, title="👎", value="thumbs_down"),
        ],
    )
    attachment = Attachment(
        content_type="application/vnd.microsoft.card.hero", content=card
    )
    await turn_context.send_activity(MessageFactory.attachment(attachment))
