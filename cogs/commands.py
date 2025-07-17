# IMPORTS #
from datetime import timedelta
import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CooldownMapping, BucketType

import os
import json

# FILES REF #
INFRACTIONS_FILE = "json/infractions.json"
ANTI_RAID_FILE = "json/anti_raid.json"

# MAIN DEF #
def load_anti_raid():
    if not os.path.exists(ANTI_RAID_FILE):
        return {}
    with open(ANTI_RAID_FILE, "r") as f:
        return json.load(f)

def save_anti_raid(data):
    with open(ANTI_RAID_FILE, "w") as f:
        json.dump(data, f, indent=4)

# MAIN CLASSE #
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anti_raid_data = load_anti_raid()
        self.cooldowns = CooldownMapping.from_cooldown(1, 10, BucketType.user)


    ############################################################################################################
    # MODERATION                                                                                               #
    ############################################################################################################
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
                f"🔇 {user.mention} a été rendu muet pendant `{duration}`. Raison : {reason}",
                ephemeral=True  # <-- message visible uniquement par l'admin
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de rendre ce membre muet.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du mute : {e}", ephemeral=True)

    def parse_duration(self, duration_str: str):
        duration_str = duration_str.strip().lower()
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
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
            await member.timeout(None)
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

    ############################################################################################################
    # ANALYSE & SURVEILLANCE                                                                                   #
    ############################################################################################################
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

    ############################################################################################################
    # SECURITE                                                                                                 #
    ############################################################################################################
    ############
    # ANTIRAID #
    ############
    @app_commands.command(name="antiraid", description="Activer ou désactiver l'anti-raid.")
    @app_commands.describe(mode="on ou off pour gérer la protection anti-raid.")
    async def antiraid(self, interaction: discord.Interaction, mode: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        mode = mode.lower()
        guild_id = str(interaction.guild.id)

        if mode == "on":
            self.anti_raid_data[guild_id] = True
            save_anti_raid(self.anti_raid_data)
            await interaction.response.send_message("🛡️ Protection anti-raid **activée**.", ephemeral=True)

        elif mode == "off":
            self.anti_raid_data[guild_id] = False
            save_anti_raid(self.anti_raid_data)
            await interaction.response.send_message("⚠️ Protection anti-raid **désactivée**.", ephemeral=True)

        else:
            await interaction.response.send_message("❗ Utilise `on` ou `off`.", ephemeral=True)

    def is_antiraid_enabled(self, guild_id: int) -> bool:
        return self.anti_raid_data.get(str(guild_id), False)
    
    ############################################################################################################
    # INFORMATIONS                                                                                             #
    ############################################################################################################
    ###############
    # SERVER INFO #
    ###############
    @app_commands.command(name="serverinfo", description="Affiche les infos générales du serveur")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        owner = guild.owner or await guild.fetch_owner()
        created_at = guild.created_at.strftime('%d/%m/%Y')
        roles = len(guild.roles) - 1  # Exclut @everyone
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        members = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = members - bots

        embed = discord.Embed(
            title=f"📊 Informations sur {guild.name}",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Propriétaire", value=f"{owner} ({owner.id})", inline=True)
        embed.add_field(name="📅 Créé le", value=created_at, inline=True)
        embed.add_field(name="👥 Membres", value=f"Total : {members}\nHumains : {humans}\nBots : {bots}", inline=False)
        embed.add_field(name="💬 Textuels", value=text_channels, inline=True)
        embed.add_field(name="🔊 Vocaux", value=voice_channels, inline=True)
        embed.add_field(name="🏷️ Rôles", value=roles, inline=True)

        await interaction.response.send_message(embed=embed)

    #############
    # USER INFO #
    #############
    @app_commands.command(name="userinfo", description="Infos d’un membre (compte, rôles, etc.)")
    @app_commands.describe(user="Le membre à examiner")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=False)

        roles = [role.mention for role in user.roles if role != interaction.guild.default_role]
        joined = user.joined_at.strftime('%d/%m/%Y %H:%M') if user.joined_at else "Inconnu"
        created = user.created_at.strftime('%d/%m/%Y %H:%M')

        embed = discord.Embed(
            title=f"📋 Infos sur {user.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.add_field(name="📛 Nom d'utilisateur", value=str(user), inline=True)
        embed.add_field(name="📅 Créé le", value=created, inline=False)
        embed.add_field(name="📥 A rejoint le serveur", value=joined, inline=False)
        embed.add_field(name="🏷️ Rôles", value=", ".join(roles) if roles else "Aucun rôle", inline=False)
        embed.set_footer(text=f"Requête faite par {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

    #############
    # ROLE INFO #
    #############
    @app_commands.command(name="roleinfo", description="Infos sur un rôle spécifique")
    @app_commands.describe(role="Le rôle à examiner")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=False)

        embed = discord.Embed(
            title=f"📘 Infos sur le rôle : {role.name}",
            color=role.color
        )
        embed.add_field(name="🆔 ID", value=role.id, inline=True)
        embed.add_field(name="📛 Nom", value=role.name, inline=True)
        embed.add_field(name="🧱 Position", value=role.position, inline=True)
        embed.add_field(name="🔒 Mentionnable", value="Oui" if role.mentionable else "Non", inline=True)
        embed.add_field(name="🌐 Affiché séparément", value="Oui" if role.hoist else "Non", inline=True)
        embed.add_field(name="🎨 Couleur", value=str(role.color), inline=True)
        embed.add_field(name="👥 Nombre de membres", value=str(len(role.members)), inline=False)
        embed.set_footer(text=f"Créé le {role.created_at.strftime('%d/%m/%Y à %H:%M')}")

        await interaction.followup.send(embed=embed)

    ################
    # CHANNEL INFO #
    ################
    @app_commands.command(name="channelinfo", description="Infos sur le salon actuel")
    async def channel_info(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        channel = interaction.channel

        embed = discord.Embed(
            title=f"📺 Infos sur le salon : {channel.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="🆔 ID", value=channel.id, inline=True)
        embed.add_field(name="📁 Catégorie", value=channel.category.name if channel.category else "Aucune", inline=True)
        embed.add_field(name="🗣️ Type", value=str(channel.type).capitalize(), inline=True)
        embed.add_field(name="🔒 Salon privé", value="Oui" if isinstance(channel, discord.TextChannel) and not channel.permissions_for(channel.guild.default_role).read_messages else "Non", inline=True)
        embed.set_footer(text=f"Créé le {channel.created_at.strftime('%d/%m/%Y à %H:%M')}")

        await interaction.followup.send(embed=embed)

    ########
    # HELP #
    ########
    @app_commands.command(name="help", description="Afficher la liste des commandes disponibles")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Commandes disponibles",
            description="Voici les commandes triées par catégorie.",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🛡️ Modération Générale",
            value=(
                "/ban @user [raison] - Bannir un membre du serveur\n"
                "/unban user_id - Débannir un membre\n"
                "/kick @user [raison] - Expulser un membre\n"
                "/mute @user [durée] - Rendre muet un membre (timeout ou rôle)\n"
                "/unmute @user - Enlever le mute\n"
                "/warn @user [raison] - Avertir un membre\n"
                "/warnings @user - Afficher les avertissements d’un membre\n"
                "/clear [nombre] - Supprimer un certain nombre de messages\n"
                "/slowmode [secondes] - Activer/désactiver le mode lent d’un salon\n"
                "/lock - Fermer un salon textuel\n"
                "/unlock - Rouvrir un salon textuel\n"
            ),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Analyse & Surveillance",
            value=(
                "/logs - Voir les derniers logs de modération\n"
                "/scan_messages [mot] - Scanner les messages récents contenant un mot\n"
                "/check_user @user - Infos sur un membre (rôles, infractions, etc.)\n"
                "/ping_check - Vérifier la latence du bot\n"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Sécurité",
            value=(
                "/antiraid on|off - Activer ou désactiver la protection anti-raid\n"
                "/blacklist add [mot] - Ajouter un mot à la liste noire\n"
                "/blacklist remove [mot] - Retirer un mot de la liste noire\n"
                "/blacklist list - Afficher tous les mots interdits\n"
                "/antispam on|off - Activer ou désactiver le filtre anti-spam\n"
                "/suspicious_links on|off - Bloquer ou autoriser les liens suspects"
            ),
            inline=False
        )

        embed.add_field(
            name="❓ Informations",
            value=(
                "/serverinfo - Infos générales sur le serveur\n"
                "/userinfo @user - Infos d’un membre (compte, rôles, etc.)\n"
                "/roleinfo @role - Infos sur un rôle spécifique\n"
                "/channelinfo - Infos sur le salon actuel"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))