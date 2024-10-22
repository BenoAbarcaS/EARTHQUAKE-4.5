import discord
from discord.ext import commands, tasks
from selenium import webdriver
import requests
import sqlite3
import time
import os
import webserver

# Obtener el token desde las variables de entorno
TOKEN = os.getenv('TOKEN')

# Inicializar el bot
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Obtener la ruta absoluta del directorio actual
current_directory = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_directory, 'server_config.db')

# Conectar a la base de datos SQLite
conn = sqlite3.connect(database_path)
c = conn.cursor()

try:
    # Crear la tabla solo si la base de datos no existe
    c.execute('''CREATE TABLE IF NOT EXISTS server_config (
                 server_id INTEGER PRIMARY KEY,
                 channel_id INTEGER,
                 eqlast TEXT DEFAULT NULL,
                 eqplace TEXT DEFAULT NULL,
                 eqmag TEXT DEFAULT NULL
                 )''')
    conn.commit()
except sqlite3.Error as e:
    print("Error al crear la tabla:", e)

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
        place = data['properties']['place']
        coordinates = data['geometry']['coordinates']
        longitude = coordinates[0]
        latitude = coordinates[1]
        
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
                    
                    # Crear una instancia del navegador
                    options = webdriver.ChromeOptions()
                    options.add_argument('headless')  # Para que no se abra la ventana del navegador
                    driver = webdriver.Chrome(options=options, executable_path='/usr/local/bin/chromedriver')  # Especifica la ruta de ChromeDriver
                    
                    # Abrir Google Maps y obtener la captura de pantalla
                    google_maps_link = f"http://maps.google.com/maps?t=k&q=loc:{latitude}+{longitude}"  # Agregar el parámetro para mostrar la vista de satélite
                    driver.get(google_maps_link)
                    time.sleep(4)
                    driver.execute_script("document.getElementsByClassName('widget-scene-canvas')[0].style.transform = 'translateX(0%)'")
                    time.sleep(1)
                    driver.save_screenshot("map_screenshot.png")
                    
                    file = discord.File("map_screenshot.png", filename="map_screenshot.png")
                    embed = discord.Embed(title="Alerta de Terremoto", description=f"**{place}**\nMagnitud: {mag}", color=discord.Color.red())
                    embed.set_thumbnail(url="https://cdn3.iconfinder.com/data/icons/volcano-and-earthquake/512/earthquake-512.png")
                    embed.add_field(name="Para más detalles:", value=f"[Ver en Google Maps]({google_maps_link})")
                    embed.set_image(url="attachment://map_screenshot.png")  # Adjuntar la imagen al campo
                    await channel.send(embed=embed, file=file)
                    
                    # Actualizar el último título enviado (eqlast) en la base de datos
                    c.execute("UPDATE server_config SET eqlast=? WHERE server_id=?", (title, server_id))
                    conn.commit()
                    
                    # Cerrar el navegador después de tomar la captura de pantalla
                    driver.quit()  # Asegúrate de cerrar el navegador

# Comando para establecer el filtro de eqplace de un servidor
@bot.command()
async def eqplace(ctx, *, eqplace_filter: str = None):
    server_id = ctx.guild.id
    if eqplace_filter is None or eqplace_filter == '0':
        eqplace_filter = None  # Si no se proporciona filtro o se proporciona "0", se establece como None
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
        eqmag_filter = None  # Si no se proporciona filtro o se proporciona "0", se establece como None
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

# mantener el servidor
webserver.keep_alive()
# Inicializar el bot
bot.run(TOKEN)
