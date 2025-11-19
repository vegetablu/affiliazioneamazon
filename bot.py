import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from urllib.parse import urlparse, parse_qs
import re
import requests
import asyncio

# Legge il token dal file
def leggi_token(nome_file="token.txt"):
    try:
        with open(nome_file, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Errore: File {nome_file} non trovato!")
        print(f"Crea il file {nome_file} e inserisci il token del bot nella prima riga")
        exit(1)


# Configurazione da variabili d'ambiente
#TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TOKEN = leggi_token()
#AFFILIATE_TAG = os.getenv('AFFILIATE_TAG', 'bot3d-21')
AFFILIATE_TAG = "bot3d-21"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def expand_short_url(short_url: str) -> str:
    """Espande URL abbreviati"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(short_url, allow_redirects=True, timeout=15)
        final_url = response.url
        session.close()
        
        logger.info(f"URL espanso: {short_url} -> {final_url}")
        return final_url
        
    except Exception as e:
        logger.error(f"Errore espansione URL {short_url}: {e}")
        return short_url

def extract_product_id(url: str) -> str:
    """Estrae ID prodotto da URL Amazon"""
    try:
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:[/?]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        for param in ['asin', 'productID']:
            if param in params and re.match(r'^[A-Z0-9]{10}$', params[param][0], re.IGNORECASE):
                return params[param][0].upper()
                
        return None
    except Exception as e:
        logger.error(f"Errore estrazione ID: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi"""
    try:
        user_message = update.message.text
        if not user_message:
            await update.message.reply_text("Per favore invia un link Amazon valido")
            return

        urls = re.findall(r'https?://[^\s]+', user_message)
        
        if not urls:
            await update.message.reply_text("Nessun link trovato nel messaggio")
            return

        modified_links = []
        
        for url in urls:
            if not re.search(r'amazon\.|amzn\.(to|eu)', url.lower()):
                await update.message.reply_text(f"❌ {url} non è un link Amazon valido")
                continue
                
            expanded_url = url
            if 'amzn.' in url.lower():
                expanded_url = expand_short_url(url)
            
            product_id = extract_product_id(expanded_url)
            if not product_id:
                await update.message.reply_text(f"❌ Impossibile estrarre l'ID prodotto da: {url}")
                continue

            affiliate_url = f"https://www.amazon.it/dp/{product_id}?tag={AFFILIATE_TAG}"
            modified_links.append(affiliate_url)

        if modified_links:
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Impossibile cancellare messaggio: {e}")
            
            response = "✅ Link affiliato generato:\n\n" + "\n\n".join(modified_links)
            await update.message.reply_text(response)
            
    except Exception as e:
        logger.error(f"Errore in handle_message: {e}")
        try:
            await update.message.reply_text("❌ Si è verificato un errore durante l'elaborazione")
        except:
            pass

def main():
    """Avvia il bot"""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN non configurato!")
        return

    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("✅ Bot avviato correttamente su Railway!")
        logger.info("📱 Pronto a ricevere messaggi...")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Errore critico nell'avvio: {e}")

if __name__ == "__main__":
    main()
