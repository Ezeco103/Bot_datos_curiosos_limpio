import os
import discord
from discord.ext import commands
import edge_tts
import requests

# Pega aquí tu token entre las comillas
TOKEN = "YOUR TOKEN HERE"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

VOICES = {
    "femenina": "es-MX-DaliaNeural",
    "masculina": "es-MX-JorgeNeural",
}
user_voices = {}


def traducir_a_espanol(texto):
    """Traduce texto del inglés al español usando MyMemory API."""
    url = (
        "https://api.mymemory.translated.net/get?"
        f"q={requests.utils.quote(texto)}&langpair=en|es"
    )
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()["responseData"]["translatedText"]
        return texto
    except Exception:
        return texto


def get_fact(cat="general"):
    """Obtiene un dato curioso aleatorio según la categoría indicada."""
    cat = cat.lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        if cat in ["historia", "history"]:
            url = "http://numbersapi.com/random/year?json"
            r = requests.get(url, headers=headers, timeout=5)
            text = r.json().get("text", "") if r.status_code == 200 else ""
        elif cat in ["ciencia", "math"]:
            url = "http://numbersapi.com/random/math?json"
            r = requests.get(url, headers=headers, timeout=5)
            text = r.json().get("text", "") if r.status_code == 200 else ""
        elif cat in ["gatos", "cat"]:
            r = requests.get("https://catfact.ninja/fact", timeout=5)
            text = r.json().get("fact", "") if r.status_code == 200 else ""
        else:
            text = ""

        if not text:
            fallback_url = "https://uselessfacts.jsph.pl/random.json"
            r = requests.get(fallback_url, timeout=5)
            text = (
                r.json().get("text", "")
                if r.status_code == 200
                else "Dato no disponible."
            )
        return traducir_a_espanol(text)
    except Exception:
        return "No se pudo obtener el dato curioso."


async def text_to_audio(text, filename, voice):
    """Convierte el texto recibido a un archivo de audio usando edge_tts."""
    await edge_tts.Communicate(text, voice, rate="-20%").save(filename)


@bot.command()
async def start(ctx):
    """Muestra un mensaje de bienvenida y los comandos disponibles."""
    await ctx.send(
        f"Hola {ctx.author.name}\nComandos:\n"
        "`!fact` [historia/ciencia/gatos/general]\n"
        "`!voz femenina` o `!voz masculina`"
    )


@bot.command()
async def voz(ctx, tipo: str = None):
    """Permite al usuario configurar el tipo de voz preferido."""
    if not tipo or tipo.lower() not in VOICES:
        return await ctx.send(
            "Usa: `!voz femenina` o `!voz masculina`."
        )
    user_voices[ctx.author.id] = VOICES[tipo.lower()]
    await ctx.send(f"Voz cambiada a **{tipo.lower()}**.")


@bot.command()
async def fact(ctx, cat: str = "general"):
    """Envía un dato curioso en texto y generado como audio de voz."""
    fact_text = get_fact(cat)
    voice = user_voices.get(ctx.author.id, VOICES["femenina"])
    filename = f"fact_{ctx.author.id}.mp3"
    try:
        await text_to_audio(fact_text, filename, voice)
        await ctx.send(
            f"**Dato ({cat.capitalize()}):** {fact_text}",
            file=discord.File(filename),
        )
    finally:
        if os.path.exists(filename):
            os.remove(filename)


@bot.event
async def on_ready():
    """Informa por consola cuando el bot se ha conectado con éxito."""
    print(f"Bot conectado como {bot.user}")


bot.run(TOKEN)
