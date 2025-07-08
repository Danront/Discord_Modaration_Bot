from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CooldownMapping, BucketType

import os
import json

class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # cooldown : 1 fois tous les 10 secondes par utilisateur
        self.cooldowns = CooldownMapping.from_cooldown(1, 10, BucketType.user)


    ########
    # PING #
    ########
    @app_commands.command(name="ping", description="Test de latence")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong !")

    #######
    # BAN #
    #######
    @app_commands.command(name="ban", description="Bannir un membre du serveur")
    @app_commands.describe(user="Le membre à bannir", reason="La raison du bannissement")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
            return
        
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"✅ {user} a été banni du serveur. Raison : {reason if reason else 'Aucune raison spécifiée'}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de bannir ce membre.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Une erreur est survenue lors du bannissement.", ephemeral=True)

    #########
    # UNBAN #
    #########
    @app_commands.command(name="unban", description="Débannir un membre du serveur via son ID")
    @app_commands.describe(user_id="L'ID du membre à débannir")
    async def unban(self, interaction: discord.Interaction, user_id: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
            return

        try:
            banned_users = await interaction.guild.bans()
            user = discord.utils.get(banned_users, user__id=user_id)
            if user is None:
                await interaction.response.send_message(f"❌ Aucun membre banni avec l'ID {user_id} trouvé.", ephemeral=True)
                return
            
            await interaction.guild.unban(user.user)
            await interaction.response.send_message(f"✅ {user.user} a été débanni du serveur.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de débannir ce membre.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Une erreur est survenue lors du débannissement.", ephemeral=True)

    ########
    # KICK #
    ########
    @app_commands.command(name="kick", description="Expulser un membre du serveur")
    @app_commands.describe(user="Le membre à expulser", reason="La raison de l'expulsion")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison fournie"):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
            return

        if user == interaction.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas vous expulser vous-même.", ephemeral=True)
            return

        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"✅ {user.mention} a été expulsé du serveur. Raison : {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission d'expulser ce membre.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'expulsion.", ephemeral=True)

    ########
    # MUTE #
    ########
    @app_commands.command(name="mute", description="Rendre muet un membre pendant une durée spécifiée")
    @app_commands.describe(user="Le membre à rendre muet", duration="Durée du mute (ex: 10m, 1h, 1d)", reason="Raison du mute")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "Aucune raison fournie"):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
            return

        if user == interaction.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas vous rendre muet vous-même.", ephemeral=True)
            return

        time_seconds = self.parse_duration(duration)
        if time_seconds is None:
            await interaction.response.send_message("❌ Durée invalide. Utilisez `10m`, `1h`, `2d`, etc.", ephemeral=True)
            return

        try:
            await user.timeout(timedelta(seconds=time_seconds), reason=reason)
            await interaction.response.send_message(
                f"🔇 {user.mention} a été rendu muet pendant `{duration}`. Raison : {reason}"
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de rendre ce membre muet.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du mute : {e}", ephemeral=True)

    def parse_duration(self, duration_str: str):
        duration_str = duration_str.strip().lower()
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        match = discord.utils.remove_markdown(duration_str)
        if duration_str[-1] in units and duration_str[:-1].isdigit():
            return int(duration_str[:-1]) * units[duration_str[-1]]
        return None
    
    ##########
    # UNMUTE #
    ##########
    @app_commands.command(name="unmute", description="Enlever le mute d'un membre.")
    @app_commands.describe(member="Le membre à démute")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(timeout=None)
            await interaction.response.send_message(f"{member.mention} a été démute.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission de démute ce membre.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}", ephemeral=True)

    ########
    # WARN #
    ########
    @app_commands.command(name="warn", description="Avertir un membre du serveur.")
    @app_commands.describe(member="Le membre à avertir", reason="Raison de l'avertissement")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        warnings_file = "warnings.json"

        # Charger warnings existants
        warnings = {}
        if os.path.exists(warnings_file):
            try:
                with open(warnings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        warnings = json.loads(content)
            except json.JSONDecodeError:
                warnings = {}

        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings:
            warnings[guild_id] = {}

        if user_id not in warnings[guild_id]:
            warnings[guild_id][user_id] = []

        warnings[guild_id][user_id].append({
            "mod_id": str(interaction.user.id),
            "reason": reason
        })

        with open(warnings_file, "w", encoding="utf-8") as f:
            json.dump(warnings, f, indent=4, ensure_ascii=False)

        # Essayer d'envoyer un DM au membre averti
        try:
            await member.send(f"Vous avez été averti sur le serveur **{interaction.guild.name}** pour la raison suivante : {reason}")
        except discord.Forbidden:
            # DM impossible (membre a désactivé les DMs)
            pass

        # Confirmer l'avertissement dans le serveur
        await interaction.response.send_message(
            f"{member.mention} a été averti pour : {reason}", ephemeral=True
        )
    

    ###########
    # WARNING #
    ###########
    @app_commands.command(name="warnings", description="Voir les avertissements d'un membre.")
    @app_commands.describe(member="Le membre à vérifier")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        warnings_file = "warnings.json"

        # Charger les avertissements
        warnings = {}
        if os.path.exists(warnings_file):
            try:
                with open(warnings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        warnings = json.loads(content)
            except json.JSONDecodeError:
                warnings = {}

        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings or user_id not in warnings[guild_id] or not warnings[guild_id][user_id]:
            await interaction.response.send_message(f"{member.mention} n'a aucun avertissement.", ephemeral=True)
            return

        user_warnings = warnings[guild_id][user_id]

        # Construire le message
        description = ""
        for i, w in enumerate(user_warnings, 1):
            mod_id = w.get("mod_id", "Inconnu")
            reason = w.get("reason", "Aucune raison fournie")
            description += f"**{i}.** Raison: {reason} \n"

        embed = discord.Embed(
            title=f"Avertissements de {member.display_name}",
            description=description,
            color=discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    #########
    # CLEAR #
    #########
    @app_commands.command(name="clear", description="Supprime un certain nombre de messages")
    @app_commands.describe(nombre="Nombre de messages à supprimer")
    async def clear(self, interaction: discord.Interaction, nombre: int):
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=nombre + 1)

        # Envoie la réponse
        msg = await interaction.followup.send(f"{len(deleted)} messages supprimés.", ephemeral=True)

        # Supprime le message après 5 secondes
        await msg.delete(delay=5)

    ############
    # SLOWMODE #
    ############
    @app_commands.command(name="slowmode", description="Définir le slowmode d'un salon (en secondes).")
    @app_commands.describe(delay="Temps en secondes (0 pour désactiver)")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, delay: int):
        try:
            await interaction.channel.edit(slowmode_delay=delay)
            if delay == 0:
                await interaction.response.send_message("Mode lent désactivé.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Mode lent activé : {delay} secondes.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}", ephemeral=True)

    ########
    # LOCK #
    ########
    @app_commands.command(name="lock", description="Fermer ce salon pour les membres.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        try:
            overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = False
            await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message("🔒 Salon verrouillé.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}", ephemeral=True)

    ##########
    # UNLOCK #
    ##########
    @app_commands.command(name="unlock", description="Réouvrir ce salon pour les membres.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        try:
            overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = True
            await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message("🔓 Salon réouvert.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModCommands(bot))
 