Build an investment intelligence platform that explains portfolio performance, compares it with the right benchmarks, 
and provides transparent, evidence-based insights to help investors make better decisions.

# 📈 Stock Intelligence Platform

An Investment Intelligence Platform built with Python that helps investors make better decisions using quantitative analysis, portfolio analytics, financial data and benchmark comparison.

---

## Vision

Most investment platforms tell you **what** happened.

This platform aims to explain **why** it happened and **what to do next**.

The long-term goal is to build an intelligent assistant capable of answering questions like:

- Why did my portfolio underperform?
- Which stock contributed most to my returns?
- How does my portfolio compare with the benchmark?
- Is this company fundamentally improving?
- Should I Buy, Hold or Sell?

---

## Current Features (v0.2)

### Data Platform

- SQLite Database
- Repository Pattern
- Service Layer
- Dependency Injection
- Company Master

### Company Import

- Import company information from Yahoo Finance
- Automatic duplicate detection
- Local database storage

### Dashboard

- Streamlit Dashboard
- Database Health
- Company Count
- Price Record Count
- Portfolio Summary

### Watchlist

- Separate research watchlist
- Add, edit and remove stocks
- Reference, target and alert prices
- Priority, status, thesis and notes
- Current price and target-upside tracking
- Price history, returns, volatility and drawdown
- 50-day and 200-day moving-average review
- Valuation snapshot and deterministic signals
- No LLM installation or AI API key required

---

## Tech Stack

| Layer | Technology |
|--------|------------|
| Language | Python 3.13 |
| Database | SQLite |
| ORM | SQLAlchemy Core |
| UI | Streamlit |
| Data | Yahoo Finance |
| Charts | Plotly (Upcoming) |
| Version Control | Git + GitHub |

---

## Project Structure

```
stock-intelligence-platform/

config/

database/

dashboard/

src/
    analytics/
    benchmarks/
    collectors/
    core/
    database/
    models/
    portfolio/
    recommendations/
    repositories/
    services/
    utils/
```

---

## Architecture

```
Dashboard
      │
      ▼
 Services
      │
      ▼
Repositories
      │
      ▼
 Database

Collectors
      │
      ▼
External APIs
```

---

## Roadmap

- ✅ CLI
- 🚧 Stock Explorer
- Portfolio Analytics
- Technical Analysis
- Financial Statements
- Recommendation Engine
- AI Investment Assistant

---

## Status

Current Version

**v0.2**

Development Branch

`feature/stock-explorer`

---

## Author

Rishabh Rathi
