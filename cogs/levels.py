import discord
from discord.ext import commands
from discord import app_commands

from discord.ext import tasks
from datetime import datetime, timedelta

import random
import json
import os
import time  # for timestamps

LEVEL_ROLES = {
    5: "Active",
    10: "Super Active",
    20: "Active Member"
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
        self.last_online = {}

        # Default XP needed per level (linear scale)
        self.xp_per_level = 50

        # Default interval for passive XP task in hours
        self.passive_xp_interval_hours = 3

        # Start the passive XP task with default interval
        self.give_passive_xp.start()

    # Listener for message XP gain
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

        await self.check_level_up(msg.guild, msg.channel, msg.author)

    # This listener ensures the task is running when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.give_passive_xp.is_running():
            self.give_passive_xp.start()

    # Passive XP task that runs every self.passive_xp_interval_hours hours
    @tasks.loop(hours=3)
    async def give_passive_xp(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]:
                    guild_id = str(guild.id)
                    user_id = str(member.id)

                    self.xp_data.setdefault(guild_id, {})
                    self.xp_data[guild_id].setdefault(user_id, {"xp": 0, "level": 0})

                    self.xp_data[guild_id][user_id]["xp"] += 1

                    xp = self.xp_data[guild_id][user_id]["xp"]
                    level = self.xp_data[guild_id][user_id]["level"]
                    required = (level + 1) * self.xp_per_level  # use configurable XP per level

                    if xp >= required:
                        self.xp_data[guild_id][user_id]["level"] += 1
                        new_level = self.xp_data[guild_id][user_id]["level"]

                        channel = discord.utils.get(guild.text_channels, name="général")
                        if channel is None:
                            # fallback : premier channel où on peut écrire
                            for ch in guild.text_channels:
                                if ch.permissions_for(guild.me).send_messages:
                                    channel = ch
                                    break


                        if channel:
                            await channel.send(f"🎉 {member.mention} just reached level **{new_level}** thanks to activity time!")

                        role_name = LEVEL_ROLES.get(new_level)
                        if role_name:
                            role = discord.utils.get(guild.roles, name=role_name)
                            if role:
                                await member.add_roles(role)

        save_xp_data(self.xp_data)

    # Method to check and handle level ups (used for message XP)
    async def check_level_up(self, guild, channel, member):
        guild_id = str(guild.id)
        user_id = str(member.id)

        xp = self.xp_data[guild_id][user_id]["xp"]
        level = self.xp_data[guild_id][user_id]["level"]
        required = (level + 1) * self.xp_per_level  # use configurable XP per level

        if xp >= required:
            self.xp_data[guild_id][user_id]["level"] += 1
            new_level = self.xp_data[guild_id][user_id]["level"]
            await channel.send(f"🎉 {member.mention}, you have reached level **{new_level}**!")

            role_name = LEVEL_ROLES.get(new_level)
            if role_name:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                    await channel.send(f"🏅 You have received the **{role_name}** role!")

            save_xp_data(self.xp_data)

    # Slash command to check your level and XP
    @app_commands.command(name="level", description="Check your current level and XP")
    async def level(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        if guild_id not in self.xp_data or user_id not in self.xp_data[guild_id]:
            await interaction.response.send_message("You haven't earned any XP yet!", ephemeral=True)
            return

        user_stats = self.xp_data[guild_id][user_id]
        xp = user_stats["xp"]
        level = user_stats["level"]
        next_level_xp = (level + 1) * self.xp_per_level

        await interaction.response.send_message(
            f"🔹 Level **{level}** - XP: {xp}/{next_level_xp}", ephemeral=True
        )

    # Debug command to manually set a user's level and XP
    @app_commands.command(name="setlevel", description="Manually set a user's level and XP (debug)")
    @app_commands.describe(user="User to modify", level="New level", xp="New XP amount")
    async def setlevel(self, interaction: discord.Interaction, user: discord.Member, level: int, xp: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        self.xp_data.setdefault(guild_id, {})
        self.xp_data[guild_id].setdefault(user_id, {"xp": 0, "level": 0})

        self.xp_data[guild_id][user_id]["level"] = level
        self.xp_data[guild_id][user_id]["xp"] = xp
        save_xp_data(self.xp_data)

        role_name = LEVEL_ROLES.get(level)
        if role_name:
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role:
                await user.add_roles(role)
                await interaction.channel.send(f"🏅 {user.mention} has received the **{role_name}** role (level {level}).")

        await interaction.response.send_message(
            f"✅ {user.mention}'s level updated to **{level}** with XP: **{xp}**",
            ephemeral=True
        )

    # New command to change XP needed per level and passive XP interval
    @app_commands.command(name="setlevelup", description="Set XP needed per level and passive XP interval in hours")
    @app_commands.describe(xp_per_level="XP needed per level", interval_hours="Passive XP task interval in hours")
    async def set_levelup(self, interaction: discord.Interaction, xp_per_level: int, interval_hours: float):
        # Check admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Validate inputs
        if xp_per_level <= 0 or interval_hours <= 0:
            await interaction.response.send_message("❌ XP per level and interval must be positive numbers.", ephemeral=True)
            return

        # Update variables
        self.xp_per_level = xp_per_level
        self.passive_xp_interval_hours = interval_hours

        # Restart the passive XP task with new interval
        self.give_passive_xp.cancel()  # stop current task
        self.give_passive_xp.change_interval(hours=self.passive_xp_interval_hours)
        if not self.give_passive_xp.is_running():
            self.give_passive_xp.start()

        await interaction.response.send_message(
            f"✅ XP per level set to **{xp_per_level}** and passive XP interval set to **{interval_hours}** hours.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
