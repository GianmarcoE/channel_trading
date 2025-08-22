import streamlit as st
import yfinance as yf
from main import main  # assuming main() returns (figs, verdict)

st.set_page_config(page_title="Channel Finder", layout="centered")
st.title("Find trading channel patterns")

# --- User Inputs ---
ticker = st.text_input("Stock Name (Ticker - as in Yahoo Finance):")
own_it = st.radio("Do you own this stock already?", ["No", "Yes"])

period = "1mo"
interval = "30m"

# --- Session state for carousel ---
if "fig_index" not in st.session_state:
    st.session_state.fig_index = 0


# --- Cached functions ---
@st.cache_data
def fetch_data(ticker, period, interval):
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df.reset_index(inplace=True)
    live_price = yf.Ticker(ticker).fast_info["lastPrice"]
    return df, live_price


@st.cache_data
def compute_figs(df, live_price, own_it):
    figs, trends, verdict = main(df, live_price, False, True, own_it)
    return figs, trends, verdict


# --- Main logic ---
if ticker:
    try:
        df, live_price = fetch_data(ticker, period, interval)
        figs, trends, verdict = compute_figs(df, live_price, own_it)

        # --- Carousel for figures ---
        if figs:
            col1, col2, col3 = st.columns([1, 6, 1])
            with col1:
                if st.button("◀"):
                    st.session_state.fig_index = max(0, st.session_state.fig_index - 1)
            with col3:
                if st.button("▶"):
                    st.session_state.fig_index = min(len(figs) - 1, st.session_state.fig_index + 1)

            st.pyplot(figs[st.session_state.fig_index])
            st.caption(f"Trend {st.session_state.fig_index + 1} of {len(figs)} - {trends[st.session_state.fig_index]}")

        # --- Verdict display ---
        if "Hold" in verdict:
            st.warning(f"Overall recommendation: {verdict}")
        if "Buy" in verdict:
            st.success(f"Overall recommendation: {verdict}")
        if "Sell" in verdict:
            st.error(f"Overall recommendation: {verdict}")

    except Exception as e:
        st.error(e)
else:
    st.info("👆 Enter a ticker and press Enter to start")
