import discord
from discord.ext import commands

REACTION_ROLES = {
    "🎨": "Graphiste",
    "🧑‍🔧": "Développeur",
    "📢": "Communicant",
    "👨🏻‍💼": "Bosse"
}

TARGET_MESSAGE_ID = 0

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="rolesreactifs", description="Crée le message pour les rôles réactifs")
    async def roles_reactifs(self, interaction: discord.Interaction):
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

        for emoji in REACTION_ROLES:
            await msg.add_reaction(emoji)

        await interaction.response.send_message("Message envoyé avec succès !", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id != TARGET_MESSAGE_ID:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)
        role_name = REACTION_ROLES.get(emoji)
        role = discord.utils.get(guild.roles, name=role_name)

        if role and member:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != TARGET_MESSAGE_ID:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)
        role_name = REACTION_ROLES.get(emoji)
        role = discord.utils.get(guild.roles, name=role_name)

        if role and member:
            await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(Roles(bot))
