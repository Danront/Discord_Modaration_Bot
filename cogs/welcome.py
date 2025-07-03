import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def welcoming_message(self, member, bot):
        channel = discord.utils.get(member.guild.text_channels, name="accueil")
        if channel:
            await channel.send(f"👋 Bienvenue {member.mention} sur le serveur !")

@commands.Cog.listener()
async def on_member_join(member):
    cog = member.guild.get_cog("Welcome")
    if cog:
        await cog.welcoming_message(member, cog.bot)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
