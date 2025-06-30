import asyncio
import re
import os

from dotenv import load_dotenv

import moderation

#------------------------------------------------------------------------------------------------------------------------------------------#

def load_blacklist():
    path = "blacklist.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            blacklist = [line.strip().lower() for line in f if line.strip()]
        print(f"Blacklist chargée ({len(blacklist)} mots)")
    else:
        print("Error : Fichier blacklist.txt introuvable.")
        blacklist = []
    return blacklist

# Regex for detectiong suspected links
SUSPICIOUS_LINKS = re.compile(r"(https?:\/\/)?(www\.)?(grabify|iplogger|bit\.ly|goo\.gl|discord\.gift\/[^/]+)")

# Anti-spam
user_message_times = {}

#------------------------------------------------------------------------------------------------------------------------------------------#

async def on_send(msg, BLACKLIST, SUSPICIOUS_LINKS, user_message_times):
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

async def on_edit(before, after, BLACKLIST, SUSPICIOUS_LINKS):
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