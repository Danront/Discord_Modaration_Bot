import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

# Reading of the .env in the folder
load_dotenv()

print("Lencement du bot...")
# Get the autorisation of the bot
bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())

# On the starting of the bot
@bot.event
async def on_ready():
    print("Bot allumé !")
    # Synchronise the commands with discord
    try:
        # Synchronisation
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(e)

# Event for reacting to specific messages
@bot.event
async def on_message(msg: discord.Message):
    # Disable the capacity of the bots to trigger it self
    if msg.author.bot :
        return

    # Simple test trigger message
    if msg.content.lower() == 'test' :
        # Send on the same channel
        channel = msg.channel
        await channel.send("Réponse au test ! ")

        # Send to the auther of the msg
        # author = msg.author
        # await author.send("Réponse au test ! ")

        # Send to a specific channel
        # channel is named "acceuil" is 1387801960866123827
        # welcome_channel = bot.get_channel(1387801960866123827)
        # await welcome_channel.send("Réponse au test ! ")

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