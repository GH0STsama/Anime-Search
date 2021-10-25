import requests
from googletrans import Translator
from time import sleep
import re
import os
import zipfile
from telethon import TelegramClient, events, utils

# Importar las variables de entorno
BOT_TOKEN = os.getenv("BOT_TOKEN")
api_hash = os.getenv("api_hash")
api_id = int(os.getenv("api_id"))
bot_master = int(os.getenv("bot_master"))

bot = TelegramClient("alice", api_id, api_hash, request_retries = 10, flood_sleep_threshold = 120).start(bot_token = BOT_TOKEN)

@bot.on(events.NewMessage(pattern = "/start")) # Comando start
async def start(event):
    if event.text:
        sender = await event.get_sender()
        name = utils.get_display_name(sender)
        await event.reply(f"running..")
    raise events.StopPropagation

def translator(trans: str) -> str: # Traductor de Darkness XD
    tr = Translator()
    cont = 0
    while cont < 10:
        try:
            return tr.translate(trans, dest = "es").text
        except Exception as e:
            print("translate error", e)
            cont += 1
            sleep(2)
    return trans

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

# query para la consulta de la informacion en la api de anilist, graphql
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

def search(anime: str) -> str: # Buscar anime
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

@bot.on(events.NewMessage(from_users = bot_master)) # Procesa los documentos que le envie el bot master
async def process_file(event):
    if event.document:
        event.reply("procesando...")
        await event.download_media("./animes.file")

        text = ""

        with open("./animes.file", "rb") as f:
            animes = f.read().decode().split("\n")

        for anime in animes:
            anime = anime.replace("\r", "").replace("\n", "")
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
        await bot.send_file(entity = bot_master, file = open("./archivo.zip", "rb"))

    else:
        raise events.StopPropagation

try:
    print("Bot Iniciado!")
    bot.run_until_disconnected()
finally:
    bot.disconnect()
