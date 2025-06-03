<a id="readme-top"></a>
![XiuXianBot](https://socialify.git.ci/aosumi-rena/XiuXianBot/image?custom_description=A+text-based+XiuXian%2F%E4%BF%AE%E4%BB%99+game+Bot+which+supports+multiple+platforms+at+the+same+time.&description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fminas.mihoyo.day%2Ff%2F1902fc2bd211436baf50%2F%3Fdl%3D1&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stars][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL-3.0 License][license-shield]][license-url]

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/aosumi-rena/XiuXianBot)
[![Downloads][downloads-shield]][downloads-url]

# XiuXianGame Bot
A text-based game Bot which supports both Telegram and Discord (Matrix and more in future) at the same time, by running in a universal core logic with adapters to other platforms, all sharing the same game engine and database.

**README Variations**

[简体中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md) | [English](https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md)

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Table of Contents

<details>
  <summary>Click To Expand</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#architecture">Architecture</a>
      <ul>
        <li><a href="#file-structure">File Structure</a></li>
        <li><a href="#core-modules">Core Modules</a></li>
        <li><a href="#platform-adapters">Platform Adapters</a></li>
        <li><a href="#web-interfaces">Web Interfaces</a></li>
      </ul>
    </li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
      <ul>
        <li><a href="#core">Core</a></li>
        <li><a href="#game-functions">Game Functions</a></li>
      </ul>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
      <ul>
        <li><a href="#ai">AI</a></li>
        <li><a href="#inspirations">Inspirations</a></li>
        <li><a href="#media">Media Resources</a></li>
      </ul>
    <li><a href="#others">Others</a></li>
      <ul>
        <li><a href="#star-history">Star History</a></li>
      </ul>
  </ol>
</details>

---

## About The Project

XiuXianBot is a cultivation‑themed RPG text-based game bot originally built for Discord, and hopefully turn into a cross-platform version in future, it will contain:

- A **core** library containing all game logic, database models, and localization.
- Multiple **adapters** for different chat platforms (Discord, Telegram, Matrix…).
- **Web interfaces** for admin control and public account management.
- A **single bootstrap** (`start.py`) that loads configuration and starts the desired adapters.

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Architecture

### File Structure
```
root/
├── adapters/
│   ├── discord/    # Discord‑specific commands, modals, embeds
│   |   └── bot.py              # To activate the bot  
│   ├── telegram/   # Telegram slash commands, inline keyboards
│   |   └── bot.py              # To activate the bot  
│   ├── matrix/     # Matrix (future)
│   |   └── bot.py              # To activate the bot  
│   └── ???/        # More platforms (future)
├── core/
│   ├── commands/   # Game commands (hunt.py, cul.py, asc.py, account.py, ele.py, etc.), which decides how the bot will react
│   ├── config/     # Additional game configuaations, for example gacha, shops and maps
│   ├── textmaps/   # Folder where textmaps are stored, the bot uses these for localisations
│   ├── database/   # Allow the bot to connect to database and manage it
│   ├── admin/      # Additional admin logics to assist the web_local admin dash pages
│   ├── game/       # Migrated core logics for the main game from i3 versions, now fully separated from commands
│   ├── utils/      # Additional utility tools for the bot to execute certain sub-functions of commands
│   └── ???/        # Additional folders containing future features   
├── web_local/      # Local admin GUI (config management, server control)
│   ├── app.py                  # To launch the admin dash page at specified port
│   ├── templates/
│   │   ├── base.html           # Common layout (nav-tabs, footer)
│   │   ├── index.html          # Home/dashboard overview
│   │   ├── config.html         # Page for main configs (root/config.json)
│   │   ├── servers.html        # For switching on/off of core and adapters
│   │   ├── admin.html          # To use admin commands/functions (e.g. Edit player's values, Change player's permissions | i.e. A better GUI to edit the database)
│   │   ├── logs.html           # To view/export logs
│   │   ├── accounts.html       # To control accounts status (e.g. Banning, deactivating, linking manually, etc.) 
│   │   └── database.html       # To query player's information / render info from database in a more user friendly way
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── icons/              # SVG icons for the admin dash pages
│       └── js/
│           ├── config.js       # Logic for config's page
│           └── ...             # Logic for other pages (TBA)
├── web_public/     # Public web portal (account linking, registration)
├── backups/        # Backups of users and items
├── config.json     # Tokens, adapter toggles, DB settings
└── start.py        # Main switch to load core and adapters
```

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

### Core Modules
- **admin/**  
  Additional admin logics to assist the web_local admin dash pages
- **game/**  
  Migrated core logics for the main game from i3 versions, now fully separated from commands
- **commands/**  
  Implements every game feature as plain Python functions:  
  - Account creation & linking (Changing to web GUI in future)
  - Cultivation, hunting, ascending, element system, shop, inventory, status...
- **config/**  
  Additional game configuaations json files, used for gacha, shops, redemption codes and maps...
- **utils/**  
  Additional utility tools for the bot to execute certain sub-functions of commands
    - `account_status.py` Helps the bot to get user's data&status, and then generates markdown texts visuals display of the data
    - `database.py` Back ups user's data, generates universal uid for new uers, ensures value defaults (to prevent errors)
    - `localisation.py` Allows the bot to get localised text and sends them to users
    - `otp.py` Generates the one-time password code for users to link accounts
- **textmaps/**  
  Folder where textmaps are stored, the bot uses these for localisations

  Currently localised for (You are welcomed to contribute if you can):
    - [X] EN
    - [X] CHS
    - [ ] CHT (Partially done)
    - [ ] ???
- **database/**  
  - **connection.py**: MongoDB connection, unified `user_id` generation, backup routines for both `users` and `items` collections  

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

### Platform Adapters

Each adapter translates platform‑specific events into calls into the core:

- **Discord**  
  - Slash commands & legacy prefixes  
  - Modals for account creation & redemption  
  - Embeds for rich responses  
- **Telegram**  
  - Slash commands + inline keyboards  
  - Fallback to text if needed  
- **Matrix**  
  - To be prototyped using a Matrix SDK (e.g. `matrix-nio`)  
  - Uses plain text messages and reply buttons  

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

### Web Interfaces

- **Local admin GUI** (`web_local/`)  
  A Flask-based dashboard running on your local machine (e.g. `http://localhost:11451`) that provides a single-page, tabbed interface for:
  
  1. **Config Management** (`localhost:11451/config`)  
     - Loads `config.json` into a user-friendly form: each key/value rendered as an editable field.  
     - "Save" button sends the updated JSON via Fetch to a POST endpoint, writes back to disk, and displays success feedback—all without reloading the page, and reminds user whether a full restart of `start.py` is required based on the config editted.  

  2. **Server Control** (`localhost:11451/servers`)  
     - Lists the Core process and each enabled adapter (Discord, Telegram, etc.) with toggle switches.  
     - Choosing "Start/Stop" invokes a subprocess or system call to launch or terminate only the required service.
     - Status indicators (green/red dots) show which components are running at a glance.  
     - (Future) Options like "Pause/Resume" similar to docker containers

  3. **Admin Tools** (`localhost:11451/admin`)  
     - A GUI wrapper around the legacy admin commands (e.g. textmap indexing, player data overrides, permission changes).  

  4. **Logs Viewer** (`localhost:11451/logs`)  
     - Streams recent log entries in real time.
     - Buttons to download log files.  
     - Filtering of source of log and severity level.

  5. **Database Browser** (`localhost:11451/database`)  
     - Query `users` (automatically locates item informations in `items` for specified user/owner) collections with filters.  
     - Display results in a paginated table with export options.  

  6. **Account Management** (`localhost:11451/accounts`)  
     - Browse and search player information.
     - Ban/unban, deactivate/reactivate, or manually link third-party IDs.  
     - TBA (Adding when page is done)

  **Technical Highlights**  
  - **Flask Blueprints** organize routes (`admin_bp`).  
  - **Jinja2 Templates** (`base.html`, `index.html`, `config.html`, etc.) provide a consistent nav-tab layout.  
  - **Bootstrap 5** for responsive, polished UI (nav-tabs, cards, badges).  
  - **Static assets** in `static/css` and `static/js` separate styling and client logic.  
  - No external authentication by default (localhost only), but easily bolted on (API key, IP whitelist).  

- **Public portal** (`web_public/`)
  Public domain that allows users to
  - View server status
  - Register new accounts via web form  
  - Link existing accounts with OTP sent to the user’s chat platform  
  - View personal stats, inventory, and more via web  

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Getting Started

### Prerequisites

- Python 3.10+  
- MongoDB  
- (Optional) Docker for containerized deployment

### Installation

**[Internal-3 (i3) {Prebuild}](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)**
1. **Download Prebuild**
    - [Download from releases](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)
    - [Download from cloud drive](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **Unzip and Configure**
    - Unzip the prebuild into any directory you prefer, using [7-Zip (Recommended)](https://www.7-zip.org/)
    - Configure the variables (e.g. Bot Token, admin_ids...) based on the guide in [README.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/0-Releases/LTS/OSBLTSDiscord_pre-3.0.2/README.txt)
3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```
4. **Run**
   ```sh
   python bot.py
   ```

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

===================================

**Internal-4 (i4) And Above {Under Development}**
1. **Clone the repo**  
   ```sh
   git clone https://github.com/aosumi-rena/XiuXianBot.git
   cd XiuXianBot
   ```
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure**
   - Edit `config.json` with your MongoDB URI, Discord & Telegram tokens, and etc. to run
   
   **[config.json](https://github.com/aosumi-rena/XiuXianBot/blob/main/config_example_EN.json.txt) sample**:
   ```
   {
    "admin_panel": {                                          # Settings about the admin dashboard
      "port": 11451,                                          # Port for the dashboard to run on
      "api_switch": false,                                    # Whether to accept api request (This is for advanced users, keep this off if you only control the servers manually at the port) [Pending development, unable to use for now]
      "api_with_password": true,                              # Whether api request needs password
      "api_password": "123456"                                # Password for api requests
     },
    "adapters": {                                             # Select which platforms would you like to run the bot(s) on
      "discord": true,
      "telegram": true,
      "matrix": true
     },
    "tokens": {                                               # Tokens/Authentication for your bots
      "discord_token": "MTE...",                              # Your Discord Bot token, you can get it from Discord Dev Portal `https://discord.com/developers/applications`
      "telegram_token": "12345....",                          # Your Telegram Bot token, you can get it from BotFather `https://t.me/BotFather`

      "matrix_server_address": "https://matrix.example.com",  # Address to your matrix server (If you are not the Matrix server owner, plese check with the owner that they are *NOT* banning bots from logging-in with normal user's authentication, this program is not responsible if you are banned!)
      "matrix_ID": "@XiuXianBot:matrix.example.com",          # "Username" of your bot account
      "matrix_pass": "123456"                                 # Password of your bot's account
     },
    "db": {                                                   # Database configurations
      "mongo_uri": "mongodb://localhost:27017",               # URI to your MongoDB, usually it is `mongodb://localhost:27017`
      "mongo_db_name": "XiuXianBotV4",                        # Name of your MongoDB database for the bots to store information on
      "universal_uid_start": 1000000                          # Sets the starting universal uid generation value, "1000000" means the first user will get "1000001" for their uid
     }
   }
   ```
4. **Start the local admin dashboard webpage**
   ```sh
   python start.py
   ```
   This will start the local web admin panel in your preset port, open the webpage in browser for final check and configurations
5. **Start the bot on respective servers/platforms**

   Once everything is configured correctly and checked, start the servers (platforms) you need in the admin panel webpage
<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

### Usage
Once running, the bot will:
- Provide a local web dashboard at http://localhost:11451 (By default, you may change it in config.json) for admin control.

Select the servers/platforms you need the bot to run on, and the it will then
- Connect to Discord and respond to ^start, ^cul, ^hunt, ^asc, ^ele, /shop, etc.
- Connect to Telegram (if enabled) and mirror the same commands slash commands.
- Connect to Matrix (if enabled) and ??? (Matrix is not prototyped, unable to provide possible results here).

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Roadmap

### Core
* [X] Refactor core logic into **core/** package
* [ ] Create command listener and response logics in **core/commnads/**
* [ ] Implement **Discord** adapter
* [ ] Add **Telegram** adapter with slash commands
* [ ] Prototype **Matrix** adapter
* [X] Build **web\_local** admin GUI
* [ ] Build **web\_public** portal for account linking
* [ ] Dockerize entire application

### Game Functions
* [ ] Buff systems and consumable items
* [ ] Equipment system
* [ ] Mail function
* [ ] Exploration system (map)
* [ ] Alternate cultivating pathways
* [ ] Battle system (turn-based)
* [ ] Gacha system
* [ ] Trading system

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Contributing

- All contributions are welcomed, you may make pull requests or post any issues if you would like to contribute
- For localisation, a Weblate site will be hosted for public contributions

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## License

XiuXianBot ©2024-2025 By Aosumi Rena

This program comes with ABSOLUTELY NO WARRANTY; for details, see [LICENSE.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/LICENSE.txt).

This is free software, and you are welcome to redistribute it under the terms of the GNU GPL v3.0.

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Contact

Aosumi Rena – [rena.aosumi@mihoyo.day](mailto:rena.aosumi@mihoyo.day)

Project Link: [https://github.com/aosumi-rena/XiuXianBot/](https://github.com/aosumi-rena/XiuXianBot)

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Acknowledgments
### AI
* [OpenAI](https://chat.openai.com) - General assistance
* [Deepwiki](https://deepwiki.com) - Documentation
### Inspirations
* [BlueArchiveGM](https://github.com/PrimeStudentCouncil/BlueArchiveGM) - Provide inspirations about the admin dash page design
### Media
* [api.tomys.top](https://tomys.top) - Random anime background image (for local admin dashboard)

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

---

## Others

### Star History

<a href="https://www.star-history.com/#aosumi-rena/XiuXianBot&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=aosumi-rena/XiuXianBot&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=aosumi-rena/XiuXianBot&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=aosumi-rena/XiuXianBot&type=Date" />
 </picture>
</a>

<p align="right">(<a href="#readme-top">back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md">简中</a>)</p>

<!-- URL -->
[downloads-shield]: https://img.shields.io/github/downloads/aosumi-rena/XiuXianBot/total?logo=github&style=flat-square
[downloads-url]: https://github.com/aosumi-rena/XiuXianBot/releases/latest

[contributors-shield]: https://img.shields.io/github/contributors/aosumi-rena/XiuXianBot.svg?style=for-the-badge
[contributors-url]: https://github.com/aosumi-rena/XiuXianBot/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/aosumi-rena/XiuXianBot.svg?style=for-the-badge
[forks-url]: https://github.com/aosumi-rena/XiuXianBot/network/members

[stars-shield]: https://img.shields.io/github/stars/aosumi-rena/XiuXianBot.svg?style=for-the-badge
[stars-url]: https://github.com/aosumi-rena/XiuXianBot/stargazers

[issues-shield]: https://img.shields.io/github/issues/aosumi-rena/XiuXianBot.svg?style=for-the-badge
[issues-url]: https://github.com/aosumi-rena/XiuXianBot/issues

[license-shield]: https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=for-the-badge
[license-url]: https://www.gnu.org/licenses/gpl-3.0
