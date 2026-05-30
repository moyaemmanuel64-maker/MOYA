import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# ==============================
# APP CONFIG
# ==============================
st.set_page_config(page_title="PHARMOYA PRO", layout="wide")

st.title("💊 PHARMOYA ENTERPRISE SYSTEM")

# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("pharmoya.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine TEXT,
    batch TEXT,
    expiry TEXT,
    balance INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    medicine TEXT,
    qty INTEGER,
    price REAL,
    total REAL,
    date TEXT
)
""")

conn.commit()

# ==============================
# GOOGLE LOGIN (SIMPLIFIED FLOW)
# ==============================
if "user" not in st.session_state:

    st.header("🔐 Login Required")

    st.info("Use Google email (demo login system)")

    email = st.text_input("Enter Google Email")
    role = st.selectbox("Role", ["pharmacist", "admin"])

    if st.button("Login"):

        if email:
            st.session_state.user = email
            st.session_state.role = role

            cursor.execute(
                "INSERT INTO users VALUES (?, ?)",
                (email, role)
            )
            conn.commit()

            st.rerun()

    st.stop()

# ==============================
# SESSION INFO
# ==============================
st.sidebar.success(f"Logged in as: {st.session_state.user}")
st.sidebar.info(f"Role: {st.session_state.role}")

if st.sidebar.button("Logout"):
    del st.session_state.user
    st.rerun()

# ==============================
# MENU
# ==============================
menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Stock", "Sales", "Expiry Alerts"]
)

# ==============================
# DASHBOARD
# ==============================
if menu == "Dashboard":

    st.header("📊 Dashboard")

    stock = pd.read_sql("SELECT * FROM stock", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    total_sales = sales["total"].sum() if not sales.empty else 0
    total_medicines = len(stock)

    low_stock = stock[stock["balance"] < 20] if not stock.empty else pd.DataFrame()

    col1, col2, col3 = st.columns(3)

    col1.metric("💊 Medicines", total_medicines)
    col2.metric("⚠️ Low Stock", len(low_stock))
    col3.metric("💰 Sales", f"MK {total_sales}")

    st.subheader("🧠 Smart Alerts")

    if not low_stock.empty:
        st.warning("Low stock detected — reorder needed!")

# ==============================
# STOCK
# ==============================
elif menu == "Stock":

    st.header("📦 Stock Management")

    with st.form("stock_form"):
        med = st.text_input("Medicine")
        batch = st.text_input("Batch")
        expiry = st.date_input("Expiry Date")
        qty = st.number_input("Quantity", min_value=1)

        submit = st.form_submit_button("Add Stock")

        if submit and med:

            cursor.execute("""
            INSERT INTO stock (medicine, batch, expiry, balance)
            VALUES (?, ?, ?, ?)
            """, (med, batch, str(expiry), qty))

            conn.commit()
            st.success("Stock added!")

    stock = pd.read_sql("SELECT * FROM stock", conn)
    st.dataframe(stock)

# ==============================
# SALES
# ==============================
elif menu == "Sales":

    st.header("🧾 Sales System")

    stock = pd.read_sql("SELECT * FROM stock", conn)

    with st.form("sales_form"):
        med = st.text_input("Medicine")
        qty = st.number_input("Quantity", min_value=1)
        price = st.number_input("Price", min_value=0.0)

        total = qty * price

        submit = st.form_submit_button("Record Sale")

        if submit and med:

            cursor.execute("""
            INSERT INTO sales (email, medicine, qty, price, total, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                st.session_state.user,
                med,
                qty,
                price,
                total,
                str(date.today())
            ))

            conn.commit()
            st.success("Sale recorded!")

    sales = pd.read_sql("SELECT * FROM sales", conn)
    st.dataframe(sales)

# ==============================
# EXPIRY ALERTS
# ==============================
elif menu == "Expiry Alerts":

    st.header("⚠️ Expiry Monitoring")

    stock = pd.read_sql("SELECT * FROM stock", conn)

    if stock.empty:
        st.info("No stock available")
    else:

        stock["expiry"] = pd.to_datetime(stock["expiry"])
        today = pd.to_datetime(date.today())

        expired = stock[stock["expiry"] < today]
        expiring = stock[
            (stock["expiry"] >= today) &
            (stock["expiry"] <= today + pd.Timedelta(days=30))
        ]

        st.subheader("❌ Expired")
        st.dataframe(expired)

        st.subheader("⏳ Expiring Soon")
        st.dataframe(expiring)
