import discord
from discord.ext import commands
from discord import app_commands

import json
import os

ROLES_PATH = "json/roles.json"
TARGET_MESSAGE_ID = 0

def load_roles(path="reaction_roles.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_roles(data, path="reaction_roles.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles = load_roles(ROLES_PATH)

    @app_commands.command(name="roles_show", description="Create the message for reaction roles")
    async def roles(self, interaction: discord.Interaction):
        global TARGET_MESSAGE_ID

        await interaction.response.defer(ephemeral=True)

        channel = self.bot.get_channel(interaction.channel_id)
        if channel is None:
            await interaction.followup.send("Unable to access the channel.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎭 Choose your roles",
            description="Click a reaction to get a role. Click again to remove it.",
            color=discord.Color.green()
        )

        for emoji, role in self.roles.items():
            embed.add_field(name=role, value=f"React with {emoji}", inline=False)

        msg = await channel.send(embed=embed)
        TARGET_MESSAGE_ID = msg.id

        for emoji in self.roles:
            await msg.add_reaction(emoji)

        await interaction.followup.send("Message sent successfully!", ephemeral=True)

    @app_commands.command(name="roles_add", description="Add a new reaction role")
    @app_commands.describe(emoji="Emoji to use for the role", role_name="Exact name of the role to assign")
    async def add_reaction_role(self, interaction: discord.Interaction, emoji: str, role_name: str):
        self.roles[emoji] = role_name
        save_roles(self.roles, ROLES_PATH)
        await interaction.response.send_message(f"✅ Reaction role added: {emoji} → {role_name}", ephemeral=True)

    @app_commands.command(name="role_remove", description="Remove a reaction role by role name")
    @app_commands.describe(role_name="Name of the role to remove from reaction roles")
    async def remove_reaction_role(self, interaction: discord.Interaction, role_name: str):
        emoji_to_remove = None
        for emoji, role in self.roles.items():
            if role.lower() == role_name.lower():
                emoji_to_remove = emoji
                break

        if emoji_to_remove is None:
            await interaction.response.send_message(
                f"❌ No reaction role found with the name '{role_name}'.", ephemeral=True
            )
            return

        removed_role = self.roles.pop(emoji_to_remove)
        save_roles(self.roles, ROLES_PATH)
        await interaction.response.send_message(
            f"✅ Removed reaction role: {emoji_to_remove} → {removed_role}", ephemeral=True
        )


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id != TARGET_MESSAGE_ID or payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)
        role_name = self.roles.get(emoji)
        if not member or not role_name:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            try:
                await member.add_roles(role)
            except Exception as e:
                print(f"Error while adding role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != TARGET_MESSAGE_ID or payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji)
        role_name = self.roles.get(emoji)
        if not member or not role_name:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            try:
                await member.remove_roles(role)
            except Exception as e:
                print(f"Error while removing role: {e}")

async def setup(bot):
    await bot.add_cog(Roles(bot))