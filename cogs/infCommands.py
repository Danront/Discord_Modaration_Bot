from discord.ext import commands
from discord import app_commands
import discord
import datetime

class InfCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(InfCommands(bot))
