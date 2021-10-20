from requests import post
from googletrans import Translator
from time import sleep
import re

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
    return desc_parse.replace("\n", "")

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
        } 
    }"""

def search(anime: str): # Buscar anime
    r = post("https://graphql.anilist.co", json = {"query": query, "variables": {"search": anime}})
    if r.status_code == 200:
        info = r.json()["data"]["Media"]
        return {"romanji": info["title"]["romaji"], "native": info["title"]["native"], "episodes": info["episodes"], "duration": info["duration"], "averageScore": info["averageScore"], "genres": [f"{gen}, " for gen in info["genres"]], "studios": [f"{studio}, " for studio in info["studios"]["nodes"]], "description": translator(parse(info["description"]))}
    else:
        print(f"Error {r.status_code}")