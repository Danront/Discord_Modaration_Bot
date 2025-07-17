import discord
from discord.ext import commands

class AcceptRulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Pas de timeout pour que le bouton reste dispo

    @discord.ui.button(label="✅ J'accepte les conditions", style=discord.ButtonStyle.success, custom_id="accept_rules")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild

        role_new = discord.utils.get(guild.roles, name="Nouvel Arrivant")
        role_member = discord.utils.get(guild.roles, name="Membre")

        if role_new in member.roles:
            await member.remove_roles(role_new, reason="Conditions acceptées")

        if role_member not in member.roles:
            await member.add_roles(role_member, reason="Conditions acceptées")

        button.disabled = True  # Désactive le bouton après clic
        await interaction.message.edit(view=self)

        await interaction.response.send_message("Merci d'avoir accepté les conditions ! Tu as maintenant accès au serveur.", ephemeral=True)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def welcoming_message(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="accueil")
        if channel:
            embed = discord.Embed(
                title="Bienvenue sur le serveur !",
                description=(
                    f"{member.mention}, nous sommes ravis de t'accueillir parmi nous ! 🎉\n\n"
                    "Voici quelques informations utiles pour bien commencer :"
                ),
                color=discord.Color.blue()
            )

            embed.add_field(
                name="À propos de l'association",
                value="Notre association a pour but de [décrire brièvement la mission de l'association].",
                inline=False
            )
            embed.add_field(
                name="Activités à venir",
                value=(
                    "- [Activité 1] : [Date et description]\n"
                    "- [Activité 2] : [Date et description]\n"
                    "- [Activité 3] : [Date et description]"
                ),
                inline=False
            )
            embed.add_field(
                name="Règles du serveur à lire avec ses 2 yeux 👀",
                value=(
                    "- Respectez tous les membres.\n"
                    "- Pas de spam ou de publicité non autorisée.\n"
                    "- Utilisez les canaux appropriés pour vos messages.\n"
                    "- S'amuser\n"
                    "- [Ajoutez d'autres règles spécifiques à votre serveur]"
                ),
                inline=False
            )
            embed.set_footer(text="Bonne journée et amusez-vous bien ! 😊")
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

            view = AcceptRulesView()
            await channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="Nouvel Arrivant")
        if role:
            try:
                await member.add_roles(role, reason="Nouveau membre rejoint le serveur.")
            except discord.Forbidden:
                print(f"⚠️ Impossible d'ajouter le rôle {role.name} à {member.name} (permissions manquantes).")
            except Exception as e:
                print(f"❌ Erreur lors de l'ajout du rôle : {e}")

        await self.welcoming_message(member)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
