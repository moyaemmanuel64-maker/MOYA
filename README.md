
import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="PHARMOYA", layout="wide")

st.title("💊 PHARMOYA")

# ==============================
# SESSION STATE INITIALIZATION
# ==============================

if "stock_data" not in st.session_state:
    st.session_state.stock_data = pd.DataFrame(
        columns=[
            "Medicine",
            "Batch",
            "Expiry",
            "Received",
            "Issued",
            "Balance",
        ]
    )

if "expense_data" not in st.session_state:
    st.session_state.expense_data = pd.DataFrame(
        columns=[
            "Date",
            "Item",
            "Quantity",
            "Unit Price",
            "Total Cost",
        ]
    )

if "medicine_db" not in st.session_state:
    st.session_state.medicine_db = pd.DataFrame(
        columns=[
            "Generic Name",
            "Brand Name",
            "Strength",
            "Dosage Form",
            "Indications",
            "Contraindications",
            "Side Effects",
            "Mode of Action",
        ]
    )

if "sales_data" not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(
        columns=[
            "Date",
            "Medicine",
            "Quantity",
            "Price",
            "Total",
        ]
    )

# ==============================
# SIDEBAR NAVIGATION
# ==============================

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Expense Tracker",
        "Stock Card",
        "Medicine Database",
        "Expiry Alerts",
        "Sales & Dispensing",
        "Reports",
    ],
)

# ==============================
# DASHBOARD
# ==============================

if menu == "Dashboard":

    st.header("📊 Dashboard")

    total_medicines = len(st.session_state.stock_data)

    low_stock = st.session_state.stock_data[
        st.session_state.stock_data["Balance"] < 50
    ]

    today = pd.to_datetime(date.today())

    if not st.session_state.stock_data.empty:
        expiry_dates = pd.to_datetime(
            st.session_state.stock_data["Expiry"],
            errors="coerce"
        )

        expired = st.session_state.stock_data[
            expiry_dates < today
        ]
    else:
        expired = pd.DataFrame()

    daily_expenses = (
        st.session_state.expense_data["Total Cost"].sum()
        if not st.session_state.expense_data.empty
        else 0
    )

    monthly_sales = (
        st.session_state.sales_data["Total"].sum()
        if not st.session_state.sales_data.empty
        else 0
    )

    monthly_profit = monthly_sales - daily_expenses

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Medicines", total_medicines)
    col2.metric("Low Stock", len(low_stock))
    col3.metric("Expired Medicines", len(expired))
    col4.metric("Monthly Profit", f"MK {monthly_profit}")

# ==============================
# EXPENSE TRACKER
# ==============================

elif menu == "Expense Tracker":

    st.header("💰 Expense Tracker")

    item = st.text_input("Item Name")
    qty = st.number_input("Quantity", min_value=1)
    unit_price = st.number_input("Unit Price", min_value=0.0)

    total_cost = qty * unit_price

    expense_date = st.date_input("Date", datetime.today())

    st.write(f"### Total Cost: MK {total_cost}")

    if st.button("Add Expense"):

        new_expense = {
            "Date": expense_date,
            "Item": item,
            "Quantity": qty,
            "Unit Price": unit_price,
            "Total Cost": total_cost,
        }

        st.session_state.expense_data = pd.concat(
            [
                st.session_state.expense_data,
                pd.DataFrame([new_expense]),
            ],
            ignore_index=True,
        )

        st.success("Expense added successfully!")

    st.subheader("Expense Records")
    st.dataframe(st.session_state.expense_data)

# ==============================
# STOCK CARD
# ==============================

elif menu == "Stock Card":

    st.header("📦 Stock Card")

    medicine = st.text_input("Medicine Name")
    batch = st.text_input("Batch Number")
    expiry = st.date_input("Expiry Date")

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Received", "Issued","Losses"]
    )

    quantity = st.number_input("Quantity", min_value=1)

    current_balance = 0

    if not st.session_state.stock_data.empty:
        medicine_rows = st.session_state.stock_data[
            st.session_state.stock_data["Medicine"] == medicine
        ]

        if not medicine_rows.empty:
            current_balance = medicine_rows.iloc[-1]["Balance"]

    if st.button("Add Stock Entry"):

        if transaction_type == "Received":
            received = quantity
            issued = 0
            balance = current_balance + quantity

        else:

            if quantity > current_balance:
                st.error("Not enough stock available!")
                st.stop()

            received = 0
            issued = quantity
            balance = current_balance - quantity

        new_stock = {
            "Medicine": medicine,
            "Batch": batch,
            "Expiry": expiry,
            "Received": received,
            "Issued": issued,
            "Balance": balance,
        }

        st.session_state.stock_data = pd.concat(
            [
                st.session_state.stock_data,
                pd.DataFrame([new_stock]),
            ],
            ignore_index=True,
        )

        st.success("Stock updated successfully!")

    st.subheader("Stock Records")
    st.dataframe(st.session_state.stock_data)

# ==============================
# MEDICINE DATABASE
# ==============================

elif menu == "Medicine Database":

    st.header("💊 Medicine Information Database")

    generic = st.text_input("Generic Name")
    brand = st.text_input("Brand Name")
    strength = st.text_input("Strength")
    dosage = st.text_input("Dosage Form")

    indications = st.text_area("Indications")
    contraindications = st.text_area("Contraindications")
    side_effects = st.text_area("Side Effects")
    mode_action = st.text_area("Mode of Action")

    if st.button("Save Medicine"):

        new_medicine = {
            "Generic Name": generic,
            "Brand Name": brand,
            "Strength": strength,
            "Dosage Form": dosage,
            "Indications": indications,
            "Contraindications": contraindications,
            "Side Effects": side_effects,
            "Mode of Action": mode_action,
        }

        st.session_state.medicine_db = pd.concat(
            [
                st.session_state.medicine_db,
                pd.DataFrame([new_medicine]),
            ],
            ignore_index=True,
        )

        st.success("Medicine saved!")

    st.subheader("Medicine Database")
    st.dataframe(st.session_state.medicine_db)

# ==============================
# EXPIRY ALERTS
# ==============================

elif menu == "Expiry Alerts":

    st.header("⚠️ Expiry Alert System")

    if st.session_state.stock_data.empty:
        st.info("No stock records available.")

    else:

        stock = st.session_state.stock_data.copy()

        stock["Expiry"] = pd.to_datetime(stock["Expiry"])

        today = pd.to_datetime(date.today())

        expired = stock[stock["Expiry"] < today]

        expiring_soon = stock[
            (stock["Expiry"] >= today)
            & (stock["Expiry"] <= today + pd.Timedelta(days=30))
        ]

        st.subheader("❌ Expired Medicines")

        if expired.empty:
            st.success("No expired medicines.")
        else:
            st.dataframe(expired)

        st.subheader("⏳ Expiring Soon (30 Days)")

        if expiring_soon.empty:
            st.success("No medicines expiring soon.")
        else:
            st.dataframe(expiring_soon)

# ==============================
# SALES & DISPENSING
# ==============================

elif menu == "Sales & Dispensing":

    st.header("🧾 Sales and Dispensing Records")

    med_name = st.text_input("Medicine")
    sale_qty = st.number_input("Quantity Sold", min_value=1)
    price = st.number_input("Selling Price", min_value=0.0)

    total_sale = sale_qty * price

    sale_date = st.date_input("Sale Date", datetime.today())

    st.write(f"### Total Sale: MK {total_sale}")

    if st.button("Record Sale"):

        sale = {
            "Date": sale_date,
            "Medicine": med_name,
            "Quantity": sale_qty,
            "Price": price,
            "Total": total_sale,
        }

        st.session_state.sales_data = pd.concat(
            [
                st.session_state.sales_data,
                pd.DataFrame([sale]),
            ],
            ignore_index=True,
        )

        st.success("Sale recorded!")

    st.subheader("Sales Records")
    st.dataframe(st.session_state.sales_data)

# ==============================
# REPORTS
# ==============================

elif menu == "Reports":

    st.header("📈 Reports & Calculations")

    total_sales = (
        st.session_state.sales_data["Total"].sum()
        if not st.session_state.sales_data.empty
        else 0
    )

    total_expenses = (
        st.session_state.expense_data["Total Cost"].sum()
        if not st.session_state.expense_data.empty
        else 0
    )

    profit = total_sales - total_expenses

    st.subheader("Financial Summary")

    st.write(f"### Total Sales: MK {total_sales}")
    st.write(f"### Total Expenses: MK {total_expenses}")
    st.write(f"### Profit: MK {profit}")

    st.subheader("Download Reports")

    stock_csv = st.session_state.stock_data.to_csv(index=False).encode("utf-8")
    expense_csv = st.session_state.expense_data.to_csv(index=False).encode("utf-8")
    sales_csv = st.session_state.sales_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Stock Report",
        stock_csv,
        "stock_report.csv",
        "text/csv",
    )

    st.download_button(
        "Download Expense Report",
        expense_csv,
        "expense_report.csv",
        "text/csv",
    )

    st.download_button(
        "Download Sales Report",
        sales_csv,
        "sales_report.csv",
        "text/csv",
    )
    ## Deploy online
    Use streamlit Cloud:
    https://share.streamlit.io
