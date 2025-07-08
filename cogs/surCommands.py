from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CooldownMapping, BucketType

import os
import json

INFRACTIONS_FILE = "data/infractions.json"

class SurCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # cooldown : 1 fois tous les 10 secondes par utilisateur
        self.cooldowns = CooldownMapping.from_cooldown(1, 10, BucketType.user)

    ########
    # LOGS #
    ########
    @app_commands.command(name="logs", description="Voir les derniers logs de modération")
    async def logs(self, interaction: discord.Interaction):
        try:
            with open("mod_logs.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            await interaction.response.send_message("Aucun fichier de logs trouvé.", ephemeral=True)
            return
        
        # On garde les 10 dernières lignes max
        recent_logs = lines[-10:]
        logs_text = "".join(recent_logs)
        
        embed = discord.Embed(title="Derniers logs de modération", color=0x3498db)
        if logs_text.strip() == "":
            embed.description = "Aucun log à afficher."
        else:
            # Pour que ça rentre bien, on limite à 4000 caractères (max Discord)
            embed.description = logs_text[:4000]
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    #################
    # SCAN MESSAGES #
    #################
    @app_commands.command(name="scan_messages", description="Scanner les messages récents contenant un mot.")
    @app_commands.describe(mot="Mot ou expression à rechercher dans les messages")
    async def scan_messages(self, interaction: discord.Interaction, mot: str):
        # Vérification des permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)  # Pour éviter le timeout (affiche "pensée...")

        channel = interaction.channel
        found = []

        async for message in channel.history(limit=100):
            if mot.lower() in message.content.lower():
                found.append(f"**{message.author}**: {message.content[:100]}")

        if found:
            content = "\n".join(found[:10])  # Limite pour éviter les messages trop longs
            await interaction.followup.send(f"🔍 Messages contenant **{mot}** :\n{content}", ephemeral=True)
        else:
            await interaction.followup.send(f"Aucun message récent ne contient le mot **{mot}**.", ephemeral=True)

    ##############
    # CHECK USER #
    ##############
    @app_commands.command(name="check_user", description="Voir les infos modération d’un membre.")
    @app_commands.describe(user="Le membre à examiner")
    async def check_user(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=True)

        # Récupérer les rôles sauf @everyone
        roles = [role.mention for role in user.roles if role != interaction.guild.default_role]
        roles_display = ", ".join(roles) if roles else "Aucun rôle"

        # Récupérer le nombre d'infractions
        warnings = self.get_user_warnings(user.id, interaction.guild.id)

        # Créer l'embed
        embed = discord.Embed(
            title=f"🔎 Infos sur {user.display_name}",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.add_field(name="📅 Arrivé le", value=user.joined_at.strftime('%d/%m/%Y'), inline=True)
        embed.add_field(name="🏷️ Rôles", value=roles_display, inline=False)
        embed.set_footer(text=f"Requête faite par {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed, ephemeral=True)

    def get_user_warnings(self, user_id: int, guild_id: int) -> int:
        if not os.path.exists(INFRACTIONS_FILE):
            return 0
        with open(INFRACTIONS_FILE, "r") as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        user_data = guild_data.get(str(user_id), [])
        return len(user_data)
    
    ##############
    # PING CHECK #
    ##############
    @app_commands.command(name="ping_check", description="Vérifier la latence du bot.")
    async def ping_check(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convertit en ms
        embed = discord.Embed(
            title="Réponse Ping Check !",
            description=f"Latence : **{latency} ms**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(SurCommands(bot))