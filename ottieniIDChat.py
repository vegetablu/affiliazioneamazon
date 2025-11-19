import asyncio
from telegram import Bot

# Legge il token dal file
def leggi_token(nome_file="token.txt"):
    try:
        with open(nome_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Errore: File {nome_file} non trovato!")
        print(f"Crea il file {nome_file} e inserisci il token del bot nella prima riga")
        exit(1)

TOKEN_BOT = leggi_token()

async def get_chat_id():
    bot = Bot(TOKEN_BOT)
    updates = await bot.get_updates()
    if updates:
        chat_id = updates[-1].message.chat_id
        print(f"La tua CHAT_DESTINAZIONE è: {chat_id}")
    else:
        print("Scrivi un messaggio al bot prima di eseguire questo script")

asyncio.run(get_chat_id())
