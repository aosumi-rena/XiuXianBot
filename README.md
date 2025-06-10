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

![Alt](https://repobeats.axiom.co/api/embed/b40285fbd34567583dc0df228cace66b09a6552c.svg "Repobeats analytics image")

**README Variations**

[简体中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#关于) | [English](https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#readme-top)

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#readme-top">简中</a>)</p>

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
          <ul>
            <li><a href="#docker">Docker Installation</a></li>
            <li><a href="#build">Self Build</a></li>
          </ul>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
      <ul>
        <li><a href="#core">Core</a></li>
        <li><a href="#game-functions">Game Functions</a></li>
      </ul>
    <li><a href="#contributing">Contributing</a></li>
      <ul>
        <li><a href="#contributors">Contributors List</a></li>
      </ul>
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
XiuXianBot is a cultivation-themed RPG text-based game bot originally built for Discord, and hopefully turn into a cross-platform version in future. It will contain:

- A **core** library containing all game logic, database models, and localization.
- Multiple **adapters** for different chat platforms (Discord, Telegram, Matrix…).
- **Web interfaces** for admin control and public account management.
- A **single bootstrap** (`start.py`) that loads configuration and starts the desired adapters.

### Recent Updates (AI generated, pending checks)

- Admin dashboard now uses modal dialogs for most actions.
- Database browser table features Copy ID, Ban and Deactivate controls.
- Telegram adapter correctly renders Markdown-formatted messages.
- Core storage migrated to SQLite; SQLite (built-in; automatically created) is no longer required.

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#关于">简中</a>)</p>

---

## Architecture

### File Structure
```
root/
├── adapters/
│   ├── discord/    # Discord-specific commands, modals, embeds
│   |   └── bot.py              # To activate the bot
│   ├── telegram/   # Telegram slash commands, inline keyboards
│   |   └── bot.py              # To activate the bot
│   ├── matrix/     # Matrix (future)
│   |   └── bot.py              # To activate the bot
│   └── ???/        # More platforms (future)
├── core/
│   ├── commands/   # Game commands (hunt.py, cul.py, asc.py, account.py, ele.py, etc.), which decides how the bot will react
│   ├── config/     # Additional game configurations, for example gacha, shops and maps
│   ├── textmaps/   # Folder where textmaps are stored, the bot uses these for localizations
│   ├── database/   # Allow the bot to connect to database and manage it
│   ├── admin/      # Additional admin logics to assist the web\_local admin dash pages
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
│   │   ├── admin.html          # To use admin commands/functions (e.g. Edit player's values, Change player's permissions)
│   │   ├── logs.html           # To view/export logs
│   │   ├── accounts.html       # To control accounts status (e.g. Banning, deactivating, linking manually, etc.)
│   │   └── database.html       # To query player's information / render info from database in a more user friendly way
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── icons/              # SVG icons for the admin dash pages
│       └── js/
│           ├── config.js       # Logic for config's page
│           └── ...             # Additional logic files
├── web_public/     # Public web portal (account linking, registration)
├── backups/        # Backups of users and items
├── config.json     # Tokens, adapter toggles, DB settings
└── start.py        # Main switch to load core and adapters
```

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#文件结构">简中</a>)</p>

### Core Modules
- **admin/**  
  Additional admin logics to assist the web_local admin dash pages.
- **game/**  
  Migrated core logics for the main game from i3 versions, now fully separated from commands.
- **commands/**  
  Implements every game feature as plain Python functions:  
  - Account creation & linking (switching to web GUI in future).
  - Cultivation, hunting, ascending, element system, shop, inventory, status...
- **config/**  
  Additional game configurations (JSON files for gacha, shops, redemption codes, maps...).
- **utils/**  
  Additional utility tools for the bot to execute certain sub-functions of commands:
    - `account_status.py` helps the bot retrieve user data/status and generate Markdown‐formatted data output.
    - `database.py` handles backups, universal UID generation, and default values (to prevent errors).
    - `localisation.py` fetches localized text and sends it to users.
    - `otp.py` generates one-time passwords for account linking.
- **textmaps/**  
  Folder where textmaps are stored, the bot uses these for localizations.  
  Currently localized for (you’re welcome to contribute):  
    - [X] EN  
    - [X] CHS  
    - [ ] CHT (Partially done)  
    - [ ] ???  
- **database/**  
  - **connection.py**: SQLite connection factory and helpers for automatic table creation.

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#核心模块">简中</a>)</p>

### Platform Adapters
Each adapter translates platform-specific events into calls into the core and formats core responses for that platform:

- **Discord**  
  - Slash commands & legacy prefixes.  
  - Modals for account creation & redemption codes.  
  - Embeds for rich, formatted responses.
- **Telegram**  
  - Slash commands + inline keyboards.  
  - Fallback to plain text if necessary.
  - Messages now correctly support Markdown formatting.
- **Matrix**  
  - (Future) Prototyped using a Matrix SDK (e.g. `matrix-nio`).  
  - Uses plain text messages and reply buttons.

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#平台适配器">简中</a>)</p>

### Web Interfaces
- **Local admin GUI** (`web_local/`)  
  A Flask-based dashboard running on your local machine (e.g. `http://localhost:11451`) that provides a single-page, tabbed interface for:  
  - Modal dialogs are used for editing and confirmations.
  1. **Config Management** (`localhost:11451/config`)  
     - Loads `config.json` into a user-friendly form; each key/value appears as an editable field.  
     - “Save” button sends updated JSON via Fetch to a POST endpoint, writes back to disk, and displays a success feedback—all without reloading the page, and reminds the user if a full restart of `start.py` is required.  
  2. **Server Control** (`localhost:11451/servers`)  
     - Lists the Core process and each enabled adapter (Discord, Telegram, etc.) with toggle switches.  
     - Clicking “Start/Stop” launches or terminates the required service.  
     - Status indicators (green/red dots) show which components are running at a glance.  
     - (Future) Options like “Pause/Resume” similar to Docker containers.  
  3. **Admin Tools** (`localhost:11451/admin`)  
     - GUI wrapper around legacy admin commands (e.g. textmap indexing, player data overrides, permission changes).  
  4. **Logs Viewer** (`localhost:11451/logs`)  
     - Streams recent log entries in real time.  
     - Buttons to download log files.  
     - Filter by log source and severity.  
  5. **Database Browser** (`localhost:11451/database`)  
     - Query `users` (automatically joins `items` collection info) with filters.  
     - Displays results in a paginated table with export options.  
     - Each row provides Copy ID, Ban and Deactivate controls.
     - See [docs/sqlite_guide.md](docs/sqlite_guide.md) for tips on editing the SQLite database.
  6. **Account Management** (`localhost:11451/accounts`)  
     - Browse and search player information.  
     - Ban/unban, deactivate/reactivate, or manually link third-party IDs.  
     - TBA (to be added when page is done).  
  **Technical Highlights**  
  - **Flask Blueprints** organize routes (`admin_bp`).  
  - **Jinja2 Templates** (`base.html`, `index.html`, `config.html`, etc.) provide a consistent nav-tab layout.  
  - **Bootstrap 5** for responsive, polished UI (nav-tabs, cards, badges).  
  - Static assets in `static/css` and `static/js` separate styling and client logic.  
  - No external authentication by default (localhost only), but easily bolted on (API key, IP whitelist).  
- **Public portal** (`web_public/`)  
  Public domain that allows users to:  
  - View server status.  
  - Register new accounts via web form.  
  - Link existing accounts with OTP sent to the user’s chat platform.  
  - View personal stats, inventory, and more via web.

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#网页界面">简中</a>)</p>

---

## Getting Started

### Prerequisites

**Docker Deployment**:  
- Docker (obviously)

**Self Build**:  
- Python 3.12+  
- SQLite (built-in; automatically created)
- MongoDB (For `i3` version)

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#快速上手">简中</a>)</p>

### Installation

#### Docker
&&& This Section Is Incomplete &&&  
**Official Releases (`OSRELDocker1.0.0_*` and above) {Under Development}**  
1. **Clone the repo**  
   ```sh
   git clone https://github.com/aosumi-rena/XiuXianBot.git
   cd XiuXianBot
   ```

2. **Configure**

   * Edit `docker-compose.yml`: Add your Discord & Telegram tokens to the environment, and edit other environment variables if needed.
     **[docker-compose.yml](https://github.com/aosumi-rena/XiuXianBot/blob/main/docker-compose.yml) sample**:

   ```yaml
   # Temporary placeholder, may not be the same after real release
   services:
     xiu-xian-bot:
       image: aosumi-rena/xiu-xian-bot:latest
       environment:
         - DISCORD_TOKEN=YOUR_DISCORD_TOKEN
         - TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN
       ports:
         - "11451:11451"
       volumes:
         - ./config.json:/app/config.json
   ```
3. **Docker compose**

   ```sh
   docker-compose up -d
   ```
4. **Start the local admin dashboard webpage**  
   Once compose is up, the required containers start automatically.
   
   Then open your browser to the configured port (e.g. `http://localhost:11451`) to check/finalize settings.
5. **Start the bot on respective servers/platforms**  
   From the local admin panel, enable whichever platform adapters you need (Discord, Telegram, etc.), and the containers covering those adapters will launch.

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#docker">简中</a>)</p>

#### Self Build

**Pre-release: [Internal-3 (i3)](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)**

1. **Download Prebuild**

   * [Download from releases](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)
   * [Download from cloud drive](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **Unzip and Configure**

   * Unzip the prebuild into any directory (7-Zip recommended).
   * Configure variables (Bot Token, `admin_ids`, etc.) per the instructions in [README.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/0-Releases/LTS/OSBLTSDiscord_pre-3.0.2/README.txt).
3. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```
4. **Run**

   ```sh
   python bot.py
   ```

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#自建">简中</a>)</p>

---

### Usage

Once running, the bot will:

* Provide a local web dashboard at `http://localhost:11451` (by default; you may change this in `config.json`) for admin control.
* The core game server listens on `http://localhost:11450` by default.
* In that dashboard, enable whichever servers/platforms you need, and then:

  * Connect to Discord and respond to `^start`, `^cul`, `^hunt`, `^asc`, `^ele`, `/shop`, etc.
  * Connect to Telegram (if enabled) and mirror the same slash commands.
  * Connect to Matrix (if enabled; prototyping in progress).

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#使用">简中</a>)</p>

---

## Roadmap

### Core

* [x] Refactor core logic into **core/** package
* [ ] Create command listener and response logic in **core/commands/**
* [ ] Re-construct the core server using `C#`
* [X] Implement **Discord** adapter
* [X] Add **Telegram** adapter with slash commands
* [ ] Prototype **Matrix** adapter
* [x] Build **web\_local** admin GUI
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

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#后续">简中</a>)</p>

---

## Contributing

* All contributions are welcome: make pull requests or open issues if you want to help improve the project.
* For localization, a Weblate site will be hosted for public contributions.

### Contributors

<table cellpadding="0" cellspacing="0">
  <tr>
    <td valign="middle">
      <a href="https://github.com/aosumi-rena" target="_blank">
        <img
          src="https://github.com/aosumi-rena.png"
          alt="Aosumi Rena’s GitHub avatar"
          width="50"
          height="50"
          style="border-radius:50%;"
        />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em;">
      <p style="margin:0;">Project Leader | Game Logic Codes | Local Admin Dash HTML</p>
    </td>
  </tr>

  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/Columbina-Dev" target="_blank">
        <img
          src="https://github.com/Columbina-Dev.png"
          alt="Columbina’s GitHub avatar"
          width="50"
          height="50"
          style="border-radius:50%;"
        />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;">Game Mechanism Designer | Discord Adapter | Database w/r Logics | Localisations</p>
    </td>
  </tr>

  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/ThirtySeven377" target="_blank">
        <img
          src="https://github.com/ThirtySeven377.png"
          alt="ThirtySeven377’s GitHub avatar"
          width="50"
          height="50"
          style="border-radius:50%;"
        />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;">Telegram Adapter | Documentations</p>
    </td>
  </tr>
</table>

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#贡献者">简中</a>)</p>

---

## License

[![License](https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/GPLv3_Logo.svg/330px-GPLv3_Logo.svg.png)](https://www.gnu.org/licenses/gpl-3.0)

XiuXianBot ©2024-2025 By Aosumi Rena

This program comes with ABSOLUTELY NO WARRANTY; for details, see [LICENSE.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/LICENSE.txt).

This is free software, and you are welcome to redistribute it under the terms of the GNU GPL v3.0.

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#许可">简中</a>)</p>

---

## Contact

Aosumi Rena – [rena.aosumi@mihoyo.day](mailto:rena.aosumi@mihoyo.day)

Project Link: [https://github.com/aosumi-rena/XiuXianBot/](https://github.com/aosumi-rena/XiuXianBot)

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#联系">简中</a>)</p>

---

## Acknowledgments

### AI

* [OpenAI](https://chat.openai.com) – General assistance
* [Deepwiki](https://deepwiki.com) – Documentation

### Inspirations

* [BlueArchiveGM](https://github.com/PrimeStudentCouncil/BlueArchiveGM) – Provided inspiration for the admin dash design

### Media

* [api.tomys.top](https://tomys.top) – Random anime background image (for local admin dashboard)

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#致谢">简中</a>)</p>

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

<p align="right">(<a href="#readme-top">Back to top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#star-历史">简中</a>)</p>

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
