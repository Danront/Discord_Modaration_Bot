import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def welcoming_message(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="accueil")
        if channel:
            embed = discord.Embed(
                title="Bienvenue INTERA-BOT !",
                description=(
                    "Nous sommes ravis de vous compter parmi nous. Voici quelques informations utiles pour bien commencer :"
                ),
                color=discord.Color.blue()
            )

            embed.add_field(
                name="À propos de l'association",
                value="Notre association a pour but de [décrire brièvement la mission de l'association].",
                inline=False
            )
            embed.add_field(
                name="Règles du serveur",
                value=(
                    "- Respectez tous les membres.\n"
                    "- Pas de spam ou de publicité non autorisée.\n"
                    "- Utilisez les canaux appropriés pour vos messages.\n"
                    "- [Ajoutez d'autres règles spécifiques à votre serveur]"
                ),
                inline=False
            )
            embed.add_field(
                name="Activités à venir",
                value=(
                    "- [Activité 1] : [Date et description]\n"
                    "- [Activité 2] : [Date et description]\n"
                    "- [Activité 3] : [Date et description]"
                ),
                inline=False
            )
            embed.set_footer(text="Bonne journée et amusez-vous bien ! 😊")
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.welcoming_message(member)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
