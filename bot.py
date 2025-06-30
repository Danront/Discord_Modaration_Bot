import discord
from discord.ext import commands

import re
import json
import random

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

XP_FILE = "xp_data.json"
LEVEL_ROLES = {
    5: "Actif",
    10: "Super Actif",
    20: "Légende"
}

XP_FILE = "xp_data.json"

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

     # -------- XP SYSTEM --------
    if msg.guild is None:  # message privé, on ignore
        return
    author = msg.author
    guild_id = str(msg.guild.id)
    user_id = str(author.id)

    # Initialisation si nouveau serveur ou utilisateur
    if guild_id not in xp_data:
        xp_data[guild_id] = {}
    if user_id not in xp_data[guild_id]:
        xp_data[guild_id][user_id] = {"xp": 0, "level": 0}

    # Gain d'XP (1 à 5 par message)
    gained_xp = random.randint(1, 5)
    xp_data[guild_id][user_id]["xp"] += gained_xp
    xp = xp_data[guild_id][user_id]["xp"]
    level = xp_data[guild_id][user_id]["level"]

    # Calcul du niveau (par exemple : 50 XP * niveau)
    next_level = level + 1
    required_xp = next_level * 50

    if xp >= required_xp:
        xp_data[guild_id][user_id]["level"] = next_level
        await msg.channel.send(f"🎉 Bravo {author.mention}, tu es monté au **niveau {next_level}** !")

        # Donne un rôle s’il correspond à ce niveau
        role_name = LEVEL_ROLES.get(next_level)
        if role_name:
            role = discord.utils.get(msg.guild.roles, name=role_name)
            if role:
                await author.add_roles(role)
                await msg.channel.send(f"🏅 {author.mention} a reçu le rôle **{role_name}** !")

    save_xp_data(xp_data)

#------------------------------------------------------------------------------------------------------------------------------------------#

@bot.event
async def on_message_edit(before, after):
    await moderation.on_edit(before, after, BLACKLIST, SUSPICIOUS_LINKS)
    
    
#------------------------------------------------------------------------------------------------------------------------------------------#

def load_xp_data():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp_data(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

xp_data = load_xp_data()
save_xp_data(xp_data)

@bot.tree.command(name="niveau", description="Voir ton niveau et ton XP")
async def niveau(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    if guild_id not in xp_data or user_id not in xp_data[guild_id]:
        await interaction.response.send_message("Tu n'as pas encore gagné d'XP ! Envoie des messages pour commencer. 🚀", ephemeral=True)
        return

    user_stats = xp_data[guild_id][user_id]
    xp = user_stats["xp"]
    level = user_stats["level"]
    next_level_xp = (level + 1) * 50

    await interaction.response.send_message(
        f"🔹 {interaction.user.mention} - Niveau **{level}**\n"
        f"🔸 XP : {xp} / {next_level_xp}",
        ephemeral=True
    )

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