import streamlit as st
import pandas as pd

st.title("📦 MANZY MAMUNA WA GLORY")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["Date", "Description", "Received", "Issued", "Balance"]
    )
    st.session_state.balance = 0

st.header("Add Transaction")

date = st.date_input("Date")
description = st.selectbox("Type", ["Received", "Issued"])
quantity = st.number_input("Quantity", min_value=0, step=1)

if st.button("Add Entry"):
    if description == "Received":
        st.session_state.balance += quantity
        received = quantity
        issued = 0
    else:
        if quantity > st.session_state.balance:
            st.error("Not enough stock!")
            st.stop()
        st.session_state.balance -= quantity
        received = 0
        issued = quantity

    new_row = {
        "Date": date,
        "Description": description,
        "Received": received,
        "Issued": issued,
        "Balance": st.session_state.balance,
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])],
        ignore_index=True
    )

    st.success("Transaction added!")

st.header("📊 Stock Card")
st.dataframe(st.session_state.data)

st.subheader(f"📦 Current Balance: {st.session_state.balance}")

csv = st.session_state.data.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "stock_card.csv", "text/csv")
