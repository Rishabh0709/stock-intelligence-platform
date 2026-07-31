import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.bootstrap import Bootstrap

bootstrap = Bootstrap()
dashboard_service = bootstrap.dashboard_service

st.set_page_config(
    page_title="Stock Intelligence Platform",
    page_icon="📈",
    layout="wide",
)

summary = dashboard_service.get_dashboard_summary()
portfolio = summary["portfolio"]

companies = {
    c.symbol: c
    for c in bootstrap.company_repository.list_all()
}


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def format_money(value: float) -> str:

    value = float(value)

    if abs(value) >= 1e7:
        return f"₹{value/1e7:.2f} Cr"

    elif abs(value) >= 1e5:
        return f"₹{value/1e5:.2f} L"

    elif abs(value) >= 1e3:
        return f"₹{value/1e3:.2f} K"

    return f"₹{value:.2f}"


def recommendation_badge(recommendation):

    rating = recommendation.rating.upper()

    if rating == "BUY":
        st.success("🟢 BUY")

    elif rating == "HOLD":
        st.warning("🟡 HOLD")

    elif rating == "SELL":
        st.error("🔴 SELL")

    else:
        st.info(rating)


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
st.markdown(f"### {greeting}, Rishabh 👋")

st.write("")


# -------------------------------------------------------
# System Metrics
# -------------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Companies",
    summary["companies"],
)

col2.metric(
    "Database Size",
    f"{summary['database_size']} MB",
)

col3.metric(
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
    format_money(portfolio.total_investment),
)

c2.metric(
    "Current Value",
    format_money(portfolio.current_value),
)

c3.metric(
    "Profit / Loss",
    format_money(portfolio.total_profit_loss),
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
# Portfolio Allocation
# -------------------------------------------------------

st.subheader("Portfolio Allocation")

allocation_rows = []

for p in portfolio.positions:
    allocation_rows.append(
        {
            "Symbol": p.symbol,
            "Value": p.current_value,
        }
    )

allocation_df = (
    pd.DataFrame(allocation_rows)
    .sort_values(
        "Value",
        ascending=False,
    )
)

allocation_df["Allocation"] = (
    allocation_df["Value"]
    / allocation_df["Value"].sum()
    * 100
)

top10 = allocation_df.head(10).copy()

others = allocation_df.iloc[10:]

if not others.empty:
    top10.loc[len(top10)] = {
        "Symbol": "Others",
        "Value": others["Value"].sum(),
        "Allocation": others["Allocation"].sum(),
    }

fig = px.bar(
    top10,
    x="Allocation",
    y="Symbol",
    orientation="h",
    text="Allocation",
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)

fig.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis_title="Allocation (%)",
    yaxis_title="",
    height=450,
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.divider()

# -------------------------------------------------------
# Sector Allocation
# -------------------------------------------------------

st.subheader("Sector Allocation")

sector_rows = []

for position in portfolio.positions:

    company = companies[position.symbol]

    sector_rows.append(
        {
            "Sector": company.sector or "Unknown",
            "Value": position.current_value,
        }
    )

sector_df = (
    pd.DataFrame(sector_rows)
    .groupby("Sector", as_index=False)["Value"]
    .sum()
    .sort_values(
        "Value",
        ascending=False,
    )
)

sector_df["Allocation"] = (
    sector_df["Value"]
    / sector_df["Value"].sum()
    * 100
)

top10 = sector_df.head(10).copy()

others = sector_df.iloc[10:]

if not others.empty:

    top10.loc[len(top10)] = {
        "Sector": "Others",
        "Value": others["Value"].sum(),
        "Allocation": others["Allocation"].sum(),
    }

fig = px.bar(
    top10,
    x="Allocation",
    y="Sector",
    orientation="h",
    text="Allocation",
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)

fig.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis_title="Allocation (%)",
    yaxis_title="",
    height=420,
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# -------------------------------------------------------
# Top Winners & Losers
# -------------------------------------------------------

left, right = st.columns(2)

positions_df = pd.DataFrame(
    [
        {
            "Symbol": p.symbol,
            "P/L %": p.profit_loss_percent,
            "P/L": p.profit_loss,
        }
        for p in portfolio.positions
    ]
)

with left:

    st.subheader("🏆 Top Winners")

    winners = (
        positions_df
        .sort_values("P/L %", ascending=False)
        .head(5)
    )

    for _, row in winners.iterrows():

        c1, c2 = st.columns([3, 1])

        c1.write(f"**{row['Symbol']}**")

        c2.success(f"{row['P/L %']:.2f}%")

with right:

    st.subheader("📉 Top Losers")

    losers = (
        positions_df
        .sort_values("P/L %")
        .head(5)
    )

    for _, row in losers.iterrows():

        c1, c2 = st.columns([3, 1])

        c1.write(f"**{row['Symbol']}**")

        c2.error(f"{row['P/L %']:.2f}%")

# -------------------------------------------------------
# Recommendation Distribution
# -------------------------------------------------------

st.subheader("Recommendation Distribution")

recommendation_df = pd.DataFrame(
    [
        {
            "Recommendation": p.recommendation.rating,
        }
        for p in portfolio.positions
    ]
)

recommendation_df = (
    recommendation_df
    .groupby("Recommendation")
    .size()
    .reset_index(name="Count")
)

fig = px.pie(
    recommendation_df,
    names="Recommendation",
    values="Count",
    hole=0.45,
)

fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),
    height=400,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# -------------------------------------------------------
# Portfolio Insights
# -------------------------------------------------------

st.subheader("Portfolio Insights")

best = max(
    portfolio.positions,
    key=lambda p: p.profit_loss_percent,
)

worst = min(
    portfolio.positions,
    key=lambda p: p.profit_loss_percent,
)

largest = max(
    portfolio.positions,
    key=lambda p: p.current_value,
)

buy_count = sum(
    1
    for p in portfolio.positions
    if p.recommendation.rating == "BUY"
)

hold_count = sum(
    1
    for p in portfolio.positions
    if p.recommendation.rating == "HOLD"
)

sell_count = sum(
    1
    for p in portfolio.positions
    if p.recommendation.rating == "SELL"
)

c1, c2 = st.columns(2)

with c1:

    st.info(
        f"""
### 📌 Portfolio Highlights

• Largest Holding : **{largest.symbol}**

• Best Performer : **{best.symbol}** ({best.profit_loss_percent:.2f}%)

• Worst Performer : **{worst.symbol}** ({worst.profit_loss_percent:.2f}%)

• Winners : **{portfolio.winners}**

• Losers : **{portfolio.losers}**
"""
    )

with c2:

    st.success(
        f"""
### 🤖 Recommendation Summary

• BUY : **{buy_count}**

• HOLD : **{hold_count}**

• SELL : **{sell_count}**
"""
    )

left, right = st.columns(2)

with left:

    st.subheader("🏆 Top Winners")

    winners = sorted(
        portfolio.positions,
        key=lambda x: x.profit_loss_percent,
        reverse=True,
    )[:5]

    for p in winners:

        st.metric(
            p.symbol,
            f"{p.profit_loss_percent:.2f}%",
        )

with right:

    st.subheader("📉 Top Losers")

    losers = sorted(
        portfolio.positions,
        key=lambda x: x.profit_loss_percent,
    )[:5]

    for p in losers:

        st.metric(
            p.symbol,
            f"{p.profit_loss_percent:.2f}%",
        )


# -------------------------------------------------------
# Portfolio Layout
# -------------------------------------------------------

left, right = st.columns([2.2, 1.2])


# =======================================================
# LEFT PANEL
# =======================================================

with left:

    st.subheader("Portfolio Holdings")

    rows = []

    for position in portfolio.positions:

        rows.append(
            {
                "Symbol": position.symbol,
                "Qty": position.quantity,
                
                "P/L %": round(position.profit_loss_percent, 2),
                "Score": position.score.score,
                "Recommendation": position.recommendation.rating,
            }
        )

    df = pd.DataFrame(rows)
       

    st.subheader("Portfolio Explorer")

    left, right = st.columns([2, 1])
    
    with left:

        explorer_rows = []

        for p in portfolio.positions:

            explorer_rows.append(
            {
                "Symbol": p.symbol,
                "Score": p.score.score,
                "Recommendation": p.recommendation.rating,
                "P/L %": round(
                    p.profit_loss_percent,
                    2,
                ),
            }
            )

        explorer_df = (
            pd.DataFrame(explorer_rows)
            .sort_values("Score", ascending=False,)
            )

        selected_symbol = st.radio(

        "Select Holding",

        explorer_df["Symbol"],

        label_visibility="collapsed",
        )

        selected = next(

        p

        for p in portfolio.positions

        if p.symbol == selected_symbol
        )
        
    with right:

        st.subheader(selected.symbol)

        st.metric(
        "Recommendation",
        selected.recommendation.rating,
        )

        st.metric(
        "Score",
        f"{selected.score.score}/{selected.score.max_score}",
        )

        st.progress(
        max(
            0,
            min(
                selected.score.score /
                selected.score.max_score,
                1,
            ),
            )
        )
        
        st.write("### Position")

        c1, c2 = st.columns(2)

        c1.metric(
            "Investment",
            format_money(selected.invested_value),
        )

        c2.metric(
            "Current Value",
            format_money(selected.current_value),
        )

        c1.metric(
            "Current Price",
            f"₹{selected.current_price:.2f}",
        )

        c2.metric(
            "Return",
            f"{selected.profit_loss_percent:.2f}%",
        )
        
        st.write("### Recommendation")

        st.info(
            selected.recommendation.summary)
        
        st.write("### Score Breakdown")

        for result in selected.score.results:

            st.markdown(
                f"**{result.rule}**"
            )

            score_fraction = max(0,
            min(result.points / 10,1,),
            )

            st.progress(score_fraction)

            st.caption(result.reason)

            st.write(f"Points: {result.points}")
        
        trend = selected.analysis.trend.analyze()
        
        st.write("### Technical Indicators")

        st.metric(
            "20 SMA",
            "-" if trend.sma20 is None else f"{trend.sma20:.2f}",
            )

        st.metric(
            "50 SMA",
            "-" if trend.sma50 is None else f"{trend.sma50:.2f}",
            )

        st.metric(
            "200 SMA",
            "-" if trend.sma200 is None else f"{trend.sma200:.2f}",
            )

        st.metric(
            "EMA20",
            "-" if trend.ema20 is None else f"{trend.ema20:.2f}",
            )

        st.metric(
            "ADX",
            "-" if trend.adx is None else f"{trend.adx:.2f}",
            )
        
        st.write("### Trend")

        st.success(f"{trend.trend.value} ({trend.strength.value})")
        
# =======================================================
# RIGHT PANEL
# =======================================================

with right:

    st.subheader("Stock Details")

    selected_symbol = st.selectbox(
        "Select Stock",
        [p.symbol for p in portfolio.positions],
    )

    selected = next(
        p
        for p in portfolio.positions
        if p.symbol == selected_symbol
    )

    score_percent = max(0,
        min(1,selected.score.score /
        selected.score.max_score)
    )

    st.metric(
        "Overall Score",
        f"{selected.score.score}/{selected.score.max_score}",
    )

    st.progress(score_percent)

    recommendation_badge(
        selected.recommendation
    )

    st.divider()

    st.metric(
        "Current Price",
        format_money(selected.current_price),
    )

    st.metric(
        "Average Price",
        format_money(selected.average_price),
    )

    st.metric(
        "Quantity",
        selected.quantity,
    )

    st.metric(
        "Investment",
        format_money(selected.invested_value),
    )

    st.metric(
        "Current Value",
        format_money(selected.current_value),
    )

    st.metric(
        "Profit / Loss",
        f"{selected.profit_loss_percent:.2f}%",
    )

    st.divider()

    with st.expander(
        "Why this recommendation?",
        expanded=True,
    ):

        for result in selected.score.results:

            icon = "✅" if result.passed else "⚠️"

            st.markdown(
                f"### {icon} {result.rule}"
            )

            progress = max(0.0,min(result.points / 25,1.0,),)

            st.progress(progress)

            st.write(
                f"**Points:** {result.points}"
            )

            st.write(
                result.reason
            )

            st.divider()


st.caption(
    f"Last refreshed: {datetime.now():%d %b %Y %H:%M:%S}"
)
