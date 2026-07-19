import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.core.container import dashboard_service


st.set_page_config(
    page_title="Stock Intelligence Platform",
    page_icon="📈",
    layout="wide",
)

summary = dashboard_service.get_dashboard_summary()

portfolio = summary["portfolio"]


# -------------------------------------------------------
# Greeting
# -------------------------------------------------------

hour = datetime.now().hour

if hour < 12:
    greeting = "Good Morning"
elif hour < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

st.title("📈 Stock Intelligence Platform")

st.markdown(
    f"### {greeting}, Rishabh 👋"
)

st.write("")


# -------------------------------------------------------
# System Metrics
# -------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Companies",
    summary["companies"],
)

col2.metric(
    "Price Records",
    f"{summary['price_records']:,}",
)

col3.metric(
    "Database Size",
    f"{summary['database_size']} MB",
)

col4.metric(
    "Health",
    summary["health_score"],
)

st.divider()


# -------------------------------------------------------
# Portfolio Summary
# -------------------------------------------------------

st.subheader("Portfolio Summary")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Investment",
    f"₹{portfolio.total_investment:,.2f}",
)

c2.metric(
    "Current Value",
    f"₹{portfolio.current_value:,.2f}",
)

c3.metric(
    "Profit / Loss",
    f"₹{portfolio.total_profit_loss:,.2f}",
)

c4.metric(
    "Return",
    f"{portfolio.total_profit_loss_percent:.2f}%",
)

c5.metric(
    "Winners / Losers",
    f"{portfolio.winners}/{portfolio.losers}",
)

st.divider()


# -------------------------------------------------------
# Holdings
# -------------------------------------------------------

st.subheader("Portfolio Holdings")

rows = []

for position in portfolio.positions:

    rows.append(
        {
            "Symbol": position.symbol,
            "Quantity": position.quantity,
            "Average Price": round(position.average_price, 2),
            "Current Price": round(position.current_price, 2),
            "Investment": round(position.invested_value, 2),
            "Current Value": round(position.current_value, 2),
            "P/L": round(position.profit_loss, 2),
            "P/L %": round(position.profit_loss_percent, 2),
            "Recommendation": position.recommendation.rating,
            "Confidence": position.recommendation.confidence,
        }
    )

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    f"Last refreshed: {datetime.now():%d %b %Y %H:%M:%S}"
)