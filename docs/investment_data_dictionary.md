# Investment Data Dictionary

## Companies

| Field | Type | Frequency | Source | Importance | Used In |
|---------|------|-----------|----------|------------|----------|
| symbol | TEXT | Static | NSE | Critical | Everywhere |
| isin | TEXT | Static | NSE | Critical | Data Integration |
| sector | TEXT | Rare | Yahoo | High | Analytics |
| industry | TEXT | Rare | Yahoo | High | Analytics |

---

## Daily Prices

| Field | Type | Frequency | Source | Importance | Used In |
|---------|------|-----------|----------|------------|----------|
| open | FLOAT | Daily | Yahoo | High | Technical |
| high | FLOAT | Daily | Yahoo | High | Technical |
| low | FLOAT | Daily | Yahoo | High | Technical |
| close | FLOAT | Daily | Yahoo | Critical | Everywhere |
| volume | BIGINT | Daily | Yahoo | High | Liquidity |

---

## Financial Metrics

| Field | Type | Frequency | Source | Importance | Used In |
|---------|------|-----------|----------|------------|----------|
| ROE | FLOAT | Quarterly | Screener | Critical | Quality Score |
| ROCE | FLOAT | Quarterly | Screener | Critical | Quality Score |
| Debt/Equity | FLOAT | Quarterly | Screener | High | Risk Score |