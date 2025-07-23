from discord.ext import commands
import discord
from discord import app_commands

import re
import time
from collections import defaultdict, deque

import asyncio
import json
import os

BLACKLIST_FILE = "json/black_list.json"

async def safe_delete(self, message: discord.Message, delay: float = 0.25):
    """
    Safely delete a Discord message after an optional delay.
    Handles potential rate limits or HTTP exceptions.
    """
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except discord.HTTPException:
        print("Rate limit or error occurred while deleting the message.")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load blacklisted words from file or initialize empty list
        self.blacklisted_words = self.load_blacklist()
        # Store recent message timestamps per user to detect spam (max 5 messages stored per user)
        self.message_logs = defaultdict(lambda: deque(maxlen=5))
        self.antispam_enabled = True  # Anti-spam feature enabled by default
        self.suspicious_links_enabled = True  # Suspicious link filtering enabled by default
        
        # Anti-spam settings
        self.MAX_MESSAGES = 2       # Number of messages allowed in the interval
        self.INTERVAL_SECONDS = 2   # Time window (seconds) to check for spam
        
        # Tracking cooldowns and mute durations per user (user_id: timestamp)
        self.user_warn_cooldowns = {}  # Last warning timestamp per user
        self.user_muted_until = {}     # Timestamp until which user is muted (messages deleted silently)
        
        # Duration settings (seconds)
        self.WARNING_COOLDOWN = 5   # Minimum seconds between warnings
        self.MUTE_DURATION = 5      # Duration of silent message deletion after warning

    def load_blacklist(self):
        """
        Load the blacklist of forbidden words from a JSON file.
        Return an empty list if file doesn't exist or on error.
        """
        try:
            if not os.path.exists(BLACKLIST_FILE):
                return []
            with open(BLACKLIST_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []

    def save_blacklist(self):
        """
        Save the current blacklist words to the JSON file.
        """
        with open(BLACKLIST_FILE, "w", encoding="utf-8") as file:
            json.dump(self.blacklisted_words, file, indent=4)

    def contains_blacklisted_word(self, content: str) -> bool:
        """
        Check if the given message content contains any blacklisted word.
        Case-insensitive check.
        """
        content = content.lower()
        return any(word.lower() in content for word in self.blacklisted_words)

    def contains_suspicious_link(self, content: str) -> bool:
        """
        Detect suspicious URLs in the message content.
        Ignores known safe domains like discord.gg and example.com.
        """
        url_pattern = r'https?://[^\s]+'  # Basic URL pattern matching http or https links
        matches = re.findall(url_pattern, content.lower())
        # Return True if any URL is not from safe domains
        return any("discord.gg" not in link and "example.com" not in link for link in matches)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Event listener triggered on every new message.
        Performs:
        - Blacklisted word filtering
        - Suspicious link filtering
        - Anti-spam checks with warnings and temporary mute
        """
        if message.author.bot:
            return  # Ignore bot messages

        # Check for blacklisted words and delete message if found
        if self.contains_blacklisted_word(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, your message contained a forbidden word.", delete_after=5)
            return

        # Check for suspicious links and delete message if found
        if self.suspicious_links_enabled and self.contains_suspicious_link(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, suspicious link detected.", delete_after=5)
            return

        # Anti-spam logic
        if self.antispam_enabled:
            user_id = message.author.id
            current_time = time.time()

            # If user is muted, delete all their messages silently until mute expires
            if self.user_muted_until.get(user_id, 0) > current_time:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Log the message timestamp for spam detection
            self.message_logs[user_id].append(current_time)
            timestamps = self.message_logs[user_id]

            # Check if user sent too many messages in a short interval
            if len(timestamps) >= self.MAX_MESSAGES and (timestamps[-1] - timestamps[0]) < self.INTERVAL_SECONDS:
                last_warning = self.user_warn_cooldowns.get(user_id, 0)
                # Check if enough time has passed since last warning
                if current_time - last_warning >= self.WARNING_COOLDOWN:
                    try:
                        await message.delete()
                    except discord.HTTPException:
                        pass

                    try:
                        warn_msg = await message.channel.send(f"{message.author.mention}, please avoid spamming!", delete_after=5)
                    except Exception:
                        pass

                    # Update last warning time and mute user temporarily
                    self.user_warn_cooldowns[user_id] = current_time
                    self.user_muted_until[user_id] = current_time + self.MUTE_DURATION
                else:
                    # If still on cooldown, just delete the message silently
                    try:
                        await self.safe_delete(message)
                    except discord.HTTPException:
                        pass
                return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Event listener triggered when a message is edited.
        Re-checks blacklisted words and suspicious links in the edited content,
        deletes and warns user if violations are detected.
        """
        if after.author.bot:
            return

        if self.contains_blacklisted_word(after.content):
            await after.delete()
            await after.channel.send(f"{after.author.mention}, forbidden word detected in your edit.", delete_after=5)

        elif self.suspicious_links_enabled and self.contains_suspicious_link(after.content):
            await after.delete()
            await after.channel.send(f"{after.author.mention}, suspicious link detected in your edit.", delete_after=5)

    ######################
    # BLACKLIST COMMANDS #
    ######################

    @app_commands.command(name="blacklist_add", description="Add a word to the blacklist")
    @app_commands.describe(word="Word to add to the blacklist")
    async def blacklist_add(self, interaction: discord.Interaction, word: str):
        """
        Slash command to add a new word to the blacklist.
        """
        word = word.lower()

        if word in self.blacklisted_words:
            await interaction.response.send_message(f"The word '{word}' is already in the blacklist.", ephemeral=True)
            return

        self.blacklisted_words.append(word)
        self.save_blacklist()

        await interaction.response.send_message(f"The word '{word}' has been added to the blacklist.", ephemeral=True)

    @app_commands.command(name="blacklist_remove", description="Remove a word from the blacklist")
    @app_commands.describe(word="Word to remove from the blacklist")
    async def blacklist_remove(self, interaction: discord.Interaction, word: str):
        """
        Slash command to remove a word from the blacklist.
        """
        word = word.lower()

        if word not in self.blacklisted_words:
            await interaction.response.send_message(f"The word '{word}' is not in the blacklist.", ephemeral=True)
            return

        self.blacklisted_words.remove(word)
        self.save_blacklist()

        await interaction.response.send_message(f"The word '{word}' has been removed from the blacklist.", ephemeral=True)

    @app_commands.command(name="blacklist_list", description="Display all blacklisted words")
    async def blacklist_list(self, interaction: discord.Interaction):
        """
        Slash command to list all blacklisted words in an embed.
        """
        if not self.blacklisted_words:
            await interaction.response.send_message("🚫 The blacklist is currently empty.", ephemeral=True)
            return

        words_formatted = "\n".join(f"- {word}" for word in self.blacklisted_words)
        embed = discord.Embed(
            title="📄 Blacklisted Words",
            description=words_formatted,
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    ###################
    # TOGGLE COMMANDS #
    ###################

    @app_commands.command(name="antispam", description="Enable or disable the anti-spam filter")
    @app_commands.describe(state="Desired state: on or off")
    async def toggle_antispam(self, interaction: discord.Interaction, state: str):
        """
        Slash command to toggle the anti-spam feature on or off.
        """
        state = state.lower()
        if state not in ["on", "off"]:
            await interaction.response.send_message("❌ Please use 'on' or 'off' only.", ephemeral=True)
            return

        self.antispam_enabled = (state == "on")
        status = "✅ Enabled" if self.antispam_enabled else "⛔ Disabled"
        await interaction.response.send_message(f"🛡️ Anti-spam: {status}", ephemeral=True)

    @app_commands.command(name="suspicious_links", description="Enable or disable suspicious link filtering")
    @app_commands.describe(state="Desired state: on or off")
    async def toggle_suspicious_links(self, interaction: discord.Interaction, state: str):
        """
        Slash command to toggle suspicious link filtering on or off.
        """
        state = state.lower()
        if state not in ["on", "off"]:
            await interaction.response.send_message("❌ Please use 'on' or 'off' only.", ephemeral=True)
            return

        self.suspicious_links_enabled = (state == "on")
        status = "✅ Enabled" if self.suspicious_links_enabled else "⛔ Disabled"
        await interaction.response.send_message(f"🔗 Suspicious links filter: {status}", ephemeral=True)

async def setup(bot):
    """
    Setup function to add the Moderation cog to the bot.
    """
    await bot.add_cog(Moderation(bot))
