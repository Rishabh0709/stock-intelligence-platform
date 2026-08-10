import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.bootstrap import Bootstrap


st.set_page_config(
    page_title="Stock Scanner | Stock Intelligence Platform",
    page_icon="🔎",
    layout="wide",
)


@st.cache_resource
def get_bootstrap() -> Bootstrap:
    return Bootstrap()


@st.cache_data(ttl=900, show_spinner=False)
def run_scan(
    _service,
    account_capital,
    risk_percent,
    minimum_rrr,
    include_holdings,
    include_watchlist,
    refresh,
):
    return _service.scan(
        account_capital=account_capital,
        risk_percent=risk_percent,
        minimum_rrr=minimum_rrr,
        include_holdings=include_holdings,
        include_watchlist=include_watchlist,
        refresh=refresh,
    )


def signal_summary(scanned_stock) -> str:
    signals = scanned_stock.result.report.active_signals
    bullish = [signal.name for signal in signals if signal.direction == "bullish"]
    bearish = [signal.name for signal in signals if signal.direction == "bearish"]
    selected = bullish[:2] or bearish[:2]
    return ", ".join(selected) if selected else "No latest-bar trigger"


def result_rows(scan_result) -> list[dict]:
    rows = []
    for stock in scan_result.stocks:
        result = stock.result
        report = result.report
        risk = report.risk
        bullish_count = sum(
            signal.active and signal.direction == "bullish"
            for signal in report.signals
        )
        bearish_count = sum(
            signal.active and signal.direction == "bearish"
            for signal in report.signals
        )
        rows.append(
            {
                "Symbol": result.symbol,
                "Company": result.company_name,
                "Source": " + ".join(stock.sources),
                "Sector": result.sector or "Unknown",
                "Score": report.score.score,
                "Category": report.score.category,
                "Price": risk.entry_price if risk else None,
                "RRR": risk.risk_reward_ratio if risk else None,
                "RRR Eligible": risk.eligible if risk else False,
                "Stop Loss": risk.initial_stop if risk else None,
                "Resistance": risk.resistance if risk else None,
                "Quantity": risk.quantity if risk else None,
                "Bullish Signals": bullish_count,
                "Bearish Signals": bearish_count,
                "Key Signal": signal_summary(stock),
                "Stale": result.is_stale,
                "Price Date": result.price_as_of,
            }
        )
    return rows


bootstrap = get_bootstrap()

st.title("🔎 Stock Intelligence Scanner")
st.caption(
    "Ranks your Holdings and Watchlist using explainable trend, momentum, "
    "volatility, volume and risk rules. Signals are decision support, not "
    "investment advice."
)

with st.sidebar:
    st.header("Scanner Setup")
    account_capital = st.number_input(
        "Trading capital",
        min_value=10_000.0,
        value=500_000.0,
        step=10_000.0,
        format="%.0f",
    )
    risk_percent = st.number_input(
        "Maximum risk per trade (%)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
    )
    minimum_rrr = st.number_input(
        "Minimum acceptable RRR",
        min_value=0.5,
        max_value=10.0,
        value=2.5,
        step=0.1,
    )
    st.subheader("Universe")
    include_holdings = st.checkbox("Portfolio Holdings", value=True)
    include_watchlist = st.checkbox("Watchlist", value=True)
    refresh_market_data = st.checkbox(
        "Refresh market data before scan",
        value=False,
        help="Slower. Leave off for fast scans using stored prices.",
    )

run_clicked = st.button(
    "Run Scanner",
    type="primary",
    disabled=not (include_holdings or include_watchlist),
)

if run_clicked:
    if refresh_market_data:
        run_scan.clear()
    try:
        with st.spinner("Analysing Holdings and Watchlist..."):
            st.session_state["stock_scanner_result"] = run_scan(
                bootstrap.stock_scanner_service,
                account_capital,
                risk_percent,
                minimum_rrr,
                include_holdings,
                include_watchlist,
                refresh_market_data,
            )
        st.session_state["stock_scanner_settings"] = {
            "account_capital": account_capital,
            "risk_percent": risk_percent,
            "minimum_rrr": minimum_rrr,
        }
    except Exception as exc:
        st.error(f"Scanner failed: {exc}")

scan_result = st.session_state.get("stock_scanner_result")
if scan_result is None:
    st.info("Choose the universe and risk settings, then click **Run Scanner**.")
    st.stop()

if scan_result.failures:
    with st.expander(f"{len(scan_result.failures)} stock(s) could not be analysed"):
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Symbol": failure.symbol,
                        "Source": " + ".join(failure.sources),
                        "Reason": failure.reason,
                    }
                    for failure in scan_result.failures
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

rows = result_rows(scan_result)
if not rows:
    st.warning("No stocks could be analysed. Review the failure details above.")
    st.stop()

raw_table = pd.DataFrame(rows)
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Analysed", len(raw_table))
metric2.metric("Score 60+", int((raw_table["Score"] >= 60).sum()))
metric3.metric("RRR Eligible", int(raw_table["RRR Eligible"].sum()))
metric4.metric("Stale Data", int(raw_table["Stale"].sum()))

st.subheader("Ranked Opportunities")
filter1, filter2, filter3, filter4 = st.columns(4)
minimum_score = filter1.slider("Minimum score", 0, 100, 40, 5)
categories = sorted(raw_table["Category"].unique())
selected_categories = filter2.multiselect(
    "Category",
    categories,
    default=categories,
)
sectors = sorted(raw_table["Sector"].unique())
selected_sectors = filter3.multiselect("Sector", sectors, default=sectors)
eligible_only = filter4.checkbox("RRR eligible only", value=False)

all_signal_names = sorted(
    {
        signal.name
        for stock in scan_result.stocks
        for signal in stock.result.report.active_signals
    }
)
selected_signal = st.selectbox(
    "Active signal",
    ["All signals", *all_signal_names],
)

filtered = raw_table[
    (raw_table["Score"] >= minimum_score)
    & raw_table["Category"].isin(selected_categories)
    & raw_table["Sector"].isin(selected_sectors)
].copy()
if eligible_only:
    filtered = filtered[filtered["RRR Eligible"]]
if selected_signal != "All signals":
    symbols_with_signal = {
        stock.result.symbol
        for stock in scan_result.stocks
        if any(
            signal.active and signal.name == selected_signal
            for signal in stock.result.report.signals
        )
    }
    filtered = filtered[filtered["Symbol"].isin(symbols_with_signal)]

filtered = filtered.sort_values(["Score", "RRR"], ascending=[False, False])
st.dataframe(
    filtered[
        [
            "Symbol", "Source", "Sector", "Score", "Category", "Price",
            "RRR", "RRR Eligible", "Stop Loss", "Resistance", "Quantity",
            "Bullish Signals", "Bearish Signals", "Key Signal", "Price Date",
        ]
    ],
    hide_index=True,
    use_container_width=True,
    column_config={
        "Score": st.column_config.ProgressColumn(min_value=0, max_value=100),
        "Price": st.column_config.NumberColumn(format="₹%.2f"),
        "Stop Loss": st.column_config.NumberColumn(format="₹%.2f"),
        "Resistance": st.column_config.NumberColumn(format="₹%.2f"),
        "RRR": st.column_config.NumberColumn(format="%.2f"),
    },
)

if filtered.empty:
    st.info("No stocks match the current filters.")
    st.stop()

st.divider()
st.subheader("Stock Drill-down")
selected_symbol = st.selectbox("Stock", filtered["Symbol"].tolist())
selected = next(
    stock for stock in scan_result.stocks if stock.result.symbol == selected_symbol
)
result = selected.result
report = result.report
risk = report.risk

score_col, price_col, rrr_col, stop_col, target_col = st.columns(5)
score_col.metric("Intelligence Score", f"{report.score.score}/100")
price_col.metric("Price", f"₹{risk.entry_price:,.2f}" if risk else "N/A")
rrr_col.metric(
    "Risk–Reward",
    f"{risk.risk_reward_ratio:.2f}" if risk and risk.risk_reward_ratio else "N/A",
)
stop_col.metric("ATR Stop", f"₹{risk.initial_stop:,.2f}" if risk else "N/A")
target_col.metric(
    "Resistance",
    f"₹{risk.resistance:,.2f}" if risk and risk.resistance else "N/A",
)
st.caption(
    f"{result.company_name} · {' + '.join(selected.sources)} · "
    f"{result.history_rows} sessions · data through {result.price_as_of}"
)

chart_frame = result.indicator_frame.tail(260)
figure = go.Figure()
figure.add_trace(
    go.Candlestick(
        x=chart_frame["Date"],
        open=chart_frame["Open"],
        high=chart_frame["High"],
        low=chart_frame["Low"],
        close=chart_frame["Close"],
        name="Price",
    )
)
for column, label, color in (
    ("EMA_20", "EMA 20", "#00A6A6"),
    ("SMA_50", "SMA 50", "#F4A261"),
    ("SMA_200", "SMA 200", "#8E44AD"),
):
    figure.add_trace(
        go.Scatter(
            x=chart_frame["Date"],
            y=chart_frame[column],
            mode="lines",
            name=label,
            line={"width": 1.5, "color": color},
        )
    )
figure.update_layout(
    height=500,
    margin={"l": 10, "r": 10, "t": 20, "b": 10},
    xaxis_rangeslider_visible=False,
    legend_orientation="h",
)
st.plotly_chart(figure, use_container_width=True)

score_tab, signals_tab, risk_tab = st.tabs(
    ["Score Breakdown", "Signals", "Risk & Position Size"]
)
with score_tab:
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Factor": component.label,
                    "Points": component.points,
                    "Maximum": component.max_points,
                    "Status": "Passed" if component.passed else "Not met",
                    "Explanation": component.explanation,
                }
                for component in report.score.components
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )

with signals_tab:
    show_inactive = st.checkbox("Show inactive rules", value=False)
    signal_rows = [
        {
            "Signal": signal.name,
            "Direction": signal.direction.title(),
            "Status": "Active" if signal.active else "Inactive",
            "Explanation": signal.explanation,
            "Measured Values": ", ".join(
                f"{key}={value}" for key, value in signal.values.items()
                if value is not None
            ),
        }
        for signal in report.signals
        if show_inactive or signal.active
    ]
    if signal_rows:
        st.dataframe(pd.DataFrame(signal_rows), hide_index=True, use_container_width=True)
    else:
        st.info("No signal triggered on the latest data.")

with risk_tab:
    if risk is None:
        st.info("Risk metrics are unavailable.")
    else:
        saved_settings = st.session_state.get("stock_scanner_settings", {})
        st.write(
            f"At **{saved_settings.get('risk_percent', risk_percent):.1f}%** risk on "
            f"**₹{saved_settings.get('account_capital', account_capital):,.0f}** capital, "
            f"the ATR-based position size is **{risk.quantity:,} shares** "
            f"(approximately **₹{risk.position_value:,.2f}**)."
        )
        risk_table = pd.DataFrame(
            {
                "Metric": [
                    "ATR (14)", "Initial stop (2× ATR)",
                    "Trailing stop (2.5× ATR)", "Risk per share",
                    "Account risk amount", "Resistance", "Reward per share",
                    "Risk–reward ratio", "Passes RRR gate",
                ],
                "Value": [
                    f"₹{risk.atr:,.2f}", f"₹{risk.initial_stop:,.2f}",
                    f"₹{risk.trailing_stop:,.2f}", f"₹{risk.risk_per_share:,.2f}",
                    f"₹{risk.account_risk_amount:,.2f}",
                    f"₹{risk.resistance:,.2f}" if risk.resistance else "Not available",
                    f"₹{risk.reward_per_share:,.2f}" if risk.reward_per_share is not None else "Not available",
                    f"{risk.risk_reward_ratio:.2f}" if risk.risk_reward_ratio is not None else "Not available",
                    "Yes" if risk.eligible else "No",
                ],
            }
        )
        st.dataframe(risk_table, hide_index=True, use_container_width=True)

st.caption(
    "VWAP bias uses 5-session and 20-session rolling volume-weighted price "
    "proxies because the stored dataset contains end-of-day candles, not "
    "intraday trades. Portfolio transaction history is not used by this scanner."
)
