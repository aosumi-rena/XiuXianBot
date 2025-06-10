<a id="readme-top"></a>
![XiuXianBot](https://socialify.git.ci/aosumi-rena/XiuXianBot/image?custom_description=%E4%B8%80%E6%AC%BE%E5%8F%AF%E5%90%8C%E6%97%B6%E6%94%AF%E6%8C%81%E5%A4%9A%E4%B8%AA%E8%81%8A%E5%A4%A9%E5%B9%B3%E5%8F%B0%E7%9A%84%E6%96%87%E6%9C%AC%E4%BF%AE%E4%BB%99%E6%B8%B8%E6%88%8F%E6%9C%BA%E5%99%A8%E4%BA%BA&description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fminas.mihoyo.day%2Ff%2F1902fc2bd211436baf50%2F%3Fdl%3D1&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)

[![贡献者][contributors-shield]][contributors-url]
[![Forks数][forks-shield]][forks-url]
[![Stars数][stars-shield]][stars-url]
[![Issues数][issues-shield]][issues-url]
[![GPL-3.0 License][license-shield]][license-url]

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/aosumi-rena/XiuXianBot)
[![下载量][downloads-shield]][downloads-url]

# 修仙机器人

一个文字游戏机器人，通过使用通用的核心逻辑及“适配器”，并共享同一套游戏引擎和数据库，同时在 Telegram 和 Discord 运行

![Alt](https://repobeats.axiom.co/api/embed/b40285fbd34567583dc0df228cace66b09a6552c.svg "Repobeats analytics image")

**其他语言的 README**

[简体中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md#readme-top) | [English](https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#about-the-project)

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#about-the-project">English</a>)</p>

---

## 目录

<details>
  <summary>点击展开</summary>
  <ol>
    <li><a href="#关于">关于</a></li>
    <li><a href="#架构">架构</a>
      <ul>
        <li><a href="#文件结构">文件结构</a></li>
        <li><a href="#核心模块">核心模块</a></li>
        <li><a href="#平台适配器">平台适配器</a></li>
        <li><a href="#网页界面">网页界面</a></li>
      </ul>
    </li>
    <li><a href="#快速上手">快速上手</a>
      <ul>
        <li><a href="#环境准备">环境准备</a></li>
        <li><a href="#安装">安装</a></li>
          <ul>
            <li><a href="#docker">Docker部署</a></li>
            <li><a href="#自建">自建</a></li>
          </ul>
      </ul>
    </li>
    <li><a href="#使用">使用</a></li>
    <li><a href="#后续">后续</a></li>
      <ul>
        <li><a href="#内核">内核</a></li>
        <li><a href="#游戏功能">游戏功能</a></li>
      </ul>
    <li><a href="#贡献">贡献</a></li>
      <ul>
        <li><a href="#贡献者">贡献者名单</a></li>
      </ul>
    <li><a href="#许可">许可</a></li>
    <li><a href="#联系">联系</a></li>
    <li><a href="#致谢">致谢</a></li>
      <ul>
        <li><a href="#ai">AI</a></li>
        <li><a href="#灵感">灵感</a></li>
        <li><a href="#媒体资源">媒体资源</a></li>
      </ul>
    <li><a href="#其他">其他</a></li>
      <ul>
        <li><a href="#star-历史">Star 历史</a></li>
      </ul>
  </ol>
</details>

---

## 关于

此项目是一个以修仙主题为背景的文字 RPG 游戏机器人，最初为 Discord 平台开发，现已重构为跨平台方案，包含：

- **核心库**：实现所有游戏逻辑、数据库模型和本地化  
- 多个**适配器**：支持不同聊天平台（Discord、Telegram、Matrix 等）  
- **Web 界面**：用于管理员控制与公开账号管理  
- 单**启动脚本** (`start.py`)：加载配置并启动对应的适配器

### 最新更新（由 AI 编写，待人工检查）

- 管理面板改为全模态弹窗操作。
- 数据库表格新增复制 ID、封禁和停用按钮。
- Telegram 适配器现能正确渲染 Markdown。
- 底层数据库已迁移至 SQLite，无需 MongoDB。

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#about-the-project">English</a>)</p>

---

## 架构

### 文件结构

```
root/
├── adapters/
│   ├── discord/    # Discord 适配：斜杠命令、前缀命令、Modal、Embed
│   │   └── bot.py  # 启动机器人
│   ├── telegram/   # Telegram 适配：斜杠命令、Inline Keyboard
│   │   └── bot.py  # 启动机器人
│   ├── matrix/     # Matrix 适配（TBA）
│   │   └── bot.py  # 启动机器人
│   └── …           # 其他平台（TBA）
├── core/
│   ├── commands/   # 游戏命令（hunt.py、cul.py、asc.py、account.py、ele.py 等），决定 Bot 如何回应命令
│   ├── config/     # 游戏内的一些配置，例如卡池、商店、地图等
│   ├── textmaps/   # 储存 Textmap 的文件夹，机器人将使用这些文字完成本地化
│   ├── database/   # 允许 Bot 连接并管理数据库
│   ├── admin/      # 额外的管理员逻辑系统，增强本地管理面板功能
│   ├── game/       # 从 i3 版本迁移后的游戏核心逻辑，现与命令完全分离
│   ├── utils/      # 辅助执行特定命令的工具逻辑
│   └── …           # 未来功能的扩展文件夹
├── web_local/      # 本地管理控制台 GUI（配置管理、服务器控制等）
│   ├── app.py      # 在预设端口启动管理员控制台
│   ├── templates/
│   │   ├── base.html   # 公共布局（nav-tabs、footer）
│   │   ├── index.html  # 首页
│   │   ├── config.html # 修改配置（root/config.json）的页面
│   │   ├── servers.html# 控制核心服务及适配器启停
│   │   ├── admin.html  # 管理命令界面（如：编辑玩家数据、权限修改等）
│   │   ├── logs.html   # 查看/导出日志
│   │   ├── accounts.html# 管理玩家账号状态（封禁、停用、手动关联等）
│   │   └── database.html# 查看玩家信息/渲染数据库内容
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── icons/      # 管理面板 SVG 图标
│       └── js/
│           ├── config.js# 配置页面逻辑
│           └── …        # 其他页面逻辑
├── web_public/     # 公开网页 GUI（账号关联、注册等）
├── backups/        # 用户与物品备份
├── config.json     # Token、适配器开关、数据库配置等
└── start.py        # 一键启动脚本
```

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#architecture">English</a>)</p>

### 核心模块
- **admin/**  
  额外的管理员逻辑系统，增强本地管理面板功能。  
- **game/**  
  从 i3 版本迁移后的游戏核心逻辑，与命令完全分离。  
- **commands/**  
  将所有游戏功能通过纯 Python 实现：  
  - 账号创建与关联（未来将改为 Web 界面）  
  - 修炼（cul）、打野（hunt）、突破（asc）、元素系统（ele）、商店（shop）、物品栏（inventory）、状态（status）等  
- **config/**  
  游戏配置（JSON 文件，用于卡池、商店、兑换码、地图等）  
- **utils/**  
  辅助执行特定命令的工具逻辑：  
  - `account_status.py`：帮助机器人获取用户数据/状态，并生成 Markdown 格式的输出  
  - `database.py`：负责备份用户数据，生成通用 UID，确保默认数值（防止错误）  
  - `localisation.py`：负责获取本地化文本并发送给用户  
  - `otp.py`：生成一次性密码以关联账号  
- **textmaps/**  
  储存 Textmap 的文件夹，机器人将使用这些文字完成本地化。  
  目前本地化进度（欢迎贡献）：  
    - [X] 英语  
    - [X] 简体中文  
    - [ ] 繁体中文（部分完成）  
    - [ ] 其他  
- **database/**  
  - **connection.py**：SQLite 连接工厂，自动创建表结构的相关辅助函数。

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#core-modules">English</a>)</p>

### 平台适配器
各适配器负责将平台消息/事件映射到核心命令，并将核心返回格式化为平台消息：

- **Discord**  
  - 支持斜杠命令 & 前缀命令  
  - 使用 Modal 进行账号创建/兑换码  
  - 使用 Embed 输出丰富内容  
- **Telegram**  
  - 支持斜杠命令 & Inline Keyboard  
  - 不支持时回退为纯文本输出  
  - 现已正确渲染 Markdown 信息
- **Matrix**  
  - 使用 Matrix SDK（例如 `matrix-nio`）进行原型开发  
  - 纯文本与回复按钮  

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#platform-adapters">English</a>)</p>

### 网页界面
- **本地网页管理面板** (`web_local/`)  
  基于 Flask 的本地网页版管理面板，默认运行在 `http://localhost:11451`，提供单页标签式界面：  
  - 管理面板的所有界面均改为模态弹窗操作。
  1. **配置管理** (`localhost:11451/config`)  
     - 将 `config.json` 以 GUI 形式加载，所有键值以可编辑字段显示。  
     - “保存”按钮通过 Fetch POST 接口提交更新后的 JSON，写回磁盘并提示保存成功，同时提醒是否需要重启 `start.py`，无需刷新页面。  
  2. **服务器控制** (`localhost:11451/servers`)  
     - 列出核心进程与已启用的适配器（Discord、Telegram 等），并提供开关切换。  
     - 运行状态显示为绿/红指示灯。  
     - 点击启动/停止即可控制所选服务（核心服务、Discord 适配器、Telegram 适配器等）。  
     - 未来将支持“暂停/恢复”类似 Docker 容器功能。  
  3. **管理工具** (`localhost:11451/admin`)  
     - GUI 封装的老版本管理命令（如 Textmap 索引、玩家数据覆盖、权限修改等）。  
  4. **日志查看** (`localhost:11451/logs`)  
     - 实时流式展示最新日志条目。  
     - 提供下载日志文件按钮。  
     - 日志可按来源与重要程度筛选。  
  5. **数据库浏览** (`localhost:11451/database`)  
     - 按条件查询 `users` 集合（自动关联 `items` 集合中的玩家物品信息）。  
     - 以分页表格显示结果，并支持导出。  
     - 每行均提供复制 ID、封禁和停用按钮。
  6. **账号管理** (`localhost:11451/accounts`)  
     - 浏览与搜索玩家信息。  
     - 封禁/解封、停用/重新激活，或手动关联第三方账号 ID。  
     - 待补充（页面完成后添加）。  
  **技术亮点**  
  - 使用 **Flask Blueprints** 组织路由（`admin_bp`）。  
  - 使用 **Jinja2 模板** (`base.html`、`index.html`、`config.html` 等) 提供统一导航标签布局。  
  - 使用 **Bootstrap 5** 构建响应式、精美界面（导航标签、卡片、徽章）。  
  - 静态资源集中在 `static/css` 和 `static/js`，样式与逻辑分离。  
  - 默认仅允许本地访问，无需外部认证，但可轻松添加 API Key 或 IP 白名单。  
- **公共域名** (`web_public/`)  
  - 查看服务器状态  
  - 通过网页注册新账号  
  - 发送 OTP 到聊天平台以关联已有账号  
  - 在网页端查看个人状态、物品栏等  

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#web-interfaces">English</a>)</p>

---

## 快速上手

### 环境准备

**Docker 部署**：  
- Docker（废话）

**自建**：  
- Python 3.12+  
- SQLite（内置，无需额外安装）
- MongoDB （仅`i3`版本需要）

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#getting-started">English</a>)</p>

### 安装

#### Docker 部署
&&& 本节内容未完成 &&&  
**官方 Release (`OSRELDocker1.0.0_*` 及以上) {开发中}**  
1. **Clone 仓库**  
   ```sh
   git clone https://github.com/aosumi-rena/XiuXianBot.git
   cd XiuXianBot
   ```

2. **配置**

   * 修改 `docker-compose.yml`：添加你的 Discord & Telegram Token，并根据需要修改其他环境变量。
     **[docker-compose.yml](https://github.com/aosumi-rena/XiuXianBot/blob/main/docker-compose.yml) 示例**：

   ```yaml
   # 临时占位，发布后可能不会一致
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
3. **Docker Compose**

   ```sh
   docker-compose up -d
   ```
4. **启动本地管理面板网页**  
   执行完 `docker-compose up` 后，相关容器会自动启动。  
   打开浏览器访问 `http://localhost:11451`（或配置中指定的端口），检查和最终确认设置。
5. **启动机器人各平台适配器**  
   在本地管理面板中，启用所需平台适配器（Discord、Telegram 等），对应容器将被启动。  

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#docker">English</a>)</p>

#### 自建
**Pre-release: [OSBLTSDocker0.1.52](https://github.com/aosumi-rena/XiuXianBot/releases/tag/v0.1.52-LTS)**
&&& 待翻译，不行了得睡了困死了 &&&
1. **Download Prebuild**  

   * [Download from releases](https://github.com/aosumi-rena/XiuXianBot/releases/tag/v0.1.52-LTS)
   * [Download from cloud drive](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **Unzip and Configure**

   * Unzip the prebuild into any directory ([7-Zip](https://www.7-zip.org/) recommended).
   * Configure variables (Bot Token, etc.) in the config.json
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

---


**Pre-release: [Internal-3 (i3)](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)**

1. **下载 Prebuild**

   * [从 Release 下载](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)
   * [从云盘下载](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **解压及配置**

   * 使用 [7-Zip(推荐)](https://www.7-zip.org/) 解压下载文件到任意目录。
   * 根据 [README.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/0-Releases/LTS/OSBLTSDiscord_pre-3.0.2/README.txt) 配置变量（Bot Token、`admin_ids` 等）。
3. **安装依赖**

   ```sh
   pip install -r requirements.txt
   ```
4. **启动**

   ```sh
   python bot.py
   ```

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#build">English</a>)</p>

---

## 使用

运行后，机器人将：

* 在 `http://localhost:11451`（默认端口，可在 `config.json` 中修改）打开本地管理面板网页。
* 核心服务器默认监听 `http://localhost:11450`。
* 在该面板里启用所需平台后，机器人会：

  * 连接 Discord 并响应 `^start`、`^cul`、`^hunt`、`^asc`、`^ele`、`/shop` 等命令。
  * 连接 Telegram（若启用）并响应相应的斜杠命令。
  * 连接 Matrix（若启用，正在试作阶段），并使用纯文本/按钮交互。

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#usage">English</a>)</p>

---

## 后续

### 内核

* [x] 将核心逻辑拆分至 **core/**
* [ ] 在 **core/commands/** 制作命令监听/响应逻辑
* [ ] 改为使用`C#`制作核心服务器
* [X] 完善 **Discord** 适配器
* [X] 添加 **Telegram** 适配器
* [ ] 试作 **Matrix** 适配器
* [x] 构建 **web\_local** 管理面板 GUI
* [ ] 构建 **web\_public** 公开网页
* [ ] Docker 化部署

### 游戏功能

* [ ] Buff 系统及可使用物品
* [ ] 装备系统
* [ ] 邮件功能
* [ ] 探索系统（地图）
* [ ] 修仙分支（例如宇宙主题等）
* [ ] 战斗系统（回合制）
* [ ] 抽卡系统
* [ ] 交易系统

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#roadmap">English</a>)</p>

---

## 贡献

* 欢迎任何人为此仓库贡献，您可以通过 Pull Requests 或 Issues 提出改进建议。
* 对于本地化贡献，将使用 Weblate 搭建贡献平台，目前可临时通过 Issues 或 Pull Requests 进行贡献。

### 贡献者

<table cellpadding="0" cellspacing="0">
  <tr>
    <td valign="middle">
      <a href="https://github.com/aosumi-rena" target="_blank">
        <img
          src="https://github.com/aosumi-rena.png"
          alt="头像-青澄玲奈"
          width="50"
          height="50"
          style="border-radius:50%;"
        />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em;">
      <b style="margin:0;">项目指导 | 游戏逻辑代码 | 本地控制面板 HTML</b>
    </td>
  </tr>

  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/Columbina-Dev" target="_blank">
        <img
          src="https://github.com/Columbina-Dev.png"
          alt="头像-Columbina"
          width="50"
          height="50"
          style="border-radius:50%;"
        />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <b style="margin:0;">游戏逻辑设计 | Discord 适配 | 数据库读写逻辑 | 本地化逻辑</b>
    </td>
  </tr>

  <tr>
    <td valign="middle" style="padding-top:0.75em;">
      <a href="https://github.com/ThirtySeven377" target="_blank">
        <img
          src="https://github.com/ThirtySeven377.png"
          alt="头像-ThirtySeven377"
          width="50"
          height="50"
          style="border-radius:50%;"
        />
      </a>
    </td>
    <td valign="middle" style="padding-left:0.5em; padding-top:0.75em;">
      <b style="margin:0;">Telegram 适配 | 文档编写</b>
    </td>
  </tr>
</table>

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#contributors">English</a>)</p>

---

## 许可

[![License](https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/GPLv3_Logo.svg/330px-GPLv3_Logo.svg.png)](https://www.gnu.org/licenses/gpl-3.0)

XiuXianBot ©2024-2025 By 青澄玲奈

此程序不含任何担保；具体细节请参见 [LICENSE.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/LICENSE.txt)。

此程序根据 GNU GPL v3.0 许可免费发布，您可以在此条款下重新分发/转载。

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#license">English</a>)</p>

---

## 联系

青澄玲奈 – [rena.aosumi@mihoyo.day](mailto:rena.aosumi@mihoyo.day)

项目地址: [https://github.com/aosumi-rena/XiuXianBot](https://github.com/aosumi-rena/XiuXianBot)

<p align="right">(<a href="#readme-top">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#contact">English</a>)</p>

---

## 致谢

### AI

* [OpenAI](https://chat.openai.com) – 一般帮助
* [Deepwiki](https://deepwiki.com) – 文档支持

### 灵感

* [BlueArchiveGM](https://github.com/PrimeStudentCouncil/BlueArchiveGM) – 本地管理面板设计灵感

### 媒体资源

* [api.tomys.top](https://tomys.top) – 随机二次元背景图（本地管理面板）

<p align="right">(<a href="#致谢">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#acknowledgments">English</a>)</p>

---

## 其他

### Star 历史

<a href="https://www.star-history.com/#aosumi-rena/XiuXianBot&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=aosumi-rena/XiuXianBot&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=aosumi-rena/XiuXianBot&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=aosumi-rena/XiuXianBot&type=Date" />
 </picture>
</a>

<p align="right">(<a href="#star历史">回到顶部</a> | <a href="https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md#star-history">English</a>)</p>

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
