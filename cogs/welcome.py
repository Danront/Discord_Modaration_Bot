import discord
from discord.ext import commands

class AcceptRulesView(discord.ui.View):
    def __init__(self, member_id: int):
        super().__init__(timeout=None)
        self.member_id = member_id  # ID du membre autorisé

    @discord.ui.button(label="✅ J'accepte les conditions", style=discord.ButtonStyle.success, custom_id="accept_rules")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user

        # Vérifie que seul le bon membre peut cliquer
        if member.id != self.member_id:
            await interaction.response.send_message("❌ Ce bouton ne t’est pas destiné !", ephemeral=True)
            return

        guild = interaction.guild
        role_new = discord.utils.get(guild.roles, name="Nouvel Arrivant")
        role_member = discord.utils.get(guild.roles, name="Membre")

        if role_new in member.roles:
            await member.remove_roles(role_new, reason="Conditions acceptées")

        if role_member not in member.roles:
            await member.add_roles(role_member, reason="Conditions acceptées")

        button.disabled = True
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            "✅ Merci d'avoir accepté les conditions ! Tu as maintenant accès au serveur.",
            ephemeral=True
        )

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def welcoming_message(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="👋-accueil")
        if channel:
            embed = discord.Embed(
                title=f"👋 Bienvenue sur {member.guild.name} !",
                description=(
                    f"Salut {member.mention} ! Nous sommes ravis de t'accueillir parmi nous. 🎉\n\n"
                    "Pour bien démarrer, voici quelques infos essentielles 👇"
                ),
                color=discord.Color.blurple()
            )

            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

            embed.add_field(
                name="📌 À faire dès maintenant",
                value=(
                    "• Lire attentivement les règles 📖\n"
                    "• Cliquer sur le bouton en bas pour accepter les règles ✅\n"
                    "• Fait le choix de ton role dans <#📝-rôles-salons> 🎭\n"
                    "• Se présenter dans <#Salon> 🙋‍♂️ (facultatif mais apprécié)\n"
                    "• Explorer les salons disponibles selon tes intérêts 🔍"
                ),
                inline=False
            )

            embed.add_field(
            name="ℹ️ À propos de l'association",
            value=(
                "Notre objectif est de sensibiliser à la surconsommation (alimentaire, vestimentaire, énergétique, etc.) "
                "pour contribuer à un avenir durable et harmonieux.\n"
                "Nous agissons sur les trois piliers du développement durable : social, économique et écologique, "
                "en organisant des événements, en soutenant les populations vulnérables, "
                "en encourageant les pratiques responsables, et en promouvant des alternatives écologiques."
            ),
            inline=False
            )

            embed.add_field(
                name="📜 Règles du serveur",
                value=(
                    "• 🤝 Respect et bienveillance entre membres\n"
                    "• 🚫 Pas de spam, insultes ou pub non autorisée\n"
                    "• 🧭 Restez dans les bons salons\n"
                    "• 🎉 Amusez-vous bien !"
                ),
                inline=False
            )

            embed.set_footer(text="L’équipe de modération est là si tu as besoin d’aide ! ❤️")

            view = AcceptRulesView(member.id)
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
