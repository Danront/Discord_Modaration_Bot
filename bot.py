import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

import keepAlive

# Chargement des variables d’environnement
load_dotenv()

# Préfixe et intentions
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Chargement des extensions
EXTENSIONS = [
    "cogs.moderation",
    "cogs.welcome",
    "cogs.levels",
    "cogs.roles",
    "cogs.commands",
    "cogs.help"
]

# Deamrage du bot (quand le bot est pret)
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"Erreur de sync : {e}")

# Chargement des extentions
@bot.event
async def setup_hook():
    for ext in EXTENSIONS:
        await bot.load_extension(ext)
    await bot.tree.sync()

#keep alive the server
keepAlive.keep_alive()

# Lancement du bot
bot.run(os.getenv("DISCORD_TOKEN"))