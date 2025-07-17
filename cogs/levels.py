import discord
from discord.ext import commands
from discord import app_commands

import random
import json
import os

LEVEL_ROLES = {
    5: "Actif",
    10: "Super Actif",
    20: "Membre Actif"
}

XP_FILE = "json/xp_data.json"

def load_xp_data():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp_data(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def gain_xp():
    return random.randint(1, 5)

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_data = load_xp_data()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or not msg.guild:
            return

        guild_id = str(msg.guild.id)
        user_id = str(msg.author.id)

        self.xp_data.setdefault(guild_id, {})
        self.xp_data[guild_id].setdefault(user_id, {"xp": 0, "level": 0})

        gained = gain_xp()
        self.xp_data[guild_id][user_id]["xp"] += gained

        xp = self.xp_data[guild_id][user_id]["xp"]
        level = self.xp_data[guild_id][user_id]["level"]
        required = (level + 1) * 50

        if xp >= required:
            self.xp_data[guild_id][user_id]["level"] += 1
            new_level = self.xp_data[guild_id][user_id]["level"]
            await msg.channel.send(f"🎉 {msg.author.mention}, tu es monté au niveau **{new_level}** !")

            role_name = LEVEL_ROLES.get(new_level)
            if role_name:
                role = discord.utils.get(msg.guild.roles, name=role_name)
                if role:
                    await msg.author.add_roles(role)
                    await msg.channel.send(f"🏅 Tu as reçu le rôle **{role_name}** !")

        save_xp_data(self.xp_data)

    @app_commands.command(name="niveau", description="Voir ton niveau et ton XP")
    async def niveau(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        if guild_id not in self.xp_data or user_id not in self.xp_data[guild_id]:
            await interaction.response.send_message("Tu n'as pas encore gagné d'XP !", ephemeral=True)
            return

        user_stats = self.xp_data[guild_id][user_id]
        xp = user_stats["xp"]
        level = user_stats["level"]
        next_level_xp = (level + 1) * 50

        await interaction.response.send_message(
            f"🔹 Niveau **{level}** - XP : {xp}/{next_level_xp}", ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
