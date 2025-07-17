import discord
from discord.ext import commands

REACTION_ROLES = {
    "✍": "Stagiaire",
    "🙋‍♂️": "Bénévole",
    
    "📢": "Finance",
    "🗣️": "Communication",
    "🧑‍🤝‍🧑": "RH",
    "🤝": "Partenariats",
    "🎓": "Formation",
    "🤖": "IA",
    "📁": "Projets",
    "💙": "HandiSD",
    "✨": "Fantasia",
    "🗼": "Antenne Paris",
    "🌄": "Antenne Montpellier",

    "👤": "Membre DSD" 
}

TARGET_MESSAGE_ID = 0

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="rolesreactifs", description="Crée le message pour les rôles réactifs")
    async def roles_reactifs(self, interaction: discord.Interaction):
        global TARGET_MESSAGE_ID

        await interaction.response.defer(ephemeral=True)  # déférer la réponse pour éviter timeout

        channel = self.bot.get_channel(interaction.channel_id)
        if channel is None:
            await interaction.followup.send("Impossible d'accéder au channel.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎭 Choisissez vos rôles",
            description="Cliquez sur une réaction pour obtenir un rôle. Cliquez à nouveau pour le retirer.",
            color=discord.Color.green()
        )

        for emoji, role in REACTION_ROLES.items():
            embed.add_field(name=role, value=f"Réagissez avec {emoji}", inline=False)

        msg = await channel.send(embed=embed)
        TARGET_MESSAGE_ID = msg.id

        for emoji in REACTION_ROLES:
            await msg.add_reaction(emoji)

        await interaction.followup.send("Message envoyé avec succès !", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id != TARGET_MESSAGE_ID:
            return

        # Ignorer les réactions du bot lui-même
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        emoji = str(payload.emoji)
        role_name = REACTION_ROLES.get(emoji)
        if role_name is None:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            return

        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Erreur lors de l'ajout du rôle: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != TARGET_MESSAGE_ID:
            return

        # Ignorer les réactions du bot lui-même
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        emoji = str(payload.emoji)
        role_name = REACTION_ROLES.get(emoji)
        if role_name is None:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            return

        try:
            await member.remove_roles(role)
        except Exception as e:
            print(f"Erreur lors de la suppression du rôle: {e}")

async def setup(bot):
    await bot.add_cog(Roles(bot))
