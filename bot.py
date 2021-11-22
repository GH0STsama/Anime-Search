from telethon import TelegramClient, Button
from telethon.events import NewMessage, StopPropagation
from telethon.utils import get_display_name
from requests import post, get
from json import loads
from googletrans import Translator
from re import sub
from os import getenv

try: # Intenta importar del secure.py para pruebas locales
    from secure import anime_bot
    api_id = int(anime_bot.api_id)
    api_hash = anime_bot.api_hash
    bot_token = anime_bot.bot_token
except: # Importar variables de entorno
    api_id = int(getenv("api_id"))
    api_hash = getenv("api_hash")
    bot_token = getenv("ANIME_BOT_TOKEN")

bot = TelegramClient("anime_bot", api_id, api_hash).start(bot_token = bot_token)

async def translator(trans: str) -> str: # Traductor de Darkness XD
    tr = Translator()
    cont = 0
    while cont < 10:
        try:
            return tr.translate(trans, dest = "es").text
        except Exception as e:
            print("translate error", e)
            cont += 1
    return trans

async def parse(desc: str) -> str: # Elimitar las etiquetas HTML de la descripcion
    desc_parse = sub("<.*?>", "", desc)
    return desc_parse.replace("\n", " ")

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

@bot.on(NewMessage(pattern = "/start"))
async def start(event):
    await bot.send_file(entity = event.sender_id, file = "./miku.jpg", caption = "<b>Miku:</b>\n\n"
    f'Hola <a href="tg://user?id={event.sender_id}">{get_display_name(await event.get_sender())}</a>, puedo buscar cualquier anime usando la API de anilist.\n\nUsa el comando /anime <code>nombre</code> para buscar info de algun anime', 
    parse_mode = "html", buttons  = [
        [Button.url("👻 Canal", "https://t.me/GhostOpenSource"), Button.url("💳 Donar", "https://qvapay.com/payme/ghostsama")],
        [Button.url("👾 GitHub", "https://github.com/GH0STsama/Anime-Search")]])

async def anime_search(anime: str) -> dict: # Realiza la busqueda
    r = post("https://graphql.anilist.co", json = {"query": query, "variables": {"search": anime}})
    info = loads(r.text)["data"]["Media"]
    if info != None:
        dicc = {
        "romanji": info["title"]["romaji"],
        "native": info["title"]["native"],
        "episodes": info["episodes"],
        "duration": info["duration"],
        "averageScore": info["averageScore"],
        "genres": [f"{await translator(gen)}" for gen in info["genres"]],
        "description": await translator(await parse(info["description"])),
        "imageSt": info["siteUrl"].replace("anilist.co/anime/", "img.anili.st/media/")
        }
        return dicc
    else:
        return None

@bot.on(NewMessage(pattern = "/anime")) # Buscar anime
async def anime_search_handler(event):
    if event.text:
        user = event.sender_id
        if len(event.text) >= 8 and str(event.text).startswith("/anime "):
            name = str(event.text)[7:]
            find = await anime_search(name)
            if find != None:
                response = get(find["imageSt"])
                with open(f"./{user}.png", "wb") as f:
                    f.write(response.content)
                gen = ""
                for genres in find["genres"]:
                    gen += genres + ", "
                await bot.send_file(entity = user, file = open(f"./{user}.png", "rb"), 
                caption = 
                f'<b>{find["romanji"]}</b> (<code>{find["native"]}</code>)\n\n'
                f'<b>Episodios: </b><code>{find["episodes"]}</code>\n'
                f'<b>Duración: </b><code>{find["duration"]} mins aprox. por ep.</code>\n'
                f'<b>Calificación: </b><code>{find["averageScore"]}\n</code>'
                f'<b>Géneros: </b><code>{gen[:-2]}</code>\n'
                f'\n<b>Descripción:</b>\n{find["description"]}', parse_mode = "html")
            else:
                await event.reply("No se encuentra el anime")
        else:
            await event.reply("Formato incorrecto, por favor use:\n\n/anime <nombre>")
    else:
        raise StopPropagation

print("Bot Iniciado!")
bot.run_until_disconnected()