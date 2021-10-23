import requests
from googletrans import Translator
from time import sleep
import re
import os
import zipfile
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

def start(update, context):
    update.message.reply_text("running..")

def translator(texto: str) -> str: # Traductor de Darkness XD
    tr = Translator()
    cont = 0
    while cont < 5:
        try:
            return tr.translate(texto, dest = "es").text
        except Exception as e:
            print("search", e)
            cont += 1
            sleep(1)
    return texto

def parse(desc: str) -> str: # Elimitar las etiquetas HTML de la descripcion
    desc_parse = re.sub("<.*?>", "", desc)
    return desc_parse.replace("\n", " ")

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

query = """
    query ($id: Int, $search: String) 
    {   Media (id: $id, type: ANIME, search: $search) 
        {
            title {
                romaji
                native
                english
            }
            description (asHtml: false)
            startDate {
                year
            }
            episodes
            season
            format
            duration
            studios {
                nodes {
                    name 
                } 
            }
            genres
            averageScore
            coverImage {
                extraLarge
            }
            bannerImage
            siteUrl
        } 
    }"""

def search(anime: str): # Buscar anime
    r = requests.post("https://graphql.anilist.co", json = {"query": query, "variables": {"search": anime}})
    if r.status_code == 200:
        info = r.json()["data"]["Media"]
        coverImage = info["coverImage"]["extraLarge"]
        bannerImage = info["bannerImage"]
        imageSt = info["siteUrl"].replace("anilist.co/anime/", "img.anili.st/media/")
        studios = []
        for studio in info["studios"]["nodes"]:
            studios.append(studio["name"])
        dicc = {
        "romanji": info["title"]["romaji"],
        "native": info["title"]["native"],
        "english": info["title"]["english"],
        "episodes": info["episodes"],
        "duration": info["duration"],
        "averageScore": info["averageScore"],
        "genres": [f"{translator(gen)}" for gen in info["genres"]],
        "studios": studios,
        "description": translator(parse(info["description"])),
        "coverImage": coverImage,
        "bannerImage": bannerImage,
        "imageSt": imageSt,
        }
        return str(dicc), coverImage, bannerImage, imageSt
    else:
        print(f"Error {r.status_code}")

def process_files(update, context):
    name = update.effective_user.id
    file_id = update.message.document.file_id
    archivo = context.bot.get_file(file_id)
    archivo.download(f"./{name}")

    text = ""

    with open(f"./{name}", "rb") as f:
        animes = f.read().decode().split("\r\n")

    for anime in animes:
        try:
            print(f"start {anime}")
            anime_name = parse_name(anime)
            find, cover, banner, st = search(anime)
            text += find + ",\n"
            if not os.path.exists("./data"):
                os.makedirs("./data")
            img_cover = requests.get(cover)
            with open(f"./data/cover_{anime_name}." + cover.split(".")[-1], "wb") as f:
                f.write(img_cover.content)
            img_banner = requests.get(banner)
            with open(f"./data/banner_{anime_name}." + banner.split(".")[-1], "wb") as f:
                f.write(img_banner.content)
            img_st = requests.get(st)
            with open(f"./data/st_{anime_name}." + "png", "wb") as f:
                f.write(img_st.content)
            print(f"complete {anime}")
            sleep(1)
        except:
            print(f"error {anime}")

    with open("./data/listado.py", "wb") as f:
       f.write(text.encode())

    fantasy_zip = zipfile.ZipFile('./archivo.zip', 'w')
    for folder, subfolders, files in os.walk('./data'):
        for file in files:
            fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), './data'), compress_type = zipfile.ZIP_DEFLATED)
    fantasy_zip.close()
    context.bot.send_document(document = open("./archivo.zip", "rb"), chat_id = name)

updater = Updater(token = BOT_TOKEN, use_context = True)
dp = updater.dispatcher
dp.add_handler(CommandHandler('start', start))
dp.add_handler(MessageHandler(Filters.document, process_files))

updater.start_polling()
print("Bot Iniciado!")
updater.idle()
