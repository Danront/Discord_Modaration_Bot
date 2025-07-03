import discord
from discord.ext import commands
import re

BLACKLIST = ["merde", "idiot", "salopard"]
SUSPICIOUS_LINKS = ["http://", "https://", "discord.gg/"]
user_message_times = {}

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_send(self, msg, blacklist, links, msg_times):
        content = msg.content.lower()
        if any(word in content for word in blacklist):
            await msg.delete()
            await msg.channel.send(f"{msg.author.mention}, ton message contient un mot interdit.")
        if any(link in content for link in links):
            await msg.delete()
            await msg.channel.send(f"{msg.author.mention}, les liens sont interdits ici.")

    async def on_edit(self, before, after, blacklist, links):
        await self.on_send(after, blacklist, links, user_message_times)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
