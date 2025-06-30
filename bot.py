import discord
from discord.ext import commands

import re

import os
from dotenv import load_dotenv

import moderation
import welcome

# Reading of the .env in the folder
load_dotenv()

# Instance
bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())

#------------------------------------------------------------------------------------------------------------------------------------------#

# blacklist for modération
BLACKLIST = []

def load_blacklist():
    global BLACKLIST
    path = "blacklist.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            BLACKLIST = [line.strip().lower() for line in f if line.strip()]
        print(f"Blacklist chargée ({len(BLACKLIST)} mots)")
    else:
        print("Error : Fichier blacklist.txt introuvable.")
        BLACKLIST = []

# Regex for detectiong suspected links
SUSPICIOUS_LINKS = re.compile(r"(https?:\/\/)?(www\.)?(grabify|iplogger|bit\.ly|goo\.gl|discord\.gift\/[^/]+)")

# Anti-spam
user_message_times = {}

#------------------------------------------------------------------------------------------------------------------------------------------#

# On the starting of the bot
@bot.event
async def on_ready():
    load_blacklist()
    
    print("Bot is strarted !")
    
    # Synchronise the commands with discord
    try:
        # Synchronisation
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(e)
        
#------------------------------------------------------------------------------------------------------------------------------------------#

# Welcoming function
@bot.event
async def on_member_join(member):
   await welcome.welcoming_message(member, bot)


#------------------------------------------------------------------------------------------------------------------------------------------#
# Event for reacting to specific messages
@bot.event
async def on_message(msg: discord.Message):
    await moderation.on_send(msg, BLACKLIST, SUSPICIOUS_LINKS, user_message_times)

#------------------------------------------------------------------------------------------------------------------------------------------#

@bot.event
async def on_message_edit(before, after):
    await moderation.on_edit(before, after, BLACKLIST, SUSPICIOUS_LINKS)
    
    
#------------------------------------------------------------------------------------------------------------------------------------------#

# Event for reacting to commands
@bot.tree.command(name="commandtest", description="Command pour tester la fonction des commands")
async def commandTest(interaction: discord.Interaction):
    await interaction.response.send_message("Réponse au commands TEST !!!")

# Send messages Embed
@bot.tree.command(name="embedtest", description="Commends TEST des Embeds")
async def warnguy(interaction: discord.Interaction):
    embed = discord.Embed(
        title="TEST Title",
        description="Description de l'embed",
        color=discord.Color.blue()
    )

    embed.add_field(name="TEST", value="TESTING n°1")
    embed.add_field(name="TESTING", value="TESTING n°2")

    await interaction.response.send_message(embed=embed)


# Envoie de Warning
@bot.tree.command(name="warnguy", description="Alerter une personne")
async def warnguy(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message("Alerte envoyé !")
    await member.send("Test de WARNING !!!")

# Bannir une personne
@bot.tree.command(name="banguy", description="Bannir une personne")
async def warnguy(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message("Ban envoyé !")
    await member.ban(reason="TEST BAN")
    await member.send("Test de BAN !!!")

# Loading (running) the bot
# DISCORD_TOKEN in the .env
bot.run(os.getenv('DISCORD_TOKEN'))