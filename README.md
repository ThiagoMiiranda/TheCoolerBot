# 🎧 The Cooler Bot - Discord Music Bot

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![discord.py](https://img.shields.io/badge/discord.py-2.3.2-blueviolet?logo=discord)
![yt-dlp](https://img.shields.io/badge/yt--dlp-2024.04.09-yellow?logo=youtube)
![License](https://img.shields.io/github/license/ThiagoMiiranda/TheCoolerBot)
![Status](https://img.shields.io/badge/status-in%20development-orange)

> 🎶 A music bot for Discord, developed with a focus on practical learning of asynchronous Python development, object oriented programming, project organization and good development practices.

---

## 🚀 **What is this project?**

The Cooler Bot is a music bot for Discord developed in Python, with robust features such as:
- 🎧 Music playback via YouTube (support for links, playlists and text search in the future).
- 🔊 Queue control (add, skip, view queue, and more).
- 🚀 Processing playlists **asynchronously and non-blocking**, avoiding bot crashes.
- 💡 Code organized into multiple classes and files for high scalability and easy maintenance.

The aim of this project is to be both a functional tool and a technical portfolio, demonstrating mastery of:
- Asynchronous Python (`asyncio`, `concurrent.futures`)
- Handling external APIs
- Software architecture
- Good practices with Git and project organization

---

## 🧠 **What have I learned?**

During development, I deepened my knowledge of:
- Organization of Python projects with multiple files, separation of responsibilities and use of absolute imports.
- Object oriented programming design in a more robust app scenario.
- Python concurrency and parallelism, mainly using `asyncio` combined with `run_in_executor` for heavy processing (such as playlist extraction) without crashing the bot's event loop.
- Queue and state management within asyncronous applications.
- Integration with robust external libraries such as [`discord.py`](https://discordpy.readthedocs.io/) and [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).

---

## 🔧 **Technologies and Libraries**

| Technology  | Description                                        |
| ------------ | ------------------------------------------------ |
| **Python** | Main language (version 3.12+)              |
| **discord.py** | API wrapper for Discord bots (version 2.x)  |
| **yt-dlp** | YouTube audio and metadata extraction        |
| **FFmpeg** | Audio stream processing               |
| **asyncio** | Event based concurrency                 |

---

## 🎯 **Main technical challenges**

> The biggest technical challenge was to ensure that loading playlists (especially **YouTube Mixes or long playlists**) didn't crash the bot.

- To do this, I implemented a system that:
  - **Loads the first song quickly** and starts playing immediately.
  - While it's playing, it loads the other songs in the playlist in **background threads**, using `run_in_executor`.
  - Handles errors such as private videos, unavailable videos or regional restrictions, without breaking the bot's flow.

---

## 🗂️ **File structure**

```
TheCoolerBot/
├── music/
│   ├── extractor.py       # Information extraction via yt-dlp
│   ├── player.py          # Playback and queue management
│   ├── queue_manager.py   # Queue operations (add, skip, skip_to, etc.)
│   ├── voice_validation.py# Checking if the user is on the voice channel
│   └── __init__.py
├── music.py               # Main bot commands (!play, !skip, !queue, etc.)
├── requirements.txt       # Project dependencies
├── .env                   # API keys and tokens (unversioned)
├── README.md              # This file
└── main.py                # Bot initialization
```

---

## 🧠 **Advanced Techniques and Concepts Used**

- 🔀 **Hybrid concurrency:** Combination of `asyncio` with `concurrent.futures` to balance I/O-bound (Discord API) and CPU/disk/network-bound (yt-dlp and ffmpeg) tasks.
- 📥 **Robust parsing:** Use of `yt-dlp` with secure metadata extraction, error handling such as private and unavailable videos.
- 📦 **Modular architecture:** Code separated by responsibilities, applying software engineering concepts.
- 🎯 **Fail-safe playback:** System that automatically removes songs with errors and continues the queue without crashing.

---

## 🌟 **Next Features (In Development)**

- 🎨 **Beautiful and informative embeds** for commands
- 🔥 **Slash commands** (with autocomplete, description and modern organization)
- 🌐 **Cloud hosting**, to stay online 24/7 (probably using Render, Railway or another platform)
- 🔍 **Search by name**, no need to pass on links
- 📝 **Logs and metrics system** (perhaps with Sentry, Loguru, or Prometheus + Grafana in the future)

---

## ▶️ **How to run locally**

### Prerequisites:
- Python 3.12+
- ffmpeg installed and in PATH (https://ffmpeg.org/)
- Create a bot on [Discord Developer Portal](https://discord.com/developers/applications) and get your token.

### Instalation:
```bash
git clone https://github.com/seu-usuario/TheCoolerBot.git
cd TheCoolerBot
python -m venv venv
venv\Scripts\activate # Windows
# source venv/bin/activate # Linux/Mac

pip install -r requirements.txt
```

### Create an `.env` file on the root:

```env
DISCORD_TOKEN=your_token_here
```

### Execute:
```bash
python bot.py
```

---

## 📜 **License**

[MIT License](LICENSE)

---

## 💼 **Contact**

If you want to discuss development, vacancies or collaborate on projects, call me on [LinkedIn](https://www.linkedin.com/in/thiago-miiranda/) or open an issue!

---

> ✨ *This project was developed as a learning project, but with a code pattern designed for production.* ✨
