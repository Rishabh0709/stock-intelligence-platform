# System Architecture

---

## Design Principles

- Separation of Concerns
- Single Responsibility Principle
- Repository Pattern
- Dependency Injection
- Service Layer
- Domain Driven Design

---

## Architecture

```
                     Streamlit

                         │

               Dashboard Pages

                         │

                  Service Layer

                         │

        ┌────────────────────────┐

        │                        │

 Repository Layer          Collectors

        │                        │

        └──────────────┬─────────┘

                       │

                   SQLite

```

---

## Layers

### Dashboard

Presentation Layer

Responsible for

- UI
- Charts
- User Interaction

---

### Services

Business Logic

Responsible for

- Portfolio calculations
- Company analysis
- Recommendation engine

---

### Repositories

Data Access Layer

Responsible for

- CRUD
- Queries
- Database interaction

---

### Collectors

External Data Sources

Responsible for

- Yahoo Finance
- NSE
- AlphaVantage
- Screener APIs (future)

---

### Database

Persistent Storage

SQLite

Future

PostgreSQL

---

## Dependency Injection

```
Dashboard

↓

StockExplorerService

↓

Repositories

↓

DatabaseManager

↓

SQLite
```

---

## Future Modules

Analytics Engine

Portfolio Engine

Recommendation Engine

AI Assistant