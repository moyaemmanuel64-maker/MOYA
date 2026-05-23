import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="PHARMOYA", layout="wide")

st.title("💊 PHARMOYA - Pharmacy Management System")

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
            "Losses",
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

    st.header("Dashboard")

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

    with st.form("expense_form"):
        item = st.text_input("Item Name", placeholder="Enter item name")
        qty = st.number_input("Quantity", min_value=1)
        unit_price = st.number_input("Unit Price", min_value=0.0)
        expense_date = st.date_input("Date", datetime.today())
        
        total_cost = qty * unit_price
        st.write(f"### Total Cost: MK {total_cost:.2f}")
        
        submit_button = st.form_submit_button("Add Expense")

        if submit_button:
            if not item.strip():
                st.error("Please enter an item name!")
            else:
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
    if not st.session_state.expense_data.empty:
        st.dataframe(st.session_state.expense_data, use_container_width=True)
    else:
        st.info("No expense records yet.")

# ==============================
# STOCK CARD
# ==============================

elif menu == "Stock Card":

    st.header("📦Stock Card")

    with st.form("stock_form"):
        medicine = st.text_input("Medicine Name", placeholder="Enter medicine name")
        batch = st.text_input("Batch Number", placeholder="Enter batch number")
        expiry = st.date_input("Expiry Date")

        transaction_type = st.selectbox(
            "Transaction Type",
            ["Received", "Issued"]
        )

        quantity = st.number_input("Quantity", min_value=1)

        submit_button = st.form_submit_button("Add Stock Entry")

        if submit_button:
            if not medicine.strip() or not batch.strip():
                st.error("Please fill in all required fields!")
            else:
                current_balance = 0

                if not st.session_state.stock_data.empty:
                    medicine_rows = st.session_state.stock_data[
                        st.session_state.stock_data["Medicine"] == medicine
                    ]

                    if not medicine_rows.empty:
                        current_balance = medicine_rows.iloc[-1]["Balance"]

                if transaction_type == "Received":
                    received = quantity
                    issued = 0
                    balance = current_balance + quantity

                else:
                    if quantity > current_balance:
                        st.error("Not enough stock available!")
                    else:
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

                if transaction_type == "Received":
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
    if not st.session_state.stock_data.empty:
        st.dataframe(st.session_state.stock_data, use_container_width=True)
    else:
        st.info("No stock records yet.")

# ==============================
# MEDICINE DATABASE
# ==============================

elif menu == "Medicine Database":

    st.header("💊 Medicine Information")

    with st.form("medicine_form"):
        generic = st.text_input("Generic Name", placeholder="Enter generic name")
        brand = st.text_input("Brand Name", placeholder="Enter brand name")
        strength = st.text_input("Strength", placeholder="e.g., 500mg")
        dosage = st.text_input("Dosage Form", placeholder="e.g., Tablet, Syrup")

        indications = st.text_area("Indications", placeholder="Medical uses...")
        contraindications = st.text_area("Contraindications", placeholder="Conditions to avoid...")
        side_effects = st.text_area("Side Effects", placeholder="Possible side effects...")
        mode_action = st.text_area("Mode of Action", placeholder="How it works...")

        submit_button = st.form_submit_button("Save Medicine")

        if submit_button:
            if not generic.strip() or not brand.strip():
                st.error("Please enter Generic and Brand names!")
            else:
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
    if not st.session_state.medicine_db.empty:
        st.dataframe(st.session_state.medicine_db, use_container_width=True)
    else:
        st.info("No medicines in database yet.")

# ==============================
# EXPIRY ALERTS
# ==============================

elif menu == "Expiry Alerts":

    st.header("⚠️ Expiry Alert System")

    if st.session_state.stock_data.empty:
        st.info("No stock records available.")

    else:

        stock = st.session_state.stock_data.copy()

        stock["Expiry"] = pd.to_datetime(stock["Expiry"], errors="coerce")

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
            st.dataframe(expired, use_container_width=True)

        st.subheader("⏳ Expiring Soon (30 Days)")

        if expiring_soon.empty:
            st.success("No medicines expiring soon.")
        else:
            st.dataframe(expiring_soon, use_container_width=True)

# ==============================
# SALES & DISPENSING
# ==============================

elif menu == "Sales & Dispensing":

    st.header("🧾 Sales and Dispensing Records")

    with st.form("sales_form"):
        med_name = st.text_input("Medicine", placeholder="Enter medicine name")
        sale_qty = st.number_input("Quantity Sold", min_value=1)
        price = st.number_input("Selling Price", min_value=0.0)
        sale_date = st.date_input("Sale Date", datetime.today())

        total_sale = sale_qty * price
        st.write(f"### Total Sale: MK {total_sale:.2f}")

        submit_button = st.form_submit_button("Record Sale")

        if submit_button:
            if not med_name.strip():
                st.error("Please enter medicine name!")
            else:
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
    if not st.session_state.sales_data.empty:
        st.dataframe(st.session_state.sales_data, use_container_width=True)
    else:
        st.info("No sales records yet.")

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

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"MK {total_sales:.2f}")
    col2.metric("Total Expenses", f"MK {total_expenses:.2f}")
    col3.metric("Profit", f"MK {profit:.2f}")

    st.subheader("Download Reports")

    stock_csv = st.session_state.stock_data.to_csv(index=False).encode("utf-8")
    expense_csv = st.session_state.expense_data.to_csv(index=False).encode("utf-8")
    sales_csv = st.session_state.sales_data.to_csv(index=False).encode("utf-8")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 Download Stock Report",
            stock_csv,
            "stock_report.csv",
            "text/csv",
        )

    with col2:
        st.download_button(
            "📥 Download Expense Report",
            expense_csv,
            "expense_report.csv",
            "text/csv",
        )

    with col3:
        st.download_button(
            "📥 Download Sales Report",
            sales_csv,
            "sales_report.csv",
            "text/csv",
        )
