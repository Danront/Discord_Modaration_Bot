# Moder_Bot

Un bot Discord de **modération avancée**, écrit avec `discord.py` et utilisant des **commandes slash**, pour automatiser la gestion de communauté et la sécurité sur ton serveur.

---

## Fonctionnalités principales

- **Filtrage de mots interdits** (`/blacklist`)
-  **Détection de liens suspects**
-  **Système anti-spam personnalisable**
-  **Commandes d'information** sur les utilisateurs, rôles, salons et le serveur
-  **Activation/désactivation des modules à la volée**
-  **Commandes slash intuitives**

---

##  Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/ton-utilisateur/Moder_Bot.git
cd Moder_Bot
```

### 2. Créer et activer un environnement virtuel
```bash
python -m venv myenv
# Windows :
myenv\Scripts\activate
# Linux/macOS :
source myenv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Ajouter le token dans un fichier `.env`
```ini
DISCORD_TOKEN=ton_token_secret
```

### 5. Lancer le bot
```bash
python bot.py
```

---
## Commandes disponibles

### Moderation
- /blacklist_add - Add a word to the blacklist 
- /blacklist_remove - Remove a word from the blacklist 
- /blacklist_list - Display all blacklisted words 
- /antispam - Enable or disable the anti-spam filter 
- /suspicious_links - Enable or disable suspicious link filtering
### LevelSystem
- /level - Check your current level and XP 
- /setlevel - Manually set a user's level and XP (debug) 
- /setlevelup - Set XP needed per level and passive XP interval in hours
### Roles
- /roles_show - Create the message for reaction roles 
- /roles_add - Add a new reaction role 
- /role_remove - Remove a reaction role by role name
### Commands
- /ban - Ban a member from the server 
- /unban - Unban a member from the server by their ID 
- /kick - Kick a member from the server 
- /mute - Mute a member for a specified duration 
- /unmute - Remove the mute from a member. 
- /warn - Warn a member of the server. 
- /warnings - View the warnings of a member. 
- /clear - Delete a certain number of messages 
- /slowmode - Set the slowmode delay of a channel (in seconds). 
- /lock - Lock this channel for members. 
- /unlock - Unlock this channel for members. 
- /scan_messages - Scan recent messages containing a word. 
- /ping_check - Check the bot's latency. 
- /antiraid - Enable or disable anti-raid protection. 
- /serverinfo - Display general server information 
- /userinfo - Information about a member (account, roles, etc.) 
- /roleinfo - Information about a specific role 
- /channelinfo - Information about the current channel
### Help
- /help - Show all available commands

---
## Structure du projet

```
Moder_Bot/
├── cogs/
│   ├── help.py                         # Programme qui affiche tous les commandes
│   ├── welcome.py                  # Programme de message de bienvenu
│   ├── roles.py                         # Programme de rôles réactif
│   ├── moderation.py              # Programme de modération
│   ├── levels.py                        # Programme de xp
│   └── commands.py               # Commandes personnalisé
├── json/
│   ├── black_list.json                    # Liste noire des mots
│   ├── anti_raid.json                     # Etat du raid mémorisée
│   ├── xp_data.json                      # Sauvegarde de XP
│   └── warnings.json                    # Sauvegarde des warn
├── bot.py                                # Point d'entrée du bot
├── keepAlive.py.py                 # Flask du service
├── requirements.txt                # Liste des librairies py
├── README.md
└── .env                                    # Token du bot (non versionné)
```

---
## Prérequis

- Python 3.10+
- Un bot Discord avec les intents activés :
    - Intents de message
    - Intents de présence (facultatif)

Créer le bot ici : discord.com/developers

---

## Contributions

Les PR sont bienvenues ! Forke le dépôt, crée une branche (`git checkout -b feature/ma-feature`), puis envoie une PR.