# Copilot Instructions — Trading Assistant

This is a Python project for an AI-powered small-cap stock signal SaaS.

## Core Architecture

Use this pipeline:

```text
ticker universe -> yfinance data -> indicators -> signal engine -> SQLite -> report