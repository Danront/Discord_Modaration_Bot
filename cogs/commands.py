# IMPORTS #
from datetime import timedelta
import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CooldownMapping, BucketType

import os
import json
import asyncio

# FILES REFERENCE #
INFRACTIONS_FILE = "json/infractions.json"
ANTI_RAID_FILE = "json/anti_raid.json"

# MAIN FUNCTIONS #
def load_anti_raid():
    if not os.path.exists(ANTI_RAID_FILE):
        return {}
    with open(ANTI_RAID_FILE, "r") as f:
        return json.load(f)

def save_anti_raid(data):
    with open(ANTI_RAID_FILE, "w") as f:
        json.dump(data, f, indent=4)

# MAIN CLASS #
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anti_raid_data = load_anti_raid()
        self.cooldowns = CooldownMapping.from_cooldown(1, 10, BucketType.user)


    ############################################################################################################
    # MODERATION                                                                                                #
    ############################################################################################################
    ########
    # PING #
    ########
    @app_commands.command(name="ping", description="Latency test")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")

    #######
    # BAN #
    #######
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(user="The member to ban", reason="Reason for the ban")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)
            return
        
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"✅ {user} has been banned from the server. Reason: {reason if reason else 'No reason specified'}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I do not have permission to ban this member.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ An error occurred while banning.", ephemeral=True)

    #########
    # UNBAN #
    #########
    @app_commands.command(name="unban", description="Unban a member from the server by their ID")
    @app_commands.describe(user_id="The ID of the member to unban")
    async def unban(self, interaction: discord.Interaction, user_id: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)
            return

        try:
            banned_users = await interaction.guild.bans()
            user = discord.utils.get(banned_users, user__id=user_id)
            if user is None:
                await interaction.response.send_message(f"❌ No banned member found with ID {user_id}.", ephemeral=True)
                return
            
            await interaction.guild.unban(user.user)
            await interaction.response.send_message(f"✅ {user.user} has been unbanned from the server.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I do not have permission to unban this member.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ An error occurred while unbanning.", ephemeral=True)

    ########
    # KICK #
    ########
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(user="The member to kick", reason="Reason for the kick")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)
            return

        if user == interaction.user:
            await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
            return

        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"✅ {user.mention} has been kicked from the server. Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I do not have permission to kick this member.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ An error occurred while kicking.", ephemeral=True)

    ########
    # MUTE #
    ########
    @app_commands.command(name="mute", description="Mute a member for a specified duration")
    @app_commands.describe(user="The member to mute", duration="Duration of the mute (e.g., 10m, 1h, 1d)", reason="Reason for the mute")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)
            return
        
        if user == interaction.user:
            await interaction.response.send_message("❌ You cannot mute yourself.", ephemeral=True)
            return

        time_seconds = self.parse_duration(duration)
        if time_seconds is None:
            await interaction.response.send_message("❌ Invalid duration. Use `10m`, `1h`, `2d`, etc.", ephemeral=True)
            return

        try:
            await user.timeout(timedelta(seconds=time_seconds), reason=reason)
            await interaction.response.send_message(
                f"🔇 {user.mention} has been muted for `{duration}`. Reason: {reason}",
                ephemeral=True  # <-- message visible only to the admin
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ I do not have permission to mute this member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error during mute: {e}", ephemeral=True)

    def parse_duration(self, duration_str: str):
        duration_str = duration_str.strip().lower()
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if duration_str[-1] in units and duration_str[:-1].isdigit():
            return int(duration_str[:-1]) * units[duration_str[-1]]
        return None
    
    ##########
    # UNMUTE #
    ##########
    @app_commands.command(name="unmute", description="Remove the mute from a member.")
    @app_commands.describe(member="The member to unmute")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.timeout(None)
            await interaction.response.send_message(f"{member.mention} has been unmuted.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to unmute this member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    ########
    # WARN #
    ########
    @app_commands.command(name="warn", description="Warn a member of the server.")
    @app_commands.describe(member="The member to warn", reason="Reason for the warning")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        warnings_file = "warnings.json"

        # Load existing warnings
        warnings = {}
        if os.path.exists(warnings_file):
            try:
                with open(warnings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        warnings = json.loads(content)
            except json.JSONDecodeError:
                warnings = {}

        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings:
            warnings[guild_id] = {}

        if user_id not in warnings[guild_id]:
            warnings[guild_id][user_id] = []

        warnings[guild_id][user_id].append({
            "mod_id": str(interaction.user.id),
            "reason": reason
        })

        with open(warnings_file, "w", encoding="utf-8") as f:
            json.dump(warnings, f, indent=4, ensure_ascii=False)

        # Try sending a DM to the warned member
        try:
            await member.send(f"You have been warned on the server **{interaction.guild.name}** for the following reason: {reason}")
        except discord.Forbidden:
            # Cannot send DM (member disabled DMs)
            pass

        # Confirm the warning in the server
        await interaction.response.send_message(
            f"{member.mention} has been warned for: {reason}", ephemeral=True
        )
    

    ###########
    # WARNINGS #
    ###########
    @app_commands.command(name="warnings", description="View the warnings of a member.")
    @app_commands.describe(member="The member to check")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        warnings_file = "warnings.json"

        # Load warnings
        warnings = {}
        if os.path.exists(warnings_file):
            try:
                with open(warnings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        warnings = json.loads(content)
            except json.JSONDecodeError:
                warnings = {}

        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings or user_id not in warnings[guild_id] or not warnings[guild_id][user_id]:
            await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)
            return

        user_warnings = warnings[guild_id][user_id]

        # Build the message
        description = ""
        for i, w in enumerate(user_warnings, 1):
            mod_id = w.get("mod_id", "Unknown")
            reason = w.get("reason", "No reason provided")
            description += f"**{i}.** Reason: {reason} \n"

        embed = discord.Embed(
            title=f"Warnings for {member.display_name}",
            description=description,
            color=discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        #########
    # CLEAR #
    #########
    @app_commands.command(name="clear", description="Delete a certain number of messages")
    @app_commands.describe(amount="Number of messages to delete")
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount + 1)

        # Send the response
        msg = await interaction.followup.send(f"{len(deleted)} messages deleted.", ephemeral=True)

        # Delete the message after 5 seconds
        await asyncio.sleep(5)
        await msg.delete()

    ############
    # SLOWMODE #
    ############
    @app_commands.command(name="slowmode", description="Set the slowmode delay of a channel (in seconds).")
    @app_commands.describe(delay="Time in seconds (0 to disable)")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, delay: int):
        try:
            await interaction.channel.edit(slowmode_delay=delay)
            if delay == 0:
                await interaction.response.send_message("Slowmode disabled.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Slowmode enabled: {delay} seconds.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    ########
    # LOCK #
    ########
    @app_commands.command(name="lock", description="Lock this channel for members.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        try:
            overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = False
            await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    ##########
    # UNLOCK #
    ##########
    @app_commands.command(name="unlock", description="Unlock this channel for members.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        try:
            overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = True
            await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    ############################################################################################################
    # ANALYSIS & MONITORING                                                                                     #
    ############################################################################################################
    #################
    # SCAN MESSAGES #
    #################
    @app_commands.command(name="scan_messages", description="Scan recent messages containing a word.")
    @app_commands.describe(word="Word or phrase to search for in messages")
    async def scan_messages(self, interaction: discord.Interaction, word: str):
        # Permission check
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)  # To avoid timeout (shows "thinking...")

        channel = interaction.channel
        found = []

        async for message in channel.history(limit=100):
            if word.lower() in message.content.lower():
                found.append(f"**{message.author}**: {message.content[:100]}")

        if found:
            content = "\n".join(found[:10])  # Limit to avoid too long messages
            await interaction.followup.send(f"🔍 Messages containing **{word}**:\n{content}", ephemeral=True)
        else:
            await interaction.followup.send(f"No recent messages contain the word **{word}**.", ephemeral=True)

    def get_user_warnings(self, user_id: int, guild_id: int) -> int:
        if not os.path.exists(INFRACTIONS_FILE):
            return 0
        with open(INFRACTIONS_FILE, "r") as f:
            data = json.load(f)
        guild_data = data.get(str(guild_id), {})
        user_data = guild_data.get(str(user_id), [])
        return len(user_data)
    
    ##############
    # PING CHECK #
    ##############
    @app_commands.command(name="ping_check", description="Check the bot's latency.")
    async def ping_check(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convert to ms
        embed = discord.Embed(
            title="Ping Check Response!",
            description=f"Latency: **{latency} ms**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    ############################################################################################################
    # SECURITY                                                                                                 #
    ############################################################################################################
    ############
    # ANTIRAID #
    ############
    @app_commands.command(name="antiraid", description="Enable or disable anti-raid protection.")
    @app_commands.describe(mode="on or off to manage anti-raid protection.")
    async def antiraid(self, interaction: discord.Interaction, mode: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        mode = mode.lower()
        guild_id = str(interaction.guild.id)

        if mode == "on":
            self.anti_raid_data[guild_id] = True
            save_anti_raid(self.anti_raid_data)
            await interaction.response.send_message("🛡️ Anti-raid protection **enabled**.", ephemeral=True)

        elif mode == "off":
            self.anti_raid_data[guild_id] = False
            save_anti_raid(self.anti_raid_data)
            await interaction.response.send_message("⚠️ Anti-raid protection **disabled**.", ephemeral=True)

        else:
            await interaction.response.send_message("❗ Use `on` or `off`.", ephemeral=True)

    def is_antiraid_enabled(self, guild_id: int) -> bool:
        return self.anti_raid_data.get(str(guild_id), False)

    ############################################################################################################
    # INFORMATION                                                                                                #
    ############################################################################################################
    ###############
    # SERVER INFO #
    ###############
    @app_commands.command(name="serverinfo", description="Display general server information")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        owner = guild.owner or await guild.fetch_owner()
        created_at = guild.created_at.strftime('%d/%m/%Y')
        roles = len(guild.roles) - 1  # exclude @everyone
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        members = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = members - bots

        embed = discord.Embed(
            title=f"📊 Information about {guild.name}",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Owner", value=f"{owner} ({owner.id})", inline=True)
        embed.add_field(name="📅 Created on", value=created_at, inline=True)
        embed.add_field(name="👥 Members", value=f"Total: {members}\nHumans: {humans}\nBots: {bots}", inline=False)
        embed.add_field(name="💬 Text Channels", value=text_channels, inline=True)
        embed.add_field(name="🔊 Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="🏷️ Roles", value=roles, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="userinfo", description="Information about a member (account, roles, etc.)")
    @app_commands.describe(user="The member to examine")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=True)
        
        roles = [role.mention for role in user.roles if role != interaction.guild.default_role]
        highest_role = user.top_role.mention if user.top_role != interaction.guild.default_role else "None"

        joined = user.joined_at.strftime('%d/%m/%Y %H:%M') if user.joined_at else "Unknown"
        created = user.created_at.strftime('%d/%m/%Y %H:%M')

        status_emoji = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🌙 Idle",
            discord.Status.dnd: "⛔ Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        status = status_emoji.get(user.status, "❔ Unknown")

        device = ", ".join(client.name for client in user.devices) if hasattr(user, 'devices') else "Unknown"
        is_timed_out = user.timed_out_until is not None and user.timed_out_until > discord.utils.utcnow()

        is_bot = "Yes 🤖" if user.bot else "No"

        # Load warnings count (simulate loading from JSON)
        try:
            with open("json/warnings.json", "r") as f:
                warns_data = json.load(f)
            guild_id = str(interaction.guild.id)
            user_id = str(user.id)
            warn_count = len(warns_data.get(guild_id, {}).get(user_id, []))
        except Exception as e:
            print(f"Error loading warnings: {e}")
            warn_count = 0

        embed = discord.Embed(
            title=f"📋 Info about {user.display_name}",
            color=user.color if user.color.value else discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.add_field(name="📛 Username", value=str(user), inline=True)
        embed.add_field(name="🤖 Bot", value=is_bot, inline=True)
        embed.add_field(name="📅 Created on", value=created, inline=False)
        embed.add_field(name="📥 Joined server", value=joined, inline=False)
        embed.add_field(name="📶 Status", value=status, inline=True)
        embed.add_field(name="💻 Platform", value=device, inline=True)
        embed.add_field(name="🔇 Muted (Timeout)", value="Yes" if is_timed_out else "No", inline=True)
        embed.add_field(name="⚠️ Warnings", value=str(warn_count), inline=True)
        embed.add_field(name="🏷️ Roles", value=", ".join(roles) if roles else "No roles", inline=False)
        embed.add_field(name="🔝 Highest role", value=highest_role, inline=True)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed, ephemeral=True)

    #############
    # ROLE INFO #
    #############
    @app_commands.command(name="roleinfo", description="Information about a specific role")
    @app_commands.describe(role="The role to examine")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title=f"📘 Info about role: {role.name}",
            color=role.color
        )
        embed.add_field(name="🆔 ID", value=role.id, inline=True)
        embed.add_field(name="📛 Name", value=role.name, inline=True)
        embed.add_field(name="🧱 Position", value=role.position, inline=True)
        embed.add_field(name="🔒 Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="🌐 Display separately", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="🎨 Color", value=str(role.color), inline=True)
        embed.add_field(name="👥 Number of members", value=str(len(role.members)), inline=False)
        embed.set_footer(text=f"Created on {role.created_at.strftime('%d/%m/%Y at %H:%M')}")

        await interaction.followup.send(embed=embed, ephemeral=True)

    ################
    # CHANNEL INFO #
    ################
    @app_commands.command(name="channelinfo", description="Information about the current channel")
    async def channel_info(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        embed = discord.Embed(
            title=f"📺 Info about channel: {channel.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="🆔 ID", value=channel.id, inline=True)
        embed.add_field(name="📁 Category", value=channel.category.name if channel.category else "None", inline=True)
        embed.add_field(name="🗣️ Type", value=str(channel.type).capitalize(), inline=True)
        embed.add_field(name="🔒 Private channel", value="Yes" if isinstance(channel, discord.TextChannel) and not channel.permissions_for(channel.guild.default_role).read_messages else "No", inline=True)
        embed.set_footer(text=f"Created on {channel.created_at.strftime('%d/%m/%Y at %H:%M')}")

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))