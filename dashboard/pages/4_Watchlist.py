import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.bootstrap import Bootstrap


st.set_page_config(
    page_title="Watchlist | Stock Intelligence Platform",
    page_icon="👁️",
    layout="wide",
)


@st.cache_resource
def get_bootstrap() -> Bootstrap:
    return Bootstrap()


bootstrap = get_bootstrap()
watchlist_service = bootstrap.watchlist_service
analysis_service = bootstrap.watchlist_analysis_service


@st.cache_data(ttl=900, show_spinner=False)
def load_watchlist_overview(_service):
    return _service.get_overview(refresh=True)


st.title("👁️ Watchlist")
st.caption(
    "Enter only the NSE stock symbol, target price and alert price. "
    "Market prices and historical ranges are populated automatically."
)

if st.button("Refresh Market Data"):
    load_watchlist_overview.clear()

try:
    with st.spinner("Refreshing watchlist market data..."):
        overview = load_watchlist_overview(watchlist_service)
except Exception as exc:
    st.warning(
        "Live refresh was unavailable. Showing the latest stored prices. "
        f"Reason: {exc}"
    )
    overview = watchlist_service.get_overview()

items = [row.item for row in overview]
items_by_symbol = {item.symbol: item for item in items}

if overview:
    overview = sorted(
        overview,
        key=lambda row: row.item.symbol,
    )
    table = pd.DataFrame(
        [
            {
                "Symbol": row.item.symbol,
                "Company": row.item.company_name,
                "Current Price": row.current_price,
                "1D Price": row.price_1d,
                "1W Price": row.price_1w,
                "1M Price": row.price_1m,
                "6M Price": row.price_6m,
                "1Y Price": row.price_1y,
                "3Y Price": row.price_3y,
                "52W High": row.fifty_two_week_high,
                "52W Low": row.fifty_two_week_low,
                "Overall Max": row.overall_high,
                "Overall Min": row.overall_low,
                "Target Price": row.item.target_price,
                "Alert Price": row.item.alert_price,
                "Target Upside %": row.upside_to_target_percent,
                "Alert Status": (
                    "Triggered" if row.alert_triggered else "Not triggered"
                ),
                "History Through": row.price_date,
            }
            for row in overview
        ]
    )
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current Price": st.column_config.NumberColumn(format="₹%.2f"),
            "1D Price": st.column_config.NumberColumn(format="₹%.2f"),
            "1W Price": st.column_config.NumberColumn(format="₹%.2f"),
            "1M Price": st.column_config.NumberColumn(format="₹%.2f"),
            "6M Price": st.column_config.NumberColumn(format="₹%.2f"),
            "1Y Price": st.column_config.NumberColumn(format="₹%.2f"),
            "3Y Price": st.column_config.NumberColumn(format="₹%.2f"),
            "52W High": st.column_config.NumberColumn(format="₹%.2f"),
            "52W Low": st.column_config.NumberColumn(format="₹%.2f"),
            "Overall Max": st.column_config.NumberColumn(format="₹%.2f"),
            "Overall Min": st.column_config.NumberColumn(format="₹%.2f"),
            "Target Price": st.column_config.NumberColumn(format="₹%.2f"),
            "Alert Price": st.column_config.NumberColumn(format="₹%.2f"),
            "Target Upside %": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )
    st.caption(
        "Historical columns use adjusted closing prices. Each lookback uses "
        "the latest trading day on or before the requested date. Overall "
        "Min/Max covers all history currently stored for that stock."
    )
else:
    st.info("Your watchlist is empty. Add the first stock below.")

manage_tab, analysis_tab = st.tabs(
    ["Manage Watchlist", "Quantitative Review"]
)

with manage_tab:
    mode = st.radio(
        "Action",
        ["Add stock", "Edit stock"],
        horizontal=True,
        disabled=not items,
    )

    selected_item = None
    if mode == "Edit stock" and items:
        selected_symbol = st.selectbox(
            "Stock to edit",
            sorted(items_by_symbol),
        )
        selected_item = items_by_symbol[selected_symbol]

    with st.form("watchlist_form", clear_on_submit=selected_item is None):
        symbol = st.text_input(
            "Stock name (NSE symbol)",
            value=selected_item.symbol if selected_item else "",
            disabled=selected_item is not None,
            placeholder="e.g. RELIANCE",
        )

        col1, col2 = st.columns(2)
        target_price = col1.number_input(
            "Target price",
            min_value=0.0,
            value=float(selected_item.target_price or 0.0)
            if selected_item else 0.0,
            step=1.0,
        )
        alert_price = col2.number_input(
            "Alert price",
            min_value=0.0,
            value=float(selected_item.alert_price or 0.0)
            if selected_item else 0.0,
            step=1.0,
        )

        submitted = st.form_submit_button(
            "Save Watchlist Stock",
            type="primary",
        )

    if submitted:
        try:
            with st.spinner("Saving and validating the stock symbol..."):
                watchlist_service.save(
                    symbol=symbol,
                    target_price=target_price or None,
                    alert_price=alert_price or None,
                )
            load_watchlist_overview.clear()
            st.success(f"{symbol.upper()} saved to the watchlist.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    if items:
        st.divider()
        st.subheader("Remove Stock")
        remove_symbol = st.selectbox(
            "Stock to remove",
            sorted(items_by_symbol),
            key="remove_symbol",
        )
        confirm = st.checkbox(
            f"Confirm removal of {remove_symbol}",
        )
        if st.button(
            "Remove from Watchlist",
            disabled=not confirm,
        ):
            watchlist_service.remove(
                items_by_symbol[remove_symbol].company_id
            )
            load_watchlist_overview.clear()
            st.success(f"{remove_symbol} removed.")
            st.rerun()

with analysis_tab:
    if not items:
        st.info("Add a stock before opening its quantitative review.")
    else:
        analysis_symbol = st.selectbox(
            "Stock to review",
            sorted(items_by_symbol),
            key="analysis_symbol",
        )
        item = items_by_symbol[analysis_symbol]

        st.caption(
            "Refreshes stored prices and calculates deterministic metrics. "
            "No LLM or AI API is used."
        )

        if st.button(
            "Refresh and Analyze",
            type="primary",
        ):
            try:
                with st.spinner("Refreshing prices and calculating metrics..."):
                    result = analysis_service.analyze(
                        analysis_symbol,
                        target_price=item.target_price,
                        alert_price=item.alert_price,
                    )
                st.session_state["watchlist_analysis_result"] = result
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

        result = st.session_state.get("watchlist_analysis_result")
        if result is not None and result.symbol == analysis_symbol:
            st.caption(
                f"{result.company_name} · Market data through "
                f"{result.price_as_of}"
            )

            price_col, return_col, risk_col, target_col = st.columns(4)
            price_col.metric(
                "Current Price",
                f"₹{result.current_price:,.2f}",
            )
            return_1y = result.returns_percent["1_year"]
            return_col.metric(
                "1-Year Return",
                "N/A" if return_1y is None else f"{return_1y:.2f}%",
            )
            volatility = result.risk["annualized_volatility_1y"]
            risk_col.metric(
                "1-Year Volatility",
                "N/A" if volatility is None else f"{volatility:.2f}%",
            )
            target_upside = (
                None
                if item.target_price is None
                else (item.target_price / result.current_price - 1) * 100
            )
            target_col.metric(
                "Upside to Target",
                "N/A"
                if target_upside is None
                else f"{target_upside:.2f}%",
            )

            chart_data = pd.DataFrame(result.price_history).set_index("Date")
            st.line_chart(
                chart_data,
                y="Adjusted Close",
                height=360,
            )

            st.subheader("Returns")
            returns_table = pd.DataFrame(
                [
                    {
                        "Period": period.replace("_", " ").title(),
                        "Return %": value,
                    }
                    for period, value in result.returns_percent.items()
                ]
            )
            st.dataframe(
                returns_table,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Return %": st.column_config.NumberColumn(format="%.2f%%")
                },
            )

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Trend and Risk")
                metric_rows = [
                    {
                        "Metric": "50-day moving average",
                        "Value": result.technical[
                            "50_day_moving_average"
                        ],
                    },
                    {
                        "Metric": "200-day moving average",
                        "Value": result.technical[
                            "200_day_moving_average"
                        ],
                    },
                    {
                        "Metric": "1-year maximum drawdown %",
                        "Value": result.risk["maximum_drawdown_1y"],
                    },
                    {
                        "Metric": "52-week high",
                        "Value": result.price["52_week_high"],
                    },
                    {
                        "Metric": "52-week low",
                        "Value": result.price["52_week_low"],
                    },
                ]
                st.dataframe(
                    pd.DataFrame(metric_rows),
                    hide_index=True,
                    use_container_width=True,
                )

            with col2:
                st.subheader("Valuation Snapshot")
                valuation_labels = {
                    "market_cap": "Market cap",
                    "trailing_pe": "Trailing P/E",
                    "forward_pe": "Forward P/E",
                    "price_to_book": "Price to book",
                    "peg_ratio": "PEG ratio",
                    "dividend_yield": "Dividend yield",
                }
                valuation_rows = [
                    {
                        "Metric": valuation_labels[key],
                        "Value": value,
                    }
                    for key, value in result.valuation.items()
                ]
                st.dataframe(
                    pd.DataFrame(valuation_rows),
                    hide_index=True,
                    use_container_width=True,
                )

            st.subheader("Watchlist Signals")
            if result.signals:
                for signal in result.signals:
                    st.write(f"- {signal}")
            else:
                st.info("Not enough data to calculate watchlist signals.")

            st.caption(
                "Metrics are descriptive research inputs, not a buy/sell "
                "recommendation. Verify important data before investing."
            )
