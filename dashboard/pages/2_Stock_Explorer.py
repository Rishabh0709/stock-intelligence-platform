import streamlit as st

st.title("🔍 Stock Explorer")

symbol = st.text_input(
    "Enter Symbol",
    "RELIANCE"
)

if st.button("Search"):

    st.write(symbol)