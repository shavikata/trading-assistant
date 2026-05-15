# AI Stock Signal SaaS — MVP Execution Plan

## 1. Project Goal

Build an AI-powered stock signal SaaS for Small-Cap US stocks.

By the end of this MVP period, the project should have a working pipeline that can:

- collect small-cap stock data
- detect technical pre-breakout setups
- store market data and signals in SQLite
- backtest similar historical setups
- generate AI-readable signal explanations
- prepare Telegram bot output
- prepare the project for paid subscription access

The product is not a financial advisor. It provides transparent, data-backed stock signal analysis.

---

## 2. Current Project Status

Status legend:

- DONE = completed
- PARTIAL = started but not complete
- TODO = not started yet

### Core MVP

- [x] Working Python project architecture — DONE: main folders exist.
- [ ] Clean modular codebase — PARTIAL: config/storage are modular; market scan logic still needs to be moved into modules.
- [ ] SQLite database initialized — PARTIAL: init script exists; mark DONE after `python scripts/init_db.py` runs successfully.
- [ ] Small-cap ticker universe loader — TODO.
- [ ] yfinance market data pipeline — TODO.
- [ ] Technical indicators — TODO.
  - [ ] RSI — TODO.
  - [ ] ATR — TODO.
  - [ ] Volume spike — TODO.
  - [ ] 52-week high distance — TODO.
- [ ] Signal engine — TODO.
- [ ] Stored signals in database — TODO.
- [ ] Backtest engine — TODO.
- [ ] AI prompt builder — TODO.
- [ ] Basic Telegram-ready signal format — TODO.
- [ ] GitHub repository updated — TODO: mark DONE after this commit is pushed.
- [x] Obsidian documentation updated — DONE: MVP plan is formatted and tracked.

### Business MVP

- [ ] Clear product positioning — PARTIAL: basic positioning is written.
- [ ] Subscription model defined — TODO.
- [ ] Disclaimer policy defined — PARTIAL: basic non-financial-advisor disclaimer exists.
- [ ] Signal transparency logic defined — TODO.
- [ ] Telegram distribution plan prepared — TODO.
- [ ] Payment integration plan prepared — TODO.

---

## 3. Product Positioning

The product helps users discover small-cap US stock setups before potential breakout moves.

The product combines:

1. Technical analysis
2. Historical backtest evidence
3. News sentiment
4. Social sentiment
5. AI explanation

Main promise:

> We do not promise guaranteed returns.
> We provide transparent, data-backed signal analysis with clear risk levels.

---

## 4. Architecture Flow

```text
Ticker Universe
↓
Market Data Ingestion
↓
Indicators
↓
Signal Engine
↓
SQLite Storage
↓
Backtest Engine
↓
AI Analysis
↓
Telegram Bot / Dashboard
↓
Performance Tracking