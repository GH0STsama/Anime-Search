from time import sleep
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from os import getenv, unlink
import anisearch
import os
import zipfile

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

def document(update, context):
    name = update.effective_user.id
    id = update.message.document.file_id
    texto = ""
    f = context.bot.get_file(id)
    f.download(f"./{name}.txt")
    with open(f"./{name}.txt", "rb") as f:
        data = f.read().decode().split("\r\n")
    for anime in data:
        a = anisearch.search(anime)
        nombre = a["romanji"]
        coverImage = a["coverImage"]
        bannerImage = a["bannerImage"]
        imageSt = a["imageSt"]
        res_c = requests.get(coverImage)
        with open(f"./files/{nombre}.jpg", "wb") as f:
            f.write(res_c.content)
        res_b = requests.get(bannerImage)
        with open(f"./files/banner_{nombre}.jpg", "wb") as f:
            f.write(res_b.content)
        res_s = requests.get(imageSt)
        with open(f"./files/st_{nombre}.jpg", "wb") as f:
            f.write(res_s.content)
        sleep(1)
    unlink(f"./{name}.txt")
    with open("listado.py", "wb") as f:
        f.write(texto.encode())
    context.bot.send_document(document = open("./listado.py", "rb"), chat_id = name)
    unlink("listado.py")
    fantasy_zip = zipfile.ZipFile('./archivo.zip', 'w')
    for folder, subfolders, files in os.walk('./files'):
        for file in files:
            fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), './files'), compress_type = zipfile.ZIP_DEFLATED)
    fantasy_zip.close()
    context.bot.send_document(document = open("./archivo.zip", "rb"), chat_id = name)
    unlink("./archivo.zip")

updater = Updater(token = BOT_TOKEN, use_context = True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(filters = Filters.text , callback = messages))
dp.add_handler(MessageHandler(filters = Filters.document, callback = document))

updater.start_polling()
print("Bot Iniciado!")
updater.idle()