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


REACTION_ROLES = {
    "🎨": "Graphiste",
    "🧑‍🔧": "Développeur",
    "📢": "Communicant",
    "👨🏻‍💼": "Bosse"
}

# ID du message contenant les réactions à surveiller
TARGET_MESSAGE_ID = 1389159089937977364  # Remplace avec l’ID réel du message

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

# Interactive role
@bot.tree.command(name="rolesreactifs", description="Crée le message pour les rôles réactifs")
async def roles_reactifs(interaction: discord.Interaction):
    global TARGET_MESSAGE_ID

    embed = discord.Embed(
        title="🎭 Choisissez vos rôles",
        description="Cliquez sur une réaction pour obtenir un rôle. Cliquez à nouveau pour le retirer.",
        color=discord.Color.green()
    )

    for emoji, role in REACTION_ROLES.items():
        embed.add_field(name=role, value=f"Réagissez avec {emoji}", inline=False)

    msg = await interaction.channel.send(embed=embed)
    TARGET_MESSAGE_ID = msg.id

    # Ajouter les réactions
    for emoji in REACTION_ROLES:
        await msg.add_reaction(emoji)

    await interaction.response.send_message("Message envoyé avec succès !", ephemeral=True)

# Ajout de rôle
@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != TARGET_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    emoji = str(payload.emoji)
    role_name = REACTION_ROLES.get(emoji)
    if not role_name:
        return

    role = discord.utils.get(guild.roles, name=role_name)
    member = guild.get_member(payload.user_id)

    if role and member:
        await member.add_roles(role)
        print(f"{member.display_name} a reçu le rôle {role.name}")

# Suppression de rôle
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != TARGET_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    emoji = str(payload.emoji)
    role_name = REACTION_ROLES.get(emoji)
    if not role_name:
        return

    role = discord.utils.get(guild.roles, name=role_name)
    member = guild.get_member(payload.user_id)

    if role and member:
        await member.remove_roles(role)
        print(f"{member.display_name} a perdu le rôle {role.name}")

# Démarrage du bot
@bot.event
async def setup_hook():
    await bot.tree.sync()

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