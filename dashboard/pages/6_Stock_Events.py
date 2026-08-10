import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.bootstrap import Bootstrap


st.set_page_config(
    page_title="Stock Events | Stock Intelligence Platform",
    page_icon="📅",
    layout="wide",
)


@st.cache_resource
def get_bootstrap() -> Bootstrap:
    return Bootstrap()


@st.cache_data(ttl=21600, show_spinner=False)
def load_events(
    _service,
    upcoming_days: int,
    recent_days: int,
    include_holdings: bool,
    include_watchlist: bool,
):
    return _service.list_events(
        upcoming_days=upcoming_days,
        recent_days=recent_days,
        include_holdings=include_holdings,
        include_watchlist=include_watchlist,
    )


def days_label(event_date: date) -> str:
    days = (event_date - date.today()).days
    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    if days > 1:
        return f"In {days} days"
    if days == -1:
        return "Yesterday"
    return f"{abs(days)} days ago"


def event_rows(result) -> list[dict]:
    rows = []
    for tracked in result.events:
        event = tracked.event
        rows.append(
            {
                "Date": event.event_date,
                "When": days_label(event.event_date),
                "Symbol": event.symbol,
                "Company": tracked.company_name,
                "Source List": " + ".join(tracked.sources),
                "Event": event.event_type,
                "Title": event.title,
                "Amount": event.amount,
                "Ratio / Factor": event.ratio,
                "Status": "Estimated" if event.is_estimated else "Reported",
                "Details": event.details or "",
            }
        )
    return rows


bootstrap = get_bootstrap()

st.title("📅 Stock Events")
st.caption(
    "Important dates for your portfolio and watchlist: quarterly results, "
    "dividends, stock splits and bonus-related share adjustments."
)

with st.sidebar:
    st.header("Event Setup")
    include_holdings = st.checkbox("Portfolio Holdings", value=True)
    include_watchlist = st.checkbox("Watchlist", value=True)
    upcoming_days = st.slider(
        "Upcoming window (days)",
        min_value=30,
        max_value=365,
        value=120,
        step=30,
    )
    recent_days = st.slider(
        "Recent history (days)",
        min_value=30,
        max_value=730,
        value=180,
        step=30,
    )

refresh_clicked = st.button(
    "Refresh Events",
    type="primary",
    disabled=not (include_holdings or include_watchlist),
)

if not include_holdings and not include_watchlist:
    st.info("Select Portfolio Holdings, Watchlist, or both.")
    st.stop()

if refresh_clicked:
    load_events.clear()

try:
    with st.spinner("Loading stock events..."):
        result = load_events(
            bootstrap.stock_event_service,
            upcoming_days,
            recent_days,
            include_holdings,
            include_watchlist,
        )
except Exception as exc:
    st.error(f"Events could not be loaded: {exc}")
    st.stop()

if result.failures:
    with st.expander(
        f"Events unavailable for {len(result.failures)} stock(s)",
        expanded=False,
    ):
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Symbol": failure.symbol,
                        "Source List": " + ".join(failure.sources),
                        "Reason": failure.reason,
                    }
                    for failure in result.failures
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

rows = event_rows(result)
if not rows:
    st.info(
        "No events were returned for the selected stocks and date window. "
        "Try a longer history or refresh the data."
    )
    st.stop()

events_df = pd.DataFrame(rows)
today = date.today()
upcoming_df = events_df[events_df["Date"] >= today].copy()
recent_df = events_df[events_df["Date"] < today].copy()

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Upcoming Events", len(upcoming_df))
metric2.metric(
    "Next 30 Days",
    int(
        upcoming_df["Date"].apply(
            lambda value: 0 <= (value - today).days <= 30
        ).sum()
    ),
)
metric3.metric(
    "Result Dates",
    int((upcoming_df["Event"] == "Quarterly Results").sum()),
)
metric4.metric(
    "Corporate Actions",
    int(
        upcoming_df["Event"].isin(
            ["Dividend", "Stock Split / Bonus"]
        ).sum()
    ),
)

st.subheader("Event Filters")
filter1, filter2, filter3 = st.columns(3)
symbols = sorted(events_df["Symbol"].unique())
selected_symbols = filter1.multiselect("Stocks", symbols, default=symbols)
event_types = sorted(events_df["Event"].unique())
selected_types = filter2.multiselect(
    "Event type",
    event_types,
    default=event_types,
)
selected_statuses = filter3.multiselect(
    "Date status",
    ["Estimated", "Reported"],
    default=["Estimated", "Reported"],
)

filtered = events_df[
    events_df["Symbol"].isin(selected_symbols)
    & events_df["Event"].isin(selected_types)
    & events_df["Status"].isin(selected_statuses)
].copy()

column_config = {
    "Date": st.column_config.DateColumn(format="DD MMM YYYY"),
    "Amount": st.column_config.NumberColumn(format="₹%.2f"),
    "Ratio / Factor": st.column_config.NumberColumn(format="%.4f"),
}

upcoming_tab, recent_tab, calendar_tab = st.tabs(
    ["Upcoming", "Recent", "All Events"]
)

with upcoming_tab:
    table = filtered[filtered["Date"] >= today].sort_values(
        ["Date", "Symbol", "Event"]
    )
    if table.empty:
        st.info("No upcoming events match the filters.")
    else:
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config=column_config,
        )

with recent_tab:
    table = filtered[filtered["Date"] < today].sort_values(
        ["Date", "Symbol", "Event"],
        ascending=[False, True, True],
    )
    if table.empty:
        st.info("No recent events match the filters.")
    else:
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config=column_config,
        )

with calendar_tab:
    table = filtered.sort_values(["Date", "Symbol", "Event"])
    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config=column_config,
    )

st.caption(
    "Estimated result dates and Yahoo share-adjustment factors should be "
    "verified against NSE/BSE or the company announcement before acting."
)

