import discord

async def welcoming_message(member, bot):
    # channel is named "acceuil" is 1387801960866123827
    channel = bot.get_channel(1387801960866123827)
    # Creation of the embed
    embed = discord.Embed(
        title=f"Bienvenue {member.name} !",
        description="Nous sommes ravis de vous compter parmi nous. Voici quelques informations utiles pour bien commencer :",
        color=discord.Color.blue()
    )

    # add field for embed
    embed.add_field(
        name="À propos de l'association",
        value="Notre association a pour but de [décrire brièvement la mission de l'association].",
        inline=False
    )

    embed.add_field(
        name="Règles du serveur",
        value="""
            1. Respectez tous les membres.
            2. Pas de spam ou de publicité non autorisée.
            3. Utilisez les canaux appropriés pour vos messages.
            4. [Ajoutez d'autres règles spécifiques à votre serveur]
            """,
        inline=False
    )

    embed.add_field(
        name="Activités à venir",
        value="""
            - [Activité 1] : [Date et description]
            - [Activité 2] : [Date et description]
            - [Activité 3] : [Date et description]
            """,
        inline=False
    )

    # Add an image to the embeded
    # embed.set_image(url="URL_DE_L_IMAGE")

    # bottom of the page
    embed.set_footer(text="Bonne journée et amusez-vous bien ! 😊")

    # send the embeded
    await channel.send(embed=embed)