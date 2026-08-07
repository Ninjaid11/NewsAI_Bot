# 📰 NewsAI Bot

Telegram bot for news processing and distribution.

The bot retrieves news through RSS feeds, stores articles in a database, generates concise summaries using LLM (Large Language Model), and sends formatted content to users.

Built as a backend development project using Docker and integration with external APIs.

---

## Features

* News retrieval through RSS feeds
* User subscription and unsubscription management
* Multi-language support (Ukrainian, English)
* Automatic news summarization using LLM
* Article storage and persistence in database
* Scheduled batch delivery via cron runner
* Full Docker containerization

---

## ⚙️ Technology Stack

* Python 3.11
* aiogram (Telegram bot framework)
* Gemini 2.5 Flash (LLM for content summarization)
* BeautifulSoup (RSS parsing and data extraction)
* PostgreSQL (article storage)
* Docker & Docker Compose

---

## 🐳 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Ninjaid11/NewsAI_Bot.git
cd NewsAI_Bot
```

### 2. Create `.env` Configuration

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:password@db:5432/newsai_db
```

### 3. Run with Docker

```bash
docker compose up -d --build
```

The bot will start automatically and begin processing RSS feeds.

---

## How It Works

1. **RSS Feed Monitoring**: Bot periodically checks configured RSS feeds for new articles
2. **Article Storage**: New articles are stored in PostgreSQL database
3. **Summarization**: Content is processed through Gemini 2.5 Flash API to generate concise summaries
4. **Batch Delivery**: Scheduled cron runner sends collected articles to subscribed users at configured intervals
5. **Multi-language Support**: Users can choose content language (Ukrainian or English)

---

## Project Purpose

This project demonstrates:

* Telegram bot development with event-driven architecture
* Integration with external LLM APIs
* RSS feed parsing and processing
* Scheduled task management with cron
* Database design for content management
* Docker containerization best practices
* Building scalable bot infrastructure

---
