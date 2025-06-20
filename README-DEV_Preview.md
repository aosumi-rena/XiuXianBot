# What's this?
This is a preview of the README file for the private XiuXianBotDev repo, which is the development build of this project.
It is to provide a quick overview of the future features and architecture of the XiuXianBot project.
It is not the final version and may contain incomplete or placeholder content.

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
A cultivation-themed text-based RPG game bot supporting multiple platforms (Discord, Telegram, Matrix, and more) via a unified **C# core server** and **Python adapters**, sharing the same game engine and SQLite database.

![Alt](https://repobeats.axiom.co/api/embed/b40285fbd34567583dc0df228cace66b09a6552c.svg "Repobeats analytics image")

**README Variations**

[English](https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#readme-top) | [简体中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#readme-top) | [繁體中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#readme-top) | [日本語](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#readme-top)

<p align="right">
(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#about-the-project">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#关于">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#修仙機器人">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#修仙ゲームbot">日</a>)
</p>

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
          <li><a href="#prerequisites">Prerequisites</a>
          <li><a href="#installation">Installation</a>
            <ul>
              <li><a href="#docker-installation">Docker Installation</a></li>
              <li><a href="#self-build">Self Build</a></li>
            </ul>
          <li><a href="#older-versions">Older Versions</a>
        </ul>
      </li>
      <li><a href="#usage">Usage</a></li>
      <li><a href="#roadmap">Roadmap</a>
        <ul>
          <li><a href="#core">Core</a></li>
          <li><a href="#game-functions">Game Functions</a></li>
        </ul>
      </li>
      <li><a href="#contributing">Contributing</a>
        <ul>
          <li><a href="#contributors-list">Contributors List</a></li>
        </ul>
      </li>
      <li><a href="#license">License</a></li>
      <li><a href="#contact">Contact</a></li>
      <li><a href="#acknowledgments">Acknowledgments</a>
        <ul>
          <li><a href="#ai">AI</a></li>
          <li><a href="#inspirations">Inspirations</a></li>
          <li><a href="#media-resources">Media Resources</a></li>
        </ul>
      </li>
      <li><a href="#others">Others</a></li>
        <ul>
          <li><a href="#star-history">Star History</a></li>
        </ul>
      </li>
    </ol>
  </details>

---

## About The Project
XiuXianBot is a cultivation-themed RPG text-based game bot originally built for Discord, now refactored into a **client-server** architecture using a high-performance **C# core server** and lightweight Python adapters. It features:

- A **C# Core Server** (ASP.NET Core) handling all game logic, database access (SQLite), and localization.
- **Python adapters** for each chat platform (Discord, Telegram, Matrix, etc.) that translate user commands into HTTP API calls.
- A **local admin dashboard** (Flask) for configuration, service control, logs, and data browsing.
- A **public web portal** (in development) for account linking and player self-service.
- A single bootstrap (`start.py`) for non-Docker setups, and a Docker Compose configuration for containerized deployments.

### Recent Updates
- **Core Rewrite**: Game engine moved from Python to a C# ASP.NET Core Web API for higher concurrency and lower latency.
- **Docker Single-Container**: All components (`core-server`, adapters, admin-dashboard) run within a single container for simplified deployment.
- **SQLite**: Default persistence is SQLite; no MongoDB required.
- **Hot-Reloadable Config**: Admin UI can reload core configuration at runtime without full restart.
- **Localization**: Full EN, CHS, CHT support in core; JP partial with README now fully translated.

<p align="right">(<a href="#readme-top">回到頂部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#about-the-project">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#关于">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#關於">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#概要">日</a>)</p>

---

## Architecture

XiuXianBot now uses a modular, client-server design: Python adapters communicate with the C# core server over HTTP, with all services running inside a single container for easy deployment.

```
[Discord / Telegram / Matrix Clients]

                │
                ▼

    Python Platform Adapters

                │  (HTTP)
                ▼

   C# Core Server (ASP.NET Core)

                │  (SQLite)
                ▼

      SQLite Database File
```

### File Structure
```
root/
├── adapters/           # Python adapters for each chat platform
│   ├── discord/        # Discord adapter (discord.py)
│   │   └── bot.py
│   ├── telegram/       # Telegram adapter (python-telegram-bot)
│   │   └── bot.py
│   ├── matrix/         # Matrix adapter (future)
│   │   └── bot.py
│   └── ...             # More platforms
│
├── server/             # C# core server (ASP.NET Core project)
│   ├── program.cs      # Main server script
│   ├── controllers/    # API controllers (endpoints)
│   ├── models/         # Data models (Player, Item, etc.)
│   ├── services/       # Game logic services (Cultivation, Shop, etc.)
│   └── data/           # DB migration scripts / SQLite schema
│
├── web_local/          # Local admin dashboard (Flask)
│   ├── app.py          # Flask application entry
│   ├── templates/      # Jinja2 templates (config.html, logs.html, etc.)
│   └── static/         # CSS/JS/icons for dashboard
│
├── web_public/         # Public web portal (in development)
│   └── ...
│
├── data/               # Shared volume for SQLite database
│   └── xiu_xian.db
│
├── config.json         # Unified configuration (tokens, feature toggles, DB path)
├── docker-compose.yml  # Multi-container orchestration
├── requirements.txt    # Python dependencies
├── start.py            # Bootstrap script for non-Docker runs
└── LICENSE.txt         # GPL-3.0 license
```

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#architecture">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#文件结构">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#檔案結構">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#ファイル構成">日</a>)</p>

### Core Modules
- **C# Core Server** (`Server/`)
  - **Controllers**: Defines HTTP endpoints for game actions (e.g., `/api/cultivate/start`).
  - **Services**: Implements game mechanics (cultivation, hunting, ascending, shop, inventory, etc.).
  - **Models**: Strongly-typed DTOs and entities for players, items, timers.
  - **Data Layer**: Uses Microsoft.Data.Sqlite or Dapper for efficient SQLite access; auto-migrates schema.
  - **Localization**: Loads JSON text maps for EN, CHS, CHT, and returns localized messages.

- **Python Adapters** (`adapters/`)
  - Receive platform-specific events (slash commands, buttons).
  - Call core server APIs via HTTP (with `API_SECRET` auth header).
  - Format JSON responses into platform messages (Embeds for Discord, Markdown for Telegram).

- **Admin Dashboard** (`web_local/`)
  - **Config**: Edit `config.json` via modal forms; send updates to core for hot reload.
  - **Servers**: Show status of core and adapters; send start/stop signals to containers or processes.
  - **Admin Tools**: One-click operations (textmap rebuild, user data override).
  - **Logs**: Stream and download logs from core and adapters.
  - **Database**: Query users and inventory; ban/unban/deactivate from UI.

- **Public Portal** (`web_public/`)
  - Planned for player self-service: account registration, OTP linking, stat view via web UI.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#core-modules">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#核心模块">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#核心模組">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#コアモジュール">日</a>)</p>

### Platform Adapters
Each adapter translates platform events into HTTP API calls and renders responses:

- **Discord**
  - Slash commands & legacy-prefix support.
  - Modal dialogs for account linking.
  - Rich Embeds for game status and actions.
- **Telegram**
  - Slash commands + inline keyboards.
  - Markdown-formatted messages.
- **Matrix** (planned)
  - Using a Matrix SDK for future support.
  - Plain-text messages with reply buttons.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#platform-adapters">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#平台适配器">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#平台適配器">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#プラットフォームアダプター">日</a>)</p>

### Web Interfaces
- **Local Admin GUI** (`web_local/`)
  - Flask app on `localhost:11451` by default.
  - Tabbed SPA with:
    1. **Config**: Edit and hot-reload `config.json`.
    2. **Servers**: Start/stop core & adapters (via HTTP signals or Docker API).
    3. **Admin Tools**: Execute maintenance commands.
    4. **Logs**: Real-time log streaming & download.
    5. **Database**: Query players, ban/deactivate via UI.
    6. **Accounts**: Manual platform linking & account management.
- **Public Portal** (`web_public/`) – upcoming web UI for players.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#web-interfaces">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#网页界面">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#網頁介面">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#ウェブインターフェース">日</a>)</p>


---

## Getting Started

### Prerequisites

**Docker Deployment**  
- Docker Engine (v20+ recommended)  
- Docker Compose v2+  

**Self Build**  
- Python 3.12+ (adapters & admin GUI)  
- .NET 7 SDK (core server)  
- SQLite (built into .NET & Python)  

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#getting-started">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#快速上手">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#快速上手">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#はじめに">日</a>)</p>

### Installation
**For Official Releases (`OSRELDocker1.0.0_*` and above) {Under Development}**    
#### Docker Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/aosumi-rena/XiuXianBot.git
   cd XiuXianBot
   ```

2. **Configure**
   Edit `config.json` or supply environment variables in `docker-compose.yml` for:

   * `DISCORD_TOKEN`, `TELEGRAM_TOKEN`, `API_SECRET`
   * Optional: `CORE_SERVER_PORT`, database path, feature toggles

3. **Start service**

   ```bash
   docker-compose up -d
   ```

   This brings up the core server, adapters, and admin dashboard in a single container.

4. **Access Admin UI**
   Visit `http://localhost:11451` to verify settings, hot-reload config, and control services.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#docker-installation">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#docker部署">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#docker部署">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#ドッカーによる部署">日</a>)</p>

#### Self Build

1. **Clone & configure**
   ```bash
   git clone https://github.com/aosumi-rena/XiuXianBot.git
   cd XiuXianBot
   ```

   and edit `config.json`.

2. **Install Python deps**

   ```bash
   pip install -r requirements.txt
   ```

3. **Build C# core**

   ```bash
   cd Server
   dotnet build -c Release
   ```

4. **Run core server**

   ```bash
   cd Server
   dotnet run -c Release
   ```

5. **Run adapters & admin UI**
   In repo root:

   ```bash
   python start.py
   ```

6. **Open Admin UI**
   Visit `http://localhost:11451` and enable adapters as needed.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#self-build">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#自建">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#自建">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#セルフビルド">日</a>)</p>


### Older Versions

**Pre-release: [OSBLTSDocker0.1.52](https://github.com/aosumi-rena/XiuXianBot/releases/tag/v0.1.52-LTS)**

1. **Download Prebuild**  

   * [Download from releases](https://github.com/aosumi-rena/XiuXianBot/releases/tag/v0.1.52-LTS)
   * [Download from cloud drive](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **Unzip and Configure**

   * Unzip the prebuild into any directory ([7-Zip](https://www.7-zip.org/) recommended).
   * Configure variables (Bot Token, etc.) in the `config.json`
3. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```
4. **Run**

   ```sh
   python start.py
   ```
   
5. **Start the local admin dashboard webpage**  
   Once the running, it opens the port  `11451` as local admin dashboard.  
   Open your browser to the configured port (e.g. `http://localhost:11451`) to check/finalize settings.  
6. **Start the bot on respective servers/platforms**  
   From the local admin panel, enable whichever platform adapters you need (Discord, Telegram, etc.), and the containers covering those adapters will launch.  
   
==================================================

**Pre-release: [Internal-3 (i3)](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)**

1. **Download Prebuild**  

   * [Download from releases](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)
   * [Download from cloud drive](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **Unzip and Configure**

   * Unzip the prebuild into any directory ([7-Zip](https://www.7-zip.org/) recommended).
   * Configure variables (Bot Token, `admin_ids`, etc.) refering to the instructions in [README.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/0-Releases/LTS/OSBLTSDiscord_pre-3.0.2/README.txt).
3. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```
4. **Run**

   ```sh
   python bot.py
   ```

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#older-versions">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#旧版本">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#舊版本">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#旧バージョン">日</a>)</p>

---

## Usage

Once running:

* **Admin Dashboard** at `http://localhost:11451` — configure & control.
* **Core API** on `http://localhost:11450` — adapters call endpoints.
* **Discord**: Bot responds to `/start`, `/cul`, `/hunt`, `/ascend`, `/shop`, etc.
* **Telegram**: Same slash commands, with inline buttons.
* **Matrix**: (when enabled) similar interface.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#usage">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#使用">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#使用">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#使い方">日</a>)</p>

---

## Roadmap

### Core

* [x] Refactor core logic into C# ASP.NET Core server
* [x] Implement HTTP API endpoints for all game actions
* [x] Containerize with Docker Compose
* [x] Python adapters for Discord & Telegram
* [ ] Prototype Matrix adapter
* [ ] Develop public web portal
* [ ] Explore live script/hot-reload for game logic

### Game Functions

* [ ] Buff & consumable item system
* [ ] Equipment & gear upgrade
* [ ] In-game mail system
* [ ] Exploration & map mechanics
* [ ] Multiple cultivation paths
* [ ] Turn-based battle system
* [ ] Gacha/lottery draws
* [ ] Player trading & marketplace

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#roadmap">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#后续">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#後續">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#今後の計画">日</a>)</p>
---

## Contributing

All contributions are welcome! Fork, fix, and submit a pull request, or open an issue for discussion.

### Contributors List

#### Key Contributors

<table cellpadding="0" cellspacing="0">
  <tr>
    <td valign="middle">
      <a href="https://github.com/aosumi-rena" target="_blank">
        <img src="https://github.com/aosumi-rena.png" width="50" height="50" style="border-radius:50%;" />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em;">
      <p style="margin:0;"><b>Aosumi Rena</b></p>
    </td>
    <td valign="middle" style="padding-left:0.5em;">
      <p style="margin:0;">Project Leader & Core Architect</p>
    </td>
  </tr>
  
  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/Columbina-Dev" target="_blank">
        <img src="https://github.com/Columbina-Dev.png" width="50" height="50" style="border-radius:50%;" />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;"><b>Columbina-Dev</b></p>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;">Game Mechanic Designer & Discord Adapter</p>
    </td>
  </tr>

  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/ThirtySeven377" target="_blank">
        <img src="https://github.com/ThirtySeven377.png" width="50" height="50" style="border-radius:50%;" />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;"><b>ThirtySeven377</b></p>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;">Telegram Adapter & Documentation</p>
    </td>
  </tr>

  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/" target="_blank">
        <img src="https://placehold.co/256x256/png" width="50" height="50" style="border-radius:50%;" />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;"><b>？？？</b></p>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <p style="margin:0;">Constant Values Designer & Tester</p>
    </td>
  </tr>
</table>

#### Full Contributors

[![Contributors](https://contrib.nn.ci/api?repo=aosumi-rena/XiuXianBot)](https://github.com/aosumi-rena/XiuXianBot/graphs/contributors)

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#contributors">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#贡献者名单">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#貢獻者名單">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#貢献者リスト">日</a>)</p>

---

## License

[![License](https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/GPLv3_Logo.svg/330px-GPLv3_Logo.svg.png)](https://www.gnu.org/licenses/gpl-3.0)

XiuXianBot ©2024–2025 Aosumi Rena

This program is licensed under the GNU GPL v3.0. See [LICENSE.txt](LICENSE.txt) for details.

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#license">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#许可">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#授權">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#ライセンス">日</a>)</p>

---

## Contact

Aosumi Rena – [rena.aosumi@mihoyo.day](mailto:rena.aosumi@mihoyo.day)

Project Link: [github.com/aosumi-rena/XiuXianBot](https://github.com/aosumi-rena/XiuXianBot)

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#contact">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#联系">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#聯絡">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#連絡先">日</a>)</p>

---

## Acknowledgments

### AI

* [OpenAI](https://chat.openai.com) – General assistance on coding
* [DeepWiki](https://deepwiki.com) – Documentation & flowchart support

### Inspirations

* [BlueArchiveGM](https://github.com/PrimeStudentCouncil/BlueArchiveGM) – Admin UI design inspiration

### Media Resources

* [api.tomys.top](https://tomys.top) – Random anime backgrounds for admin dashboard

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#acknowledgments">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#致谢">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#致謝">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#謝辞">日</a>)</p>

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

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#star-history">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#star-历史">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#star-歷史">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#スターの歴史">日</a>)</p>

---

<p align="right">(<a href="#readme-top">To Top</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#others">EN</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#其他">简</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHT.md#其他">繁</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README_JPN.md#その他">日</a>)</p>

<!-- Shields & URLs -->

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