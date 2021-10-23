from time import sleep
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from os import getenv, unlink
from anisearch import search
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

def parse_name(fname: str) -> str: # Caracteres invalidos
    fname = fname.replace("<", "")
    fname = fname.replace(":", "")
    fname = fname.replace(">", "")
    fname = fname.replace("/", "")
    fname = fname.replace("\\", "")
    fname = fname.replace("?", "")
    fname = fname.replace('"', "'")
    fname = fname.replace("|", " ")
    return fname

def document(update, context):
    name = update.effective_user.id
    f = context.bot.get_file(update.message.document.file_id)
    f.download(f"./{name}.txt")

    with open(f"./{name}.txt", "rb") as f:
        animes = f.read().decode().split("\r\n")

    text = ""
    for anime in animes:
        print(anime)
        anime_name = parse_name(anime)
        find, cover, banner, st = search(anime)
        text += find + ",\n"
        if not os.path.exists("./data/images"):
            os.makedirs("./data/images")
        img_cover = requests.get(cover)
        with open(f"./data/images/cover_{parse_name(anime)}." + cover.split(".")[-1], "wb") as f:
            f.write(img_cover.content)
        img_banner = requests.get(banner)
        with open(f"./data/images/banner_{parse_name(anime)}." + banner.split(".")[-1], "wb") as f:
            f.write(img_banner.content)
        img_st = requests.get(st)
        with open(f"./data/images/st_{parse_name(anime)}." + "png", "wb") as f:
            f.write(img_st.content)
        sleep(1)

    unlink(f"./{name}.txt")
    with open("./data/listado.py", "wb") as f:
       f.write(text.encode())

    fantasy_zip = zipfile.ZipFile('./archivo.zip', 'w')
    for folder, subfolders, files in os.walk('./data'):
        for file in files:
            fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), './data'), compress_type = zipfile.ZIP_DEFLATED)
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