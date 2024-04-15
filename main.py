from config import TOKEN
import discord
from discord.ext import commands, tasks
import requests
import json
import sqlite3
import os

# Inicializar el bot
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('server_config.db')
c = conn.cursor()

# Verificar si la base de datos ya existe
if not os.path.isfile('server_config.db'):
    # Crear la tabla solo si la base de datos no existe
    c.execute('''CREATE TABLE IF NOT EXISTS server_config (
                 server_id INTEGER PRIMARY KEY,
                 channel_id INTEGER,
                 eqlast TEXT DEFAULT NULL,
                 eqplace TEXT DEFAULT NULL,
                 eqmag TEXT DEFAULT NULL
                 )''')
    conn.commit()


# Función para obtener el JSON de la URL
def get_earthquake_data():
    response = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson")
    data = response.json()
    if 'features' in data and data['features']:
        return data['features'][0]  # Obtener solo el primer elemento
    else:
        return None

# Función para enviar las alertas de terremotos
async def send_earthquake_alerts():
    data = get_earthquake_data()
    if data:
        title = data['properties']['title']
        mag = data['properties']['mag']
        rows = c.execute("SELECT * FROM server_config").fetchall()
        for row in rows:
            server_id, channel_id, eqlast, eqplace, eqmag = row
            guild = bot.get_guild(server_id)
            channel = guild.get_channel(channel_id)
            if channel:
                # Comprobar si el título es diferente al último enviado (eqlast),
                # cumple con el filtro eqplace y cumple con el filtro eqmag
                if (not eqlast or title != eqlast) and \
                   (not eqplace or eqplace.lower() in title.lower()) and \
                   (not eqmag or (eqmag.isdigit() and float(mag) >= float(eqmag))):
                    await channel.send(f"**Alerta de terremoto:** {title}")
                    # Actualizar el último título enviado (eqlast) en la base de datos
                    c.execute("UPDATE server_config SET eqlast=? WHERE server_id=?", (title, server_id))
                    conn.commit()

# Comando para establecer el filtro de eqplace de un servidor
@bot.command()
async def eqplace(ctx, *, eqplace_filter: str = None):
    server_id = ctx.guild.id
    if eqplace_filter is None:
        eqplace_filter = "NULL"
        await ctx.send(f"Se ha borrado el filtro eqplace para este servidor.")
    else:
        await ctx.send(f"Filtro de eqplace actualizado para este servidor: {eqplace_filter}")
    c.execute("UPDATE server_config SET eqplace=? WHERE server_id=?", (eqplace_filter, server_id))
    conn.commit()

# Comando para establecer el filtro de eqmag de un servidor
@bot.command()
async def eqmag(ctx, *, eqmag_filter: str = None):
    server_id = ctx.guild.id
    if eqmag_filter is None or eqmag_filter == '0':
        eqmag_filter = "NULL"
        await ctx.send(f"Se ha borrado el filtro eqmag para este servidor.")
    else:
        await ctx.send(f"Filtro de eqmag actualizado para este servidor: {eqmag_filter}")
    c.execute("UPDATE server_config SET eqmag=? WHERE server_id=?", (eqmag_filter, server_id))
    conn.commit()

# Tarea programada para revisar el JSON cada 10 segundos
@tasks.loop(seconds=10)
async def check_earthquakes():
    await send_earthquake_alerts()

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    await update_server_config()
    check_earthquakes.start()

# Función para actualizar la configuración de todos los servidores
async def update_server_config():
    for guild in bot.guilds:
        server_id = guild.id
        channel_id = guild.system_channel.id if guild.system_channel else None
        c.execute("INSERT OR IGNORE INTO server_config (server_id, channel_id) VALUES (?, ?)", (server_id, channel_id))
    conn.commit()

# Inicializar el bot
bot.run(TOKEN)
