import discord
from discord.ext import commands
from discord import app_commands
import json
import os

ANTI_RAID_FILE = "anti_raid.json"

def load_anti_raid():
    if not os.path.exists(ANTI_RAID_FILE):
        return {}
    with open(ANTI_RAID_FILE, "r") as f:
        return json.load(f)

def save_anti_raid(data):
    with open(ANTI_RAID_FILE, "w") as f:
        json.dump(data, f, indent=4)


class SecCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anti_raid_data = load_anti_raid()

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

async def setup(bot):
    await bot.add_cog(SecCommands(bot))