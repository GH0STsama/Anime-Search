import requests
from googletrans import Translator
from time import sleep

def traducir(texto: str) -> str: # Traductor de Darkness XD
    tr = Translator()
    cont = 0
    while cont < 5:
        try:
            return tr.translate(texto, dest = "es").text
        except Exception as e:
            print('search', e)
            cont += 1
            tr = Translator()
            sleep(1)
    return texto

anime_query = '''
   query ($id: Int,$search: String) { 
      Media (id: $id, type: ANIME,search: $search) { 
        id
        idMal
        title {
          romaji
          english
          native
        }
        description (asHtml: false)
        startDate{
            year
          }
          episodes
          season
          type
          format
          status
          duration
          siteUrl
          studios{
              nodes{
                   name
              }
          }
          trailer{
               id
               site 
               thumbnail
          }
          averageScore
          genres
          bannerImage
      }
    }
'''

def get_elements(json) -> str:
    name = f"{json['title']['romaji']}"
    native = f"{json['title']['native']}"
    capts = f"{json.get('episodes', 'N/A')}"
    duracion = f"{json.get('duration', 'N/A')}"
    score =  f"{json['averageScore']}"
    generos = ""
    for x in json['genres']:
        generos += f"{x}, "
    studios = ""
    for x in json['studios']['nodes']:
        studios += f"{x['name']}, "
    info = json.get('description', 'N/A').replace('<i>', '').replace('</i>', '').replace('<br>', '')
    return name, native, capts, duracion, score, generos, studios, info

def search(anime: str) -> dict:
    variables = {'search': anime}
    res = requests.post("https://graphql.anilist.co", 
    json = {"query": anime_query, "variables": variables}).json()["data"].get("Media", None)
    if res:
        name, native, capts, duracion, score, generos, studios, info = get_elements(res)
        info_trad = traducir(info)
        generos_trad = traducir(generos[:-2])
    return {"Nombre": name, "Nativo": native, "Capitulos": capts, "Duracion": duracion, "Puntuacion": score, "Generos": generos_trad, "Estudios": studios[:-2], "Descripcion": info_trad.replace("\n", " ").replace("\n\n", " ")}
