import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Bot Help",
            description="Here are all the available commands:",
            color=discord.Color.blurple()
        )

        for cog in self.bot.cogs.values():
            command_list = cog.get_app_commands()
            if command_list:
                value = "\n".join(f"/{cmd.name} - {cmd.description}" for cmd in command_list)
                embed.add_field(name=f"📂 {cog.__class__.__name__}", value=value, inline=False)

        embed.set_footer(text="Use /command_name to execute a command.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
