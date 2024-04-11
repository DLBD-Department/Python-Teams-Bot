

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
