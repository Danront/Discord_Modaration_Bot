import discord
from discord.ext import commands

import re
import asyncio

import os
from dotenv import load_dotenv

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
# channel is named "acceuil" is 1387801960866123827
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1387801960866123827)
    # Création de l'embed
    embed = discord.Embed(
        title=f"Bienvenue {member.name} !",
        description="Nous sommes ravis de vous compter parmi nous. Voici quelques informations utiles pour bien commencer :",
        color=discord.Color.blue()
    )

    # Ajout de champs à l'embed
    embed.add_field(
        name="À propos de l'association",
        value="Notre association a pour but de [décrire brièvement la mission de l'association].",
        inline=False
    )

    embed.add_field(
        name="Règles du serveur",
        value="""
            1. Respectez tous les membres.
            2. Pas de spam ou de publicité non autorisée.
            3. Utilisez les canaux appropriés pour vos messages.
            4. [Ajoutez d'autres règles spécifiques à votre serveur]
            """,
        inline=False
    )

    embed.add_field(
        name="Activités à venir",
        value="""
            - [Activité 1] : [Date et description]
            - [Activité 2] : [Date et description]
            - [Activité 3] : [Date et description]
            """,
        inline=False
    )

    # Ajout d'une image à l'embed (optionnel)
    # embed.set_image(url="URL_DE_L_IMAGE")

    # Ajout d'un pied de page à l'embed (optionnel)
    embed.set_footer(text="Bonne journée et amusez-vous bien ! 😊")

    # Envoi de l'embed
    await channel.send(embed=embed)


#------------------------------------------------------------------------------------------------------------------------------------------#
# Event for reacting to specific messages
@bot.event
async def on_message(msg: discord.Message):
    # Disable the capacity of the bots to trigger it self
    if msg.author.bot :
        return
    
    # Check spam : trop de messages en moins de 2s
    now = asyncio.get_event_loop().time()
    user_id = msg.author.id

    if user_id in user_message_times:
        elapsed = now - user_message_times[user_id]
        if elapsed < 1.5:
            await msg.delete()
            await msg.channel.send(f"{msg.author.mention}, pas de spam ici !", delete_after=5)
            return
    user_message_times[user_id] = now

    # Check innapropriet messages
    lower_msg = msg.content.lower()
    if any(bad_word in lower_msg for bad_word in BLACKLIST):
        await msg.delete()
        await msg.channel.send(f"{msg.author.mention}, ton message a été supprimé pour langage inapproprié.", delete_after=5)
        return

     # Check suspect link
    if SUSPICIOUS_LINKS.search(msg.content):
        await msg.delete()
        await msg.channel.send(f"{msg.author.mention}, les liens suspects sont interdits ici.", delete_after=5)
        return

#------------------------------------------------------------------------------------------------------------------------------------------#

@bot.event
async def on_message_edit(before, after):
    if after.author.bot:
        return

    lower_msg = after.content.lower()

    # Check contenu haineux
    if any(bad_word in lower_msg for bad_word in BLACKLIST):
        await after.delete()
        await after.channel.send(f"{after.author.mention}, ton message modifié a été supprimé pour langage inapproprié.", delete_after=5)
        return

    # Check lien suspect
    if SUSPICIOUS_LINKS.search(after.content):
        await after.delete()
        await after.channel.send(f"{after.author.mention}, les liens suspects sont interdits ici (même après modification).", delete_after=5)
        return
    
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