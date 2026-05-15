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

## 2. End-of-Period Target

At the end of the period, we want to have:

### Core MVP

- [ ] Working Python project architecture
- [ ] Clean modular codebase
- [ ] SQLite database initialized
- [ ] Small-cap ticker universe loader
- [ ] yfinance market data pipeline
- [ ] Technical indicators:
  - [ ] RSI
  - [ ] ATR
  - [ ] Volume spike
  - [ ] 52-week high distance
- [ ] Signal engine
- [ ] Stored signals in database
- [ ] Backtest engine
- [ ] AI prompt builder
- [ ] Basic Telegram-ready signal format
- [ ] GitHub repository updated
- [ ] Obsidian documentation updated

### Business MVP

- [ ] Clear product positioning
- [ ] Subscription model defined
- [ ] Disclaimer policy defined
- [ ] Signal transparency logic defined
- [ ] Telegram distribution plan prepared
- [ ] Payment integration plan prepared

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