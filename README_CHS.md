<a id="readme-top"></a>
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/aosumi-rena/XiuXianBot)
# 修仙机器人

*此文件由AI翻译，本人做了部分的修改，有些可能看得很入机，欢迎修改（不得不说还是AI方便（*

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
├── core/
│   ├── commands/   # 游戏命令（hunt.py、cul.py、asc.py、account.py、ele.py 等）
│   ├── admin/      # 老版本的管理工具（textmap 索引、统计、备份）
│   └── utils/      # 数据库模型、本地化、计算工具、ID 生成
│   └── …           # 未来扩展功能文件夹
├── adapters/
│   ├── discord/    # Discord 适配：斜杠命令、前缀命令、Modal、Embed
│   ├── telegram/   # Telegram 适配：斜杠命令、Inline keyboard
│   └── matrix/     # Matrix 适配（TBA）
│   └── …           # 其他平台（TBA）
├── web_local/      # 本地的Bot/数据管理网页版GUI（配置管理、服务器控制等）
├── web_public/     # 公共域名的网页版GUI（账号关联、注册等）
├── backups/        # 用户与物品数据备份
├── config.json     # Token、适配器开关、数据库配置等
└── start.py          # 一键启动
```

### 核心模块

- **commands/**  
  将所有游戏功能通过纯Python实现：  
  - 账号创建与关联（未来将改为使用Web界面）  
  - 修炼（cul）、打野（hunt）、突破（asc）、元素系统（ele）、商店（shop）、物品栏（inventory）、状态（status）等  
- **admin/**  
  老版本的Discord Bot Admin命令（未来切换到网页GUI）  
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

- **本地管理员GUI** (`web_local/`)  
  - 配置管理 (`config.json`)  
  - 适配器开关
  - 查看日志  
  - 原Admin命令快速调用  
- **公共域名** (`web_public/`)  
  - 注册新账号  
  - 通过发送验证码到聊天平台关联玩家的现有账号  

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
4. **启动！**
   ```sh
   python start.py
   ```

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 使用

运行后，机器人将能够：
* 连接 Discord 并响应 `^start`、`^cul`、`^hunt`、`^asc`、`^ele`、`/shop` 等各种命令
* 连接 Telegram（若启用）并相应对应的的斜杠命令
* 在`http://127.0.0.1:11451`提供本地的机器人管理功能

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

&&&此部分未完成&&&

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>

---

## 许可

&&&此部分未完成&&&

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
