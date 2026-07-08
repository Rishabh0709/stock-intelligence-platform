import sys
from pathlib import Path
from config.settings import DATABASE_PATH


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


import streamlit as st
from datetime import datetime
from src.services.dashboard_service import DashboardService

from src.core.container import dashboard_service

summary = dashboard_service.get_summary()

st.write(DATABASE_PATH)

st.set_page_config(
    page_title="Stock Intelligence Platform",
    page_icon="📈",
    layout="wide"
)


hour = datetime.now().hour

if hour < 12:
    greeting = "Good Morning"
elif hour < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"
    

st.markdown(
    f"""
## {greeting}, Rishabh 👋

Welcome back to your Investment Intelligence Platform.
"""
)

st.success(
"""
Portfolio Status

🟢 System Ready

Database Connected

Ready for Analysis
"""
)

with st.sidebar:

    st.title("Navigation")

    st.success("Database Connected")

    st.write("---")

    st.write("Version")

    st.code("v0.2")
    
col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
    "🏢 Companies",
    summary["companies"]
    )

with col2:

    st.metric(
    "📈 Price Records",
    f"{summary['price_records']:,}"
    )

with col3:

    st.metric(
    "💰 Portfolio",
    f"₹{summary['portfolio_value']:,}"
    )

with col4:

    st.metric(
    "❤️ Health",
    summary["health_score"]
    )

st.subheader("System Status")

col1, col2 = st.columns(2)

with col1:

    st.success("Database Connected")

with col2:

    st.info(
        f"Database Size : {summary['database_size']} MB"
    )

st.caption(
    f"Last refreshed: {datetime.now():%d %b %Y %H:%M:%S}"
)