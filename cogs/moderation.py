from discord.ext import commands
import discord
from discord import app_commands

import re
import time
from collections import defaultdict, deque

import asyncio
import json
import os

BLACKLIST_FILE = "black_list.json"

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_words = self.load_blacklist()
        self.message_logs = defaultdict(lambda: deque(maxlen=5))  # max 5 messages enregistrés par utilisateur
        self.antispam_enabled = True  # Par défaut activé
        self.suspicious_links_enabled = True  # Filtrage activé par défaut
        self.MAX_MSGS = 2
        self.INTERVAL = 2  # secondes

    def load_blacklist(self):
        try:
            if not os.path.exists(BLACKLIST_FILE):
                return []
            with open(BLACKLIST_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []

    def save_blacklist(self):
        with open(BLACKLIST_FILE, "w", encoding="utf-8") as file:
            json.dump(self.blacklisted_words, file, indent=4)

    def contains_blacklisted_word(self, content: str):
        content = content.lower()
        return any(word.lower() in content for word in self.blacklisted_words)

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
        if self.suspicious_links_enabled and self.contains_suspicious_link(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, lien suspect détecté.", delete_after=5)
            return

        # Anti-spam
        if self.antispam_enabled:
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
                    await asyncio.sleep(2)
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

        elif self.suspicious_links_enabled and self.contains_suspicious_link(after.content):
            await after.delete()
            await after.channel.send(f"{after.author.mention}, modification interdite détectée (lien suspect).", delete_after=5)

    #################
    # ADD BLACKLIST #
    #################
    @app_commands.command(name="blacklist_add", description="Ajouter un mot à la liste noire")
    @app_commands.describe(mot="Mot à ajouter à la blacklist")
    async def blacklist_add(self, interaction: discord.Interaction, mot: str):
        mot = mot.lower()

        if mot in self.blacklisted_words:
            await interaction.response.send_message(f"Le mot '{mot}' est déjà dans la blacklist.", ephemeral=True)
            return

        self.blacklisted_words.append(mot)
        self.save_blacklist()

        await interaction.response.send_message(f"Le mot '{mot}' a bien été ajouté à la blacklist.", ephemeral=True)

    ####################
    # REMOVE BLACKLIST #
    ####################
    @app_commands.command(name="blacklist_remove", description="Retirer un mot de la liste noire")
    @app_commands.describe(mot="Mot à retirer de la blacklist")
    async def blacklist_remove(self, interaction: discord.Interaction, mot: str):
        mot = mot.lower()

        if mot not in self.blacklisted_words:
            await interaction.response.send_message(f"Le mot '{mot}' n'est pas dans la blacklist.", ephemeral=True)
            return

        self.blacklisted_words.remove(mot)
        self.save_blacklist()

        await interaction.response.send_message(f"Le mot '{mot}' a été retiré de la blacklist.", ephemeral=True)

    ##################
    # LIST BLACKLIST #
    ##################
    @app_commands.command(name="blacklist_list", description="Afficher tous les mots de la liste noire")
    async def blacklist_list(self, interaction: discord.Interaction):
        if not self.blacklisted_words:
            await interaction.response.send_message("🚫 La blacklist est actuellement vide.", ephemeral=True)
            return

        mots = "\n".join(f"- {mot}" for mot in self.blacklisted_words)
        embed = discord.Embed(
            title="📄 Mots interdits",
            description=mots,
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    ####################
    # ANTI SPAM SWITCH #
    ####################
    @app_commands.command(name="antispam", description="Activer ou désactiver le filtre anti-spam")
    @app_commands.describe(state="État souhaité : on ou off")
    async def antispam_toggle(self, interaction: discord.Interaction, state: str):
        state = state.lower()
        if state not in ["on", "off"]:
            await interaction.response.send_message("❌ Utilisez `on` ou `off` uniquement.", ephemeral=True)
            return

        self.antispam_enabled = (state == "on")
        status = "✅ Activé" if self.antispam_enabled else "⛔ Désactivé"
        await interaction.response.send_message(f"🛡️ Anti-spam : {status}", ephemeral=True)

    ###########################
    # SUSPICIOUS LINKS SWITCH #
    ###########################
    @app_commands.command(name="suspicious_links", description="Activer ou désactiver le filtre de liens suspects")
    @app_commands.describe(state="État souhaité : on ou off")
    async def suspicious_links_toggle(self, interaction: discord.Interaction, state: str):
        state = state.lower()
        if state not in ["on", "off"]:
            await interaction.response.send_message("❌ Utilisez `on` ou `off` uniquement.", ephemeral=True)
            return

        self.suspicious_links_enabled = (state == "on")
        status = "✅ Activé" if self.suspicious_links_enabled else "⛔ Désactivé"
        await interaction.response.send_message(f"🔗 Filtre de liens suspects : {status}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))