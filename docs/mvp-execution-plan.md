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
- [ ] Clean modular codebase — PARTIAL: config/storage are modular; market data, indicators and signal logic still need modules.
- [x] SQLite database initialized — DONE.
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
- [x] GitHub repository updated — DONE.
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
```

---

## 5. Immediate Next Steps

### Phase 1 — Repo Health

Goal: make the project runnable and automatically checked.

Tasks:

- [x] Format core Python files properly.
- [x] Add requirements for pytest and ruff.
- [x] Add SQLite initialization script.
- [x] Add database inspection script.
- [x] Add first database tests.
- [x] Add GitHub Actions CI.
- [x] Run local checks successfully.
- [x] Push changes to GitHub.
- [x] Confirm GitHub Actions passes.

### Phase 2 — Market Data Pipeline

Goal: collect and store stock price data.

Tasks:

- [ ] Create static MVP watchlist.
- [ ] Implement yfinance data downloader.
- [ ] Store historical OHLCV data in SQLite.
- [ ] Add tests for data formatting.

### Phase 3 — Indicators

Goal: calculate technical indicators.

Tasks:

- [ ] Implement RSI.
- [ ] Implement ATR.
- [ ] Implement volume spike ratio.
- [ ] Implement 52-week high distance.
- [ ] Add tests for each indicator.

### Phase 4 — Signal Engine

Goal: detect early stock setups.

Tasks:

- [ ] Define signal conditions.
- [ ] Generate signal score.
- [ ] Store generated signals in SQLite.
- [ ] Add tests for signal logic.

### Phase 5 — Backtest and AI Output

Goal: explain signals with historical context.

Tasks:

- [ ] Backtest similar historical setups.
- [ ] Generate AI-readable explanation prompt.
- [ ] Prepare Telegram-ready message format.

---

## 6. Current Rule

Do not add Telegram, payments, dashboard, or AI automation until the core pipeline works:

```text
universe -> market data -> indicators -> signal -> SQLite -> basic report
```