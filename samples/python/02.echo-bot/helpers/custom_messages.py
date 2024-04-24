

def get_en_welcome_message(user:str) -> str:
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


def get_it_welcome_message(user:str) -> str:
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
