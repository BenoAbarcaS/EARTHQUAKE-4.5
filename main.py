import discord
from discord.ext import commands, tasks
from discord import Intents
import requests
import json
import asyncio
from config import TOKEN

# Definir los intents que necesitas para tu bot
intents = discord.Intents.all()
intents.members = True


# Inicializar el bot con los intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Lista para mantener un registro de los terremotos ya enviados
sent_quakes = []

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    # Verificar si el bot está en al menos un servidor (gremio)
    if bot.guilds:
        # Obtener el ID del canal de mensajes del sistema del primer servidor (gremio)
        system_channel_id = bot.guilds[0].system_channel.id
        # Iniciar el loop que consulta la URL cada minuto
        check_quakes.start(system_channel_id)
    else:
        print("El bot no está en ningún servidor (gremio).")

# Función para obtener datos de los terremotos en Chile y enviarlos como mensaje en Discord
async def send_earthquake_data(channel_id):
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for feature in data['features']:
            # Verificar si el terremoto ya ha sido enviado
            if feature not in sent_quakes:
                place = feature['properties']['place']
                mag = feature['properties']['mag']
                await bot.get_channel(channel_id).send(f'Place: {place}, Magnitude: {mag}')
                # Agregar el terremoto al registro de terremotos enviados
                sent_quakes.append(feature)
    else:
        print(f"Error: {response.status_code}")

# Función que se ejecuta cada minuto para verificar nuevos terremotos
@tasks.loop(minutes=1)
async def check_quakes(channel_id):
    await send_earthquake_data(channel_id)

# Iniciar el bot con el token de autenticación
bot.run(TOKEN)
