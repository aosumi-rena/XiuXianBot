<a id="readme-top"></a>
# XiuXianGame Bot
A text-based game Bot which supports both Telegram and Discord (Matrix and more in future) at the same time, by running in a universal core logic with adapters to other platforms, all sharing the same game engine and database.

**README Variations**

[简体中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md) | [English](https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

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
  </ol>
</details>

---

## About The Project

XiuXianBot is a cultivation‑themed RPG text-based game bot originally built for Discord, and hopefully turn into a cross-platform version in future, it will contain:

- A **core** library containing all game logic, database models, and localization.
- Multiple **adapters** for different chat platforms (Discord, Telegram, Matrix…).
- Optional **web interfaces** for admin control and public account management.
- A **single bootstrap** (`start.py`) that loads configuration and starts the desired adapters.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Architecture

### File Structure
```
root/
├── core/
│ ├── commands/   # Game commands (hunt.py, cul.py, asc.py, account.py, ele.py, etc.)
│ ├── admin/      # Admin utilities (textmap indexing, stats, backups)
│ └── utils/      # DB models, localization, calculations, ID generation
│ └── ???/        # Additional folders containing future features   
├── adapters/
│ ├── discord/    # Discord‑specific commands, modals, embeds
│ ├── telegram/   # Telegram slash commands, inline keyboards
│ └── matrix/     # Matrix (future)
│ └── ???/        # More platforms (future)
├── web_local/    # Local admin GUI (config management, server control)
├── web_public/   # Public web portal (account linking, registration)
├── backups/      # Backups of users and items
├── config.json   # Tokens, adapter toggles, DB settings
└── start.py        # Main switch to load core and adapters
```

### Core Modules

- **commands/**  
  Implements every game feature as plain Python functions:  
  - Account creation & linking (Changing to web GUI in future)
  - Cultivation, hunting, ascending, element system, shop, inventory, status...
- **admin/**  
  Legacy admin tools by using commands (Changing to local web admin GUI in future)
- **utils/**  
  - **database.py**: MongoDB connection, unified `user_id` generation, backup routines for both `users` and `items` collections  
  - **localisation.py**: load JSON textmaps (multi‑language support) 
  - **???.py**: More functions in future...

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

### Web Interfaces

- **Local admin GUI** (`web_local/`)  
  - Manage `config.json`, start/stop adapters, view server logs, utilise the original admin commands in a convenient way.
- **Public portal** (`web_public/`)  [Public domain]
  - Register new accounts  
  - Link existing accounts via OTP sent to chat platforms  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started
&&&This Section is WIP&&&
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
4. **Run**
   ```sh
   python start.py
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

### Usage
Once running, the bot will:
- Connect to Discord and respond to ^start, ^cul, ^hunt, ^asc, ^ele, /shop, etc.
- Connect to Telegram (if enabled) and mirror the same slash commands.
- Provide a local web dashboard at http://127.0.0.1:11451 for admin control.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Roadmap

### Core
* [ ] Refactor core logic into **core/** package
* [ ] Implement **Discord** adapter
* [ ] Add **Telegram** adapter with slash commands
* [ ] Prototype **Matrix** adapter
* [ ] Build **web\_local** admin GUI
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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contributing

&&&TBA&&&

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## License

&&&TBA&&&

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contact

Aosumi Rena – [rena.aosumi@mihoyo.day](mailto:rena.aosumi@mihoyo.day)

Project Link: [https://github.com/aosumi-rena/XiuXianBot/](https://github.com/aosumi-rena/XiuXianBot)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Acknowledgments

&&&TBA&&&

<p align="right">(<a href="#readme-top">back to top</a>)</p>
