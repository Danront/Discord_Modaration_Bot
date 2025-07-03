import discord
from discord.ext import commands
from discord import app_commands

class CommandesUtiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Test de latence")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong !")

async def setup(bot):
    await bot.add_cog(CommandesUtiles(bot))
