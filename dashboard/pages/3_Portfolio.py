import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.bootstrap import Bootstrap


st.set_page_config(
    page_title="Portfolio | Stock Intelligence Platform",
    page_icon="💼",
    layout="wide",
)


@st.cache_resource
def get_bootstrap() -> Bootstrap:
    return Bootstrap()


@st.cache_data(ttl=900, show_spinner=False)
def load_market_stats(_service, holding_keys):
    result = {}
    for company_id, symbol in holding_keys:
        try:
            result[symbol] = {
                "stats": _service.get_stats(
                    symbol,
                    company_id=company_id,
                    refresh=True,
                ),
                "error": None,
            }
        except Exception as exc:
            result[symbol] = {
                "stats": None,
                "error": str(exc),
            }
    return result


def money_column() -> st.column_config.NumberColumn:
    return st.column_config.NumberColumn(format="₹%.2f")


def percent_column() -> st.column_config.NumberColumn:
    return st.column_config.NumberColumn(format="%.2f%%")


bootstrap = get_bootstrap()
holdings = bootstrap.portfolio_repository.get_all()

st.title("💼 Portfolio Holdings")
st.caption(
    "Portfolio values and market statistics refresh automatically. Historical "
    "prices use the latest trading day on or before each requested date."
)

if not holdings:
    st.info("No portfolio holdings are available. Import holdings first.")
    st.stop()

company_by_id = {
    company.id: company
    for company in bootstrap.company_repository.list_all()
}
holding_keys = tuple(
    (holding.company_id, company_by_id[holding.company_id].symbol)
    for holding in holdings
    if holding.company_id in company_by_id
)

if st.button("Refresh Market Data"):
    load_market_stats.clear()

with st.spinner("Refreshing portfolio market data..."):
    market_results = load_market_stats(
        bootstrap.stock_market_stats_service,
        holding_keys,
    )

# Market data is refreshed before analysis so the recommendation engine sees
# the latest stored closing prices.
portfolio = bootstrap.portfolio_analyzer.analyze()
positions_by_symbol = {
    position.symbol: position
    for position in portfolio.positions
}

rows = []
refresh_errors = []

for holding in holdings:
    company = company_by_id.get(holding.company_id)
    if company is None:
        continue

    market_result = market_results.get(company.symbol, {})
    stats = market_result.get("stats")
    error = market_result.get("error")
    if error:
        refresh_errors.append(f"{company.symbol}: {error}")

    position = positions_by_symbol.get(company.symbol)
    fallback_price = position.current_price if position is not None else None
    current_price = (
        stats.current_price
        if stats is not None and stats.current_price is not None
        else fallback_price
    )
    invested_value = holding.quantity * holding.average_price
    current_value = (
        holding.quantity * current_price
        if current_price is not None
        else None
    )
    profit_loss = (
        current_value - invested_value
        if current_value is not None
        else None
    )
    profit_loss_percent = (
        profit_loss / invested_value * 100
        if profit_loss is not None and invested_value > 0
        else None
    )
    distance_from_high = (
        (current_price / stats.fifty_two_week_high - 1) * 100
        if (
            stats is not None
            and current_price is not None
            and stats.fifty_two_week_high
        )
        else None
    )

    rows.append(
        {
            "Symbol": company.symbol,
            "Company": company.company_name,
            "Quantity": holding.quantity,
            "Average Price": holding.average_price,
            "Invested Value": invested_value,
            "Current Price": current_price,
            "Current Value": current_value,
            "P/L": profit_loss,
            "P/L %": profit_loss_percent,
            "Allocation %": None,
            "1D Price": stats.price_1d if stats else None,
            "1W Price": stats.price_1w if stats else None,
            "1M Price": stats.price_1m if stats else None,
            "6M Price": stats.price_6m if stats else None,
            "1Y Price": stats.price_1y if stats else None,
            "3Y Price": stats.price_3y if stats else None,
            "1D Return %": stats.return_1d_percent if stats else None,
            "1W Return %": stats.return_1w_percent if stats else None,
            "1M Return %": stats.return_1m_percent if stats else None,
            "6M Return %": stats.return_6m_percent if stats else None,
            "1Y Return %": stats.return_1y_percent if stats else None,
            "3Y Return %": stats.return_3y_percent if stats else None,
            "52W High": stats.fifty_two_week_high if stats else None,
            "52W Low": stats.fifty_two_week_low if stats else None,
            "Distance From 52W High %": distance_from_high,
            "Overall Max": stats.overall_high if stats else None,
            "Overall Min": stats.overall_low if stats else None,
            "Score": position.score.score if position is not None else None,
            "Recommendation": (
                position.recommendation.rating
                if position is not None
                else "Insufficient data"
            ),
            "History Through": stats.price_date if stats else None,
        }
    )

if not rows:
    st.warning("No holdings could be matched with the company master.")
    st.stop()

total_investment = sum(row["Invested Value"] for row in rows)
total_current_value = sum(
    row["Current Value"] or 0.0
    for row in rows
)
total_profit_loss = total_current_value - total_investment
total_return = (
    total_profit_loss / total_investment * 100
    if total_investment > 0
    else 0.0
)

for row in rows:
    row["Allocation %"] = (
        (row["Current Value"] or 0.0) / total_current_value * 100
        if total_current_value > 0
        else 0.0
    )

summary_1, summary_2, summary_3, summary_4 = st.columns(4)
summary_1.metric("Investment", f"₹{total_investment:,.2f}")
summary_2.metric("Current Value", f"₹{total_current_value:,.2f}")
summary_3.metric("Profit / Loss", f"₹{total_profit_loss:,.2f}")
summary_4.metric("Return", f"{total_return:.2f}%")

if refresh_errors:
    with st.expander(
        f"Market data unavailable for {len(refresh_errors)} holding(s)"
    ):
        for message in refresh_errors:
            st.write(f"- {message}")

overview_tab, prices_tab, returns_tab = st.tabs(
    ["Holdings Overview", "Historical Prices", "Period Returns"]
)

with overview_tab:
    overview_columns = [
        "Symbol",
        "Company",
        "Quantity",
        "Average Price",
        "Invested Value",
        "Current Price",
        "Current Value",
        "P/L",
        "P/L %",
        "Allocation %",
        "52W High",
        "52W Low",
        "Distance From 52W High %",
        "Score",
        "Recommendation",
    ]
    st.dataframe(
        pd.DataFrame(rows)[overview_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Average Price": money_column(),
            "Invested Value": money_column(),
            "Current Price": money_column(),
            "Current Value": money_column(),
            "P/L": money_column(),
            "P/L %": percent_column(),
            "Allocation %": percent_column(),
            "52W High": money_column(),
            "52W Low": money_column(),
            "Distance From 52W High %": percent_column(),
        },
    )

with prices_tab:
    price_columns = [
        "Symbol",
        "Current Price",
        "1D Price",
        "1W Price",
        "1M Price",
        "6M Price",
        "1Y Price",
        "3Y Price",
        "52W High",
        "52W Low",
        "Overall Max",
        "Overall Min",
        "History Through",
    ]
    st.dataframe(
        pd.DataFrame(rows)[price_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            column: money_column()
            for column in price_columns
            if column not in {"Symbol", "History Through"}
        },
    )
    st.caption(
        "Historical prices and ranges use adjusted closing values. Overall "
        "Min/Max covers all history currently stored for each stock."
    )

with returns_tab:
    return_columns = [
        "Symbol",
        "1D Return %",
        "1W Return %",
        "1M Return %",
        "6M Return %",
        "1Y Return %",
        "3Y Return %",
    ]
    st.dataframe(
        pd.DataFrame(rows)[return_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            column: percent_column()
            for column in return_columns
            if column != "Symbol"
        },
    )

st.caption(
    "Current price may be intraday when Yahoo provides a live snapshot. "
    "Historical prices and recommendations are descriptive research inputs, "
    "not investment advice."
)
