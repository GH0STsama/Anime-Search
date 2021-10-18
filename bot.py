from telegram.ext import Updater, CommandHandler, MessageHandler , Filters
from os import getenv

try:
    from secure import animebot
    BOT_TOKEN = animebot.bot_token
except ImportError:
    BOT_TOKEN = getenv("BOT_TOKEN")

def start(update, context):
      update.message.reply_text("Hola, soy un bot para buscar animes.")

def messages(update, context):
    text: str = update.message.text
    size = len(text)
    if text.startswith("/anime"):
        if text.startswith("/anime ") and size >= 8:
            update.message.reply_text("😭 Aun no puedo buscar animes.")
        elif text == "/anime":
            update.message.reply_text("Formato invalido, por favor introduzca:\n/anime <nombre>")
    else:
        pass

updater = Updater(token = BOT_TOKEN, use_context = True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(filters = Filters.text , callback = messages))

updater.start_polling()
print("Bot Iniciado!")
updater.idle()