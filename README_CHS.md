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

*此文件的部分由AI翻译（会专门标出），可能有些入机感*

一个文字游戏机器人，通过使用通用的核心逻辑及“适配器”，并共享同一套游戏引擎和数据库，同时在Telegram和Discord运行

**README 差分**

[简体中文](https://github.com/aosumi-rena/XiuXianBot/blob/main/README_CHS.md) | [English](https://github.com/aosumi-rena/XiuXianBot/blob/main/README.md)
<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

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
      </ul>
    </li>
    <li><a href="#使用">使用</a></li>
    <li><a href="#后续">后续</a></li>
      <ul>
        <li><a href="#内核">内核</a></li>
        <li><a href="#游戏功能">游戏功能</a></li>
      </ul>
    <li><a href="#贡献">贡献</a></li>
    <li><a href="#许可">许可</a></li>
    <li><a href="#联系">联系</a></li>
    <li><a href="#致谢">致谢</a></li>
  </ol>
</details>

---

## 关于

此Project是一个以修仙主题为背景的文字RPG游戏机器人，最初为Discord平台开发，现已重构为跨平台方案，包含：

- **核心库**：实现所有游戏逻辑、数据库模型和本地化  
- 多个**适配器**：支持不同聊天平台（Discord、Telegram、Matrix等）  
- **Web界面**（可选）：用于管理员控制与公开账号管理  
- 单**启动脚本** (`start.py`)：加载配置并启动对应的适配器  

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 架构

### 文件结构

```
root/
├── adapters/
│   ├── discord/    # Discord 适配：斜杠命令、前缀命令、Modal、Embed
│   ├── telegram/   # Telegram 适配：斜杠命令、Inline keyboard
│   ├── matrix/     # Matrix 适配（TBA）
│   └── …           # 其他平台（TBA）
├── core/
│   ├── commands/   # 游戏命令（hunt.py、cul.py、asc.py、account.py、ele.py 等）
│   ├── config/     # 游戏内的一些设置，例如卡池、商店、地图等
│   ├── textmaps/   # 储存Textmap的文件夹，机器人将通过使用这里面的文字完成本地化
│   ├── utils/      # 数据库模型、本地化、计算工具、ID 生成
│   └── …           # 未来扩展功能文件夹
├── web_local/      # 本地的Bot/数据管理网页版GUI（配置管理、服务器控制等）
│   ├── app.py                  # 在预设的端口中开放管理员控制台
│   ├── templates/
│   │   ├── base.html           # 基础的html格式(nav-tabs, footer)
│   │   ├── index.html          # 主页
│   │   ├── config.html         # 修改配置（root/config.json）的页面
│   │   ├── servers.html        # 控制开/关主服务器（游戏内核）及Bot启用的平台的页面
│   │   ├── admin.html          # 使用管理员功能/命令的页面（例：修改玩家的数值、权限 | 换句话说：一个比直接修改数据库更方便的GUI页面）
│   │   ├── logs.html           # 查看/导出日志
│   │   ├── accounts.html       # 控制玩家账号的状态（例：封禁、取消激活、手动关联账号等）
│   │   └── database.html       # 查看玩家的信息/显示数据库的数据
│   └── static/
│       ├── css/
│       │   └── styles.css
│       └── js/
│           ├── config.js       # 修改配置的页面的逻辑
│           └── ...             # 其他页面的逻辑
├── web_public/     # 公共域名的网页版GUI（账号关联、注册等）
├── backups/        # 用户与物品数据备份
├── config.json     # Token、适配器开关、数据库配置等
└── start.py        # 一键启动
```

### 核心模块

- **commands/**  
  将所有游戏功能通过纯Python实现：  
  - 账号创建与关联（未来将改为使用Web界面）  
  - 修炼（cul）、打野（hunt）、突破（asc）、元素系统（ele）、商店（shop）、物品栏（inventory）、状态（status）等  
- **config/**  
  游戏内的一些json设置，例如卡池、商店、兑换码和地图等
- **textmaps/**  
  储存Textmap的文件夹，机器人将通过使用这里面的文字完成本地化

  目前本地化进度（欢迎各位大佬贡献）：
    - [X] 英语
    - [X] 简体中文
    - [ ] 繁体中文（部分完成）
    - [ ] ？？？
    
- **utils/**  
  - **database.py**：MongoDB 连接、`user_id`自动生成、备份  
  - **localisation.py**：加载 json textmap
  - …（未来更多工具）

### 平台适配器

各适配器负责将平台消息/事件映射到核心命令，并将核心返回格式化为平台消息：

- **Discord**  
  - 支持斜杠、前缀命令  
  - 使用Modal进行账号创建/兑换码  
  - 使用Embed输出丰富内容  
- **Telegram**  
  - 支持斜杠命令和Inline Keyboard
  - 不支持的功能可回退为纯文本  
- **Matrix**  
  - 使用Matrix SDK（如 `matrix-nio`）进行原型开发  
  - 纯文本和回复按钮  

### 网页界面
&&&以下部分暂时由AI翻译，待检查&&&
- **本地管理员 GUI** (`web_local/`)  
  基于 Flask 的本地仪表盘，运行在本机（例如 `http://127.0.0.1:11451`），提供单页标签式界面：

  1. **配置管理** (`127.0.0.1:11451/config`)  
     - 将 `config.json` 以表单形式加载，每个键值对都可编辑。  
     - 高亮标注哪些设置需要重启 `start.py`（“核心重启”），哪些只需重启适配器（“适配器重启”）。  
     - “保存”按钮通过 Fetch 接口将更新后的 JSON 提交到 POST 端点，写回磁盘并显示保存成功提示，无需刷新页面。  

  2. **服务器控制** (`127.0.0.1:11451/servers`)  
     - 列出核心进程和各已启用适配器（Discord、Telegram 等），并提供开关切换。  
     - 点击“启动/停止”时调用子进程或系统命令，仅启动或停止所选服务。  
     - （未来）支持“暂停/恢复”功能，类似 Docker 容器。  
     - 运行状态以绿/红指示灯显示。  

  3. **管理工具** (`127.0.0.1:11451/admin`)  
     - GUI 封装老版本的管理员命令（如Textmap索引、玩家数据覆盖、权限修改等）。  
     - 待补充（页面完成后添加）  

  4. **日志查看** (`127.0.0.1:11451/logs`)  
     - 实时流式展示最新日志条目。  
     - 提供下载日志文件按钮。  
     - 待补充（页面完成后添加）  

  5. **账号管理** (`127.0.0.1:11451/accounts`)  
     - 浏览与搜索玩家信息。  
     - 封禁/解封、停用/重新激活，或手动关联第三方账号 ID。  
     - 待补充（页面完成后添加）  

  6. **数据库浏览** (`127.0.0.1:11451/database`)  
     - 按条件查询 `users` 集合（并自动关联 `items` 集合中的该玩家物品信息）。  
     - 以分页表格展示结果，并支持导出。  
     - 待补充（页面完成后添加）  

  **技术亮点**  
  - 使用 **Flask Blueprints** 组织路由（`admin_bp`）。  
  - 基于 **Jinja2 模板** (`base.html`、`index.html`、`config.html` 等) 实现统一的导航标签布局。  
  - 采用 **Bootstrap 5** 构建响应式、精美的界面（导航标签、卡片、徽章）。  
  - 静态资源集中在 `static/css` 和 `static/js`，样式与逻辑分离。  
  - 默认仅允许本地访问，无需外部认证，后续可轻松添加 API Key 或 IP 白名单。  

- **公共域名** (`web_public/`)  
  - 查看服务器运行状态  
  - 通过网页注册新账号  
  - 发送 OTP 到聊天平台以关联已有账号  
  - 在网页端查看个人状态、物品栏等  

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 快速上手
&&&此部分未完成&&&
### 环境准备

- Python 3.10+  
- MongoDB  
- Docker（可选，用于容器化部署）  

### 安装
**[Internal-3 (i3) 版本 {直装版}](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)**
1. **下载**
    - [从Release下载](https://github.com/aosumi-rena/XiuXianBot/releases/tag/vPre-i3.0.2-LTS)
    - [从云盘下载](https://minas.mihoyo.day/d/bea2128c4d9340208f24/)
2. **解压及配置设置**
    - 使用[7-Zip(推荐)](https://www.7-zip.org/)解压下载的文件到任意路径
    - 根据[README.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/0-Releases/LTS/OSBLTSDiscord_pre-3.0.2/README.txt)配置变量 (包括 Bot Token, admin_ids等) 
3. **安装依赖**
    ```sh
    pip install -r requirements.txt
    ```
4. **启动！**
   ```sh
   python bot.py
   ```

===================================

**Internal-4 (i4) 及以上版本 {开发中}**
1. **Clone Repo**  
   ```sh
   git clone https://github.com/aosumi-rena/XiuXianBot.git
   cd XiuXianBot
   ```

2. **安装依赖**
   ```sh
   pip install -r requirements.txt
   ```
3. **配置**
   * 编辑 `config.json`，填写 MongoDB URI、Discord 与 Telegram Token、选择启用的适配器
4. **启动本地控制台网页**
   ```sh
   python start.py
   ```
   之后会在预设的端口中打开机器人控制台网页，使用浏览器进入网页以再次检查配置是否正确
5. **启动相应的Bot平台**

   全部检查好之后，在网页中启动你需要Bot运行在的平台
<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 使用

运行后，将：
* 在`http://127.0.0.1:11451`（预设端口，可在`config.json`中更改所选端口）打开机器人控制台网页

启动需要的平台，之后机器人将：
* 连接 Discord 并响应 `^start`、`^cul`、`^hunt`、`^asc`、`^ele`、`/shop` 等各种命令
* 连接 Telegram（若启用）并相应对应的的斜杠命令
* 连接 Matrix（若启用）并？？？（暂时没有计划，所以我也不知道会发生什么）


<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 后续

### 内核
* [ ] 将核心逻辑完全拆分到 **core/**
* [ ] 完善**Discord**适配器
* [ ] 添加**Telegram**适配器
* [ ] 试作**Matrix**适配器
* [ ] 构建**web\_local**管理GUI
* [ ] 构建**web\_public**用户创建等功能
* [ ] Docker化部署

### 游戏功能
* [ ] Buff系统及可使用物品
* [ ] 装备系统
* [ ] 邮件功能
* [ ] 探索系统（地图）
* [ ] 修仙分支（例如宇宙主题等）
* [ ] 战斗系统（回合制）
* [ ] 抽卡系统
* [ ] 交易系统

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 贡献

- 欢迎任何人为此仓库贡献，你可以通过Pull requestse和Issues提出你认为可以改进 此项目的想法和建议
- 对于本地化贡献，我会使用Weblate搭建网页版贡献工具，现在可以临时使用Issues或Pull requests

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 许可

XiuXianBot ©2024-2025 By 青澄玲奈

此程序不含有任何担保；具体细节请查看[LICENSE.txt](https://github.com/aosumi-rena/XiuXianBot/blob/main/LICENSE.txt)。

此程序为免费程序，你可以根据GNU GPL v3.0的条款重新分发/转载。

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 联系

青澄玲奈 – [rena.aosumi@mihoyo.day](mailto:rena.aosumi@mihoyo.day)

项目地址: [https://github.com/aosumi-rena/XiuXianBot](https://github.com/aosumi-rena/XiuXianBot)

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 致谢

&&&此部分未完成&&&

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>


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
