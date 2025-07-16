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

###  Modération

- `/blacklist add [mot]` – Ajoute un mot à la blacklist
- `/blacklist remove [mot]` – Retire un mot de la blacklist
- `/blacklist list` – Affiche la liste complète
- `/antispam on|off` – Active/désactive le filtre anti-spam
- `/suspicious_links on|off` – Active/désactive le blocage de liens suspects

###  Informations

- `/serverinfo` – Affiche les infos générales du serveur
- `/userinfo @membre` – Infos détaillées sur un utilisateur
- `/roleinfo @rôle` – Donne des infos sur un rôle
- `/channelinfo` – Donne des infos sur le salon actuel

###  Aide

- `/help` – Affiche toutes les commandes du bot

---
## Structure du projet
Moder_Bot/
├── cogs/
│   ├── welcome.py          # Programme de message de bienvenu
│   ├── roles.py            # Programme de rôles réactif
│   ├── moderation.py       # Programme de modération
│   ├── levels.py           # Programme de xp
│   └── commands.py         # Commandes personalisé
│
├── utils/                  # Utilitaires (si nécessaire)
│   ├── anti_spam.py        # Fonction constante de l'anti spam
│   ├── constants.py        # Liste de constante
│   └── xp_utils.py         # Fonction constante de l'xp
│
├── black_list.json         # Liste noire des mots
├── anti_raid.json          # Etat du raid mémorisée
├── xp_data.json            # Sauvegarde de XP
├── warnings.json           # Sauvegarde des warn
├── bot.py                  # Point d'entrée du bot
├── keepAlive.py.py         # Flask du service
├── requirements.txt        # Liste des librairies py
├── README.md
└── .env                    # Token du bot (non versionné)

---

## Prérequis

- Python 3.10+
- Un bot Discord avec les intents activés :
    - Intents de message
    - Intents de présence (facultatif)

Créer ton bot ici : discord.com/developers

---

## Contributions

Les PR sont bienvenues ! Forke le dépôt, crée une branche (`git checkout -b feature/ma-feature`), puis envoie une PR.