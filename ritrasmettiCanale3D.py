import os
from telegram.ext import Application, MessageHandler, filters


# Legge il token dal file
def leggi_token(nome_file="token.txt"):
    try:
        with open(nome_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Errore: File {nome_file} non trovato!")
        print(f"Crea il file {nome_file} e inserisci il token del bot nella prima riga")
        exit(1)


# Legge la chat ID dal file (opzionale)
def leggi_chat_id(nome_file="chat_id.txt"):
    try:
        with open(nome_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


# Configurazione
CANALE_SORGENTE = "@offertetredi"
TOKEN_BOT = leggi_token()
CHAT_DESTINAZIONE = leggi_chat_id()

application = Application.builder().token(TOKEN_BOT).build()


async def inoltra_messaggio(update, context):
    try:
        # Usa la CHAT_DESTINAZIONE dal file, altrimenti usa la chat corrente
        chat_dest = CHAT_DESTINAZIONE or update.effective_chat.id

        await context.bot.forward_message(
            chat_id=chat_dest,
            from_chat_id=update.channel_post.chat.id,
            message_id=update.channel_post.message_id
        )
        print(f"Messaggio inoltrato a {chat_dest}")
    except Exception as e:
        print(f"Errore: {e}")


# Filtra i messaggi dal canale sorgente
application.add_handler(
    MessageHandler(filters.Chat(username=CANALE_SORGENTE) & filters.UpdateType.CHANNEL_POST, inoltra_messaggio))

if __name__ == "__main__":
    if CHAT_DESTINAZIONE:
        print(f"Bot in ascolto su canale {CANALE_SORGENTE}...")
        print(f"Messaggi verranno inoltrati a: {CHAT_DESTINAZIONE}")
    else:
        print("Chat destinazione non impostata. I messaggi verranno inoltrati alla chat corrente.")

    application.run_polling()
