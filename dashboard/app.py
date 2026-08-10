import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.bootstrap import Bootstrap


st.set_page_config(
    page_title="Portfolio Command Centre",
    page_icon="📈",
    layout="wide",
)


@st.cache_resource
def get_bootstrap() -> Bootstrap:
    return Bootstrap()


def price_value(price) -> float:
    return float(
        price.adjusted_close
        if price.adjusted_close is not None
        else price.close_price
    )


def format_money(value: float | None) -> str:
    if value is None:
        return "—"
    value = float(value)
    sign = "-" if value < 0 else ""
    absolute = abs(value)
    if absolute >= 1e7:
        return f"{sign}₹{absolute / 1e7:.2f} Cr"
    if absolute >= 1e5:
        return f"{sign}₹{absolute / 1e5:.2f} L"
    if absolute >= 1e3:
        return f"{sign}₹{absolute / 1e3:.2f} K"
    return f"{sign}₹{absolute:,.2f}"


def format_percent(value: float | None) -> str:
    return "—" if value is None else f"{value:+.2f}%"


def percent_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None or previous <= 0:
        return None
    return (current / previous - 1) * 100


def horizontal_allocation_chart(frame: pd.DataFrame, label_column: str):
    if frame.empty:
        return None
    chart = px.bar(
        frame.sort_values("Allocation %"),
        x="Allocation %",
        y=label_column,
        orientation="h",
        text="Allocation %",
    )
    chart.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        marker_color="#3b82f6",
    )
    chart.update_layout(
        height=280,
        margin=dict(l=0, r=25, t=5, b=0),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
    )
    return chart


@st.cache_data(ttl=900, show_spinner=False)
def load_market_stats(_service, company_keys):
    results = {}
    for company_id, symbol in company_keys:
        try:
            results[symbol] = {
                "stats": _service.get_stats(
                    symbol,
                    company_id=company_id,
                    refresh=False,
                ),
                "error": None,
            }
        except Exception as exc:
            results[symbol] = {"stats": None, "error": str(exc)}
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def load_benchmark_history(_provider, start_date: date, end_date: date):
    try:
        return _provider.get_price_history("^NSEI", start_date, end_date)
    except Exception:
        return []


def build_performance_frame(
    bootstrap: Bootstrap,
    holdings,
    company_by_id,
    period_days: int,
) -> pd.DataFrame:
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    stock_series = []

    for holding in holdings:
        company = company_by_id.get(holding.company_id)
        if company is None:
            continue
        prices = bootstrap.price_repository.get_prices_between(
            holding.company_id,
            start_date,
            end_date,
        )
        if not prices:
            continue
        series = pd.Series(
            {
                price.price_date: price_value(price) * holding.quantity
                for price in prices
            },
            name=company.symbol,
            dtype=float,
        )
        stock_series.append(series)

    if not stock_series:
        return pd.DataFrame()

    values = pd.concat(stock_series, axis=1).sort_index().ffill()
    # Use dates on which every included holding has a value. This prevents
    # newly listed stocks from creating an artificial jump in portfolio value.
    values = values.dropna()
    if values.empty:
        return pd.DataFrame()

    portfolio_value = values.sum(axis=1)
    portfolio_return = (portfolio_value / portfolio_value.iloc[0] - 1) * 100
    result = pd.DataFrame(
        {
            "Date": pd.to_datetime(portfolio_return.index),
            "Portfolio": portfolio_return.values,
        }
    )

    benchmark_prices = load_benchmark_history(
        bootstrap.provider,
        start_date,
        end_date,
    )
    if benchmark_prices:
        benchmark = pd.Series(
            {
                price.price_date: price_value(price)
                for price in benchmark_prices
            },
            name="Nifty 50",
            dtype=float,
        )
        benchmark = (benchmark / benchmark.iloc[0] - 1) * 100
        benchmark_frame = benchmark.rename("Nifty 50").reset_index()
        benchmark_frame.columns = ["Date", "Nifty 50"]
        benchmark_frame["Date"] = pd.to_datetime(benchmark_frame["Date"])
        result = pd.merge_asof(
            result.sort_values("Date"),
            benchmark_frame.sort_values("Date"),
            on="Date",
            direction="backward",
        )

    return result


bootstrap = get_bootstrap()
holdings = bootstrap.portfolio_repository.get_all()
company_by_id = {
    company.id: company
    for company in bootstrap.company_repository.list_all()
    if company.id is not None
}


title_col, action_col = st.columns([4, 1])
with title_col:
    st.title("📈 Portfolio Command Centre")
    st.caption("What changed, what needs attention, and where to act next.")
with action_col:
    st.write("")
    st.write("")
    refresh_clicked = st.button(
        "Refresh Market Data",
        type="primary",
        use_container_width=True,
    )


if refresh_clicked:
    companies_to_refresh = {
        holding.company_id: company_by_id.get(holding.company_id)
        for holding in holdings
    }
    for item in bootstrap.watchlist_repository.list_all():
        companies_to_refresh[item.company_id] = company_by_id.get(item.company_id)

    refresh_errors = []
    progress = st.progress(0.0, text="Refreshing market data...")
    valid_companies = [company for company in companies_to_refresh.values() if company]
    for index, company in enumerate(valid_companies, start=1):
        try:
            bootstrap.price_sync_service.sync(company)
        except Exception as exc:
            refresh_errors.append(f"{company.symbol}: {exc}")
        progress.progress(
            index / len(valid_companies) if valid_companies else 1.0,
            text=f"Refreshing {company.symbol}",
        )
    progress.empty()
    load_market_stats.clear()
    load_benchmark_history.clear()
    if refresh_errors:
        st.warning(
            f"Refresh completed with {len(refresh_errors)} error(s). "
            "Stored prices remain available."
        )
        with st.expander("Refresh errors"):
            for message in refresh_errors:
                st.write(f"- {message}")
    else:
        st.success("Market data refreshed.")


if not holdings:
    st.info(
        "No holdings are available yet. Import your portfolio from the "
        "Portfolio page to activate the command centre."
    )
    st.page_link(
        "pages/3_Portfolio.py",
        label="Open Portfolio",
        icon="💼",
    )
    st.stop()


holding_keys = tuple(
    (holding.company_id, company_by_id[holding.company_id].symbol)
    for holding in holdings
    if holding.company_id in company_by_id
)
market_results = load_market_stats(
    bootstrap.stock_market_stats_service,
    holding_keys,
)
portfolio = bootstrap.portfolio_analyzer.analyze()
positions_by_symbol = {position.symbol: position for position in portfolio.positions}


rows = []
latest_dates = []
for holding in holdings:
    company = company_by_id.get(holding.company_id)
    if company is None:
        continue
    position = positions_by_symbol.get(company.symbol)
    market_result = market_results.get(company.symbol, {})
    stats = market_result.get("stats")
    current_price = (
        stats.current_price
        if stats is not None and stats.current_price is not None
        else position.current_price if position is not None else None
    )
    invested_value = holding.quantity * holding.average_price
    current_value = (
        holding.quantity * current_price if current_price is not None else 0.0
    )
    previous_value = (
        holding.quantity * stats.price_1d
        if stats is not None and stats.price_1d is not None
        else None
    )
    year_ago_value = (
        holding.quantity * stats.price_1y
        if stats is not None and stats.price_1y is not None
        else None
    )
    if stats is not None and stats.price_date:
        latest_dates.append(stats.price_date)
    rows.append(
        {
            "Symbol": company.symbol,
            "Sector": company.sector or "Unknown",
            "Quantity": holding.quantity,
            "Current Price": current_price,
            "Current Value": current_value,
            "Previous Value": previous_value,
            "Year Ago Value": year_ago_value,
            "P/L": current_value - invested_value,
            "P/L %": percent_change(current_value, invested_value),
            "1D %": (
                stats.return_1d_percent if stats is not None else None
            ),
            "1M %": (
                stats.return_1m_percent if stats is not None else None
            ),
            "52W Low": (
                stats.fifty_two_week_low if stats is not None else None
            ),
            "History Through": stats.price_date if stats is not None else None,
            "Data Error": market_result.get("error"),
        }
    )


portfolio_frame = pd.DataFrame(rows)
total_investment = sum(
    holding.quantity * holding.average_price for holding in holdings
)
current_value = float(portfolio_frame["Current Value"].sum())
total_pnl = current_value - total_investment
total_return = percent_change(current_value, total_investment)
previous_values = portfolio_frame["Previous Value"].dropna()
today_pnl = (
    current_value - float(previous_values.sum())
    if len(previous_values) == len(portfolio_frame)
    else None
)
year_ago_values = portfolio_frame["Year Ago Value"].dropna()
portfolio_1y_return = (
    percent_change(current_value, float(year_ago_values.sum()))
    if len(year_ago_values) == len(portfolio_frame)
    else None
)
data_as_of = max(latest_dates) if latest_dates else "No market data"


st.caption(f"Stored market data through: {data_as_of}")
metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric("Current Value", format_money(current_value))
metric_2.metric("Latest-Day P&L", format_money(today_pnl))
metric_3.metric(
    "Total P&L",
    format_money(total_pnl),
    format_percent(total_return),
)
metric_4.metric("1Y Portfolio Proxy", format_percent(portfolio_1y_return))
metric_5.metric("Holdings", str(len(rows)))


# ---------------------------------------------------------------------------
# Needs attention
# ---------------------------------------------------------------------------

st.subheader("Needs Attention")
alerts = []

portfolio_frame["Allocation %"] = (
    portfolio_frame["Current Value"] / current_value * 100
    if current_value > 0
    else 0.0
)
sector_frame = (
    portfolio_frame.groupby("Sector", as_index=False)["Current Value"]
    .sum()
    .sort_values("Current Value", ascending=False)
)
sector_frame["Allocation %"] = (
    sector_frame["Current Value"] / current_value * 100
    if current_value > 0
    else 0.0
)

for row in rows:
    symbol = row["Symbol"]
    if row["Data Error"]:
        alerts.append(("warning", f"{symbol}: market data could not be loaded."))
    if row["Current Price"] and row["52W Low"]:
        distance_from_low = (row["Current Price"] / row["52W Low"] - 1) * 100
        if distance_from_low <= 5:
            alerts.append(
                ("warning", f"{symbol} is {distance_from_low:.1f}% above its 52-week low.")
            )
    if row["1M %"] is not None and row["1M %"] <= -10:
        alerts.append(("error", f"{symbol} has fallen {abs(row['1M %']):.1f}% in one month."))

for _, row in portfolio_frame.iterrows():
    if row["Allocation %"] > 15:
        alerts.append(
            ("warning", f"{row['Symbol']} is {row['Allocation %']:.1f}% of the portfolio.")
        )

for _, row in sector_frame.iterrows():
    if row["Allocation %"] > 30:
        alerts.append(
            ("warning", f"{row['Sector']} is {row['Allocation %']:.1f}% of the portfolio.")
        )

for row in rows:
    if row["History Through"]:
        history_date = date.fromisoformat(row["History Through"])
        if (date.today() - history_date).days > 5:
            alerts.append(
                ("warning", f"{row['Symbol']} data is stale ({row['History Through']}).")
            )

watchlist_rows = []
for item in bootstrap.watchlist_repository.list_all():
    try:
        stats = bootstrap.stock_market_stats_service.get_stats(
            item.symbol,
            company_id=item.company_id,
            refresh=False,
        )
    except Exception:
        continue
    upside = (
        percent_change(item.target_price, stats.current_price)
        if item.target_price is not None
        else None
    )
    distance_to_alert = (
        percent_change(stats.current_price, item.alert_price)
        if item.alert_price is not None
        else None
    )
    status = "Watching"
    if (
        stats.current_price is not None
        and item.alert_price is not None
        and stats.current_price <= item.alert_price
    ):
        status = "Alert triggered"
        alerts.append(("error", f"{item.symbol} crossed its watchlist alert price."))
    elif distance_to_alert is not None and distance_to_alert <= 5:
        status = "Near alert"
    if (
        stats.current_price is not None
        and item.target_price is not None
        and stats.current_price >= item.target_price
    ):
        status = "Target reached"
        alerts.append(("success", f"{item.symbol} reached its watchlist target."))
    watchlist_rows.append(
        {
            "Symbol": item.symbol,
            "CMP": stats.current_price,
            "Alert": item.alert_price,
            "Target": item.target_price,
            "Upside %": upside,
            "Distance to Alert %": distance_to_alert,
            "Status": status,
        }
    )

if alerts:
    alert_columns = st.columns(3)
    for index, (level, message) in enumerate(alerts[:9]):
        with alert_columns[index % 3]:
            getattr(st, level)(message)
    if len(alerts) > 9:
        st.caption(f"{len(alerts) - 9} additional alerts are available on the detailed pages.")
else:
    st.success("No threshold-based alerts need attention.")


# ---------------------------------------------------------------------------
# Portfolio vs Nifty 50
# ---------------------------------------------------------------------------

st.subheader("Portfolio Performance vs Nifty 50")
period_label = st.radio(
    "Performance period",
    ["1M", "6M", "1Y", "3Y"],
    index=2,
    horizontal=True,
    label_visibility="collapsed",
)
period_days = {"1M": 30, "6M": 183, "1Y": 365, "3Y": 1095}[period_label]
performance = build_performance_frame(
    bootstrap,
    holdings,
    company_by_id,
    period_days,
)

if performance.empty or len(performance) < 2:
    st.info("Not enough stored history is available for this comparison.")
else:
    series_columns = [
        column for column in ["Portfolio", "Nifty 50"] if column in performance
    ]
    chart_frame = performance.melt(
        id_vars="Date",
        value_vars=series_columns,
        var_name="Series",
        value_name="Return %",
    )
    performance_chart = px.line(
        chart_frame,
        x="Date",
        y="Return %",
        color="Series",
        color_discrete_map={"Portfolio": "#3b82f6", "Nifty 50": "#f59e0b"},
    )
    performance_chart.update_layout(
        height=360,
        margin=dict(l=0, r=10, t=10, b=0),
        yaxis_title="Return (%)",
        xaxis_title=None,
        legend_title=None,
        hovermode="x unified",
    )
    st.plotly_chart(performance_chart, use_container_width=True)
    ending = performance.iloc[-1]
    performance_columns = st.columns(3)
    performance_columns[0].metric(
        f"Portfolio {period_label}",
        format_percent(float(ending["Portfolio"])),
    )
    if "Nifty 50" in performance and pd.notna(ending.get("Nifty 50")):
        nifty_return = float(ending["Nifty 50"])
        performance_columns[1].metric(
            f"Nifty 50 {period_label}",
            format_percent(nifty_return),
        )
        performance_columns[2].metric(
            "Alpha",
            format_percent(float(ending["Portfolio"]) - nifty_return),
        )
    else:
        performance_columns[1].metric(f"Nifty 50 {period_label}", "Unavailable")
        performance_columns[2].metric("Alpha", "—")
    st.caption(
        "Portfolio performance is a current-holdings proxy: it applies today's "
        "quantities across the selected history and is not transaction-aware."
    )


# ---------------------------------------------------------------------------
# Movers, contributors and watchlist
# ---------------------------------------------------------------------------

left, right = st.columns([1.15, 1])
with left:
    st.subheader("Movers & Contributors")
    movers_tab, contributors_tab = st.tabs(["Latest-Day Movers", "P&L Contributors"])
    with movers_tab:
        movers = portfolio_frame.dropna(subset=["1D %"]).copy()
        movers = movers.sort_values("1D %", ascending=False)
        if movers.empty:
            st.info("Latest-day changes are unavailable.")
        else:
            top = pd.concat([movers.head(3), movers.tail(3)]).drop_duplicates("Symbol")
            st.dataframe(
                top[["Symbol", "1D %", "Current Price"]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "1D %": st.column_config.NumberColumn(format="%.2f%%"),
                    "Current Price": st.column_config.NumberColumn(format="₹%.2f"),
                },
            )
    with contributors_tab:
        contributors = portfolio_frame.sort_values("P/L", ascending=False)
        contributors = pd.concat(
            [contributors.head(3), contributors.tail(3)]
        ).drop_duplicates("Symbol")
        st.dataframe(
            contributors[["Symbol", "P/L", "P/L %"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "P/L": st.column_config.NumberColumn(format="₹%.2f"),
                "P/L %": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

with right:
    st.subheader("Watchlist Opportunities")
    if not watchlist_rows:
        st.info("Your watchlist is empty.")
    else:
        watchlist_frame = pd.DataFrame(watchlist_rows)
        status_order = {
            "Alert triggered": 0,
            "Target reached": 1,
            "Near alert": 2,
            "Watching": 3,
        }
        watchlist_frame["_priority"] = watchlist_frame["Status"].map(status_order)
        watchlist_frame = watchlist_frame.sort_values(
            ["_priority", "Distance to Alert %", "Upside %"],
            ascending=[True, True, False],
            na_position="last",
        ).head(5)
        st.dataframe(
            watchlist_frame[["Symbol", "CMP", "Alert", "Target", "Status"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "CMP": st.column_config.NumberColumn(format="₹%.2f"),
                "Alert": st.column_config.NumberColumn(format="₹%.2f"),
                "Target": st.column_config.NumberColumn(format="₹%.2f"),
            },
        )


# ---------------------------------------------------------------------------
# Compact exposure and navigation
# ---------------------------------------------------------------------------

exposure_left, exposure_right = st.columns(2)
with exposure_left:
    st.subheader("Top Holdings")
    holding_exposure = portfolio_frame.nlargest(5, "Allocation %")[
        ["Symbol", "Allocation %"]
    ]
    holding_chart = horizontal_allocation_chart(holding_exposure, "Symbol")
    if holding_chart is not None:
        st.plotly_chart(holding_chart, use_container_width=True)

with exposure_right:
    st.subheader("Sector Exposure")
    sector_exposure = sector_frame.nlargest(5, "Allocation %")[
        ["Sector", "Allocation %"]
    ]
    sector_chart = horizontal_allocation_chart(sector_exposure, "Sector")
    if sector_chart is not None:
        st.plotly_chart(sector_chart, use_container_width=True)

st.subheader("Quick Actions")
action_1, action_2, action_3, action_4 = st.columns(4)
with action_1:
    st.page_link("pages/3_Portfolio.py", label="View Portfolio", icon="💼", use_container_width=True)
with action_2:
    st.page_link("pages/4_Watchlist.py", label="Open Watchlist", icon="👁️", use_container_width=True)
with action_3:
    st.page_link("pages/2_Stock_Explorer.py", label="Explore Stock", icon="🔎", use_container_width=True)
with action_4:
    st.page_link("pages/1_Data_Manager.py", label="Manage Data", icon="🗂️", use_container_width=True)

st.caption(
    "Threshold alerts are research prompts, not buy or sell recommendations. "
    "Use the detailed pages before making an investment decision."
)