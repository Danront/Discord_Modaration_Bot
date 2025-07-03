from discord.ext import commands
import discord
import re
import time
from collections import defaultdict, deque

import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_words = self.load_blacklist()
        self.message_logs = defaultdict(lambda: deque(maxlen=5))  # max 5 messages enregistrés par utilisateur
        self.MAX_MSGS = 2
        self.INTERVAL = 6  # secondes

    def load_blacklist(self):
        try:
            with open("blacklist.txt", "r", encoding="utf-8") as file:
                return [line.strip().lower() for line in file if line.strip()]
        except FileNotFoundError:
            return []

    def contains_blacklisted_word(self, content: str):
        content = content.lower()
        return any(word in content for word in self.blacklisted_words)

    def contains_suspicious_link(self, content: str):
        url_pattern = r'https?://[^\s]+'
        matches = re.findall(url_pattern, content.lower())
        return any("discord.gg" not in link and "example.com" not in link for link in matches)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Filtrage des mots interdits
        if self.contains_blacklisted_word(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, ton message contenait un mot interdit.", delete_after=5)
            return

        # Filtrage des liens suspects
        if self.contains_suspicious_link(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, lien suspect détecté.", delete_after=5)
            return

        # Anti-spam
        user_id = message.author.id
        now = time.time()
        self.message_logs[user_id].append(now)

        timestamps = self.message_logs[user_id]
        if len(timestamps) >= self.MAX_MSGS and (timestamps[-1] - timestamps[0]) < self.INTERVAL:
            try:
                await message.delete()
            except discord.HTTPException:
                print("Rate limit atteint lors de la suppression.")
            try:
                warn_msg = await message.channel.send(f"{message.author.mention}, attention au spam !")
                await asyncio.sleep(2)  # attend 2 secondes
                await warn_msg.delete()
            except Exception as e:
                print(f"Erreur lors de l'envoi du message d'avertissement : {e}")
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return

        if self.contains_blacklisted_word(after.content):
            await after.delete()
            await after.channel.send(f"{after.author.mention}, modification interdite détectée (mot blacklisté).", delete_after=5)

        elif self.contains_suspicious_link(after.content):
            await after.delete()
            await after.channel.send(f"{after.author.mention}, modification interdite détectée (lien suspect).", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))