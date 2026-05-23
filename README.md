
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PHARMOYA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect("pharmoya.db", check_same_thread=False)
cursor = conn.cursor()

# =========================================================
# CREATE TABLES
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generic_name TEXT,
    brand_name TEXT,
    strength TEXT,
    dosage_form TEXT,
    indications TEXT,
    contraindications TEXT,
    side_effects TEXT,
    mode_of_action TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine TEXT,
    batch TEXT,
    expiry TEXT,
    transaction_type TEXT,
    quantity INTEGER,
    balance INTEGER,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_cost REAL,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine TEXT,
    quantity INTEGER,
    price REAL,
    total REAL,
    patient TEXT,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    phone TEXT,
    diagnosis TEXT,
    allergies TEXT,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT,
    contact TEXT,
    address TEXT,
    products TEXT
)
""")

conn.commit()

# =========================================================
# DEFAULT ADMIN
# =========================================================

cursor.execute("SELECT * FROM users WHERE username='admin'")
admin_exists = cursor.fetchone()

if not admin_exists:
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?)",
        ("admin", "admin123", "Admin")
    )
    conn.commit()

# =========================================================
# LOGIN SYSTEM
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 PHARMOYA LOGIN")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.role = user[2]
            st.success("Login successful!")
            st.rerun()

        else:
            st.error("Invalid username or password")

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("💊 PHARMOYA")

st.sidebar.success(f"Logged in as: {st.session_state.username}")

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Medicine Database",
        "Stock Management",
        "Sales & Dispensing",
        "Expense Tracker",
        "Patients",
        "Suppliers",
        "Expiry Alerts",
        "Reports",
        "Backup",
        "Logout"
    ]
)

# =========================================================
# DASHBOARD
# =========================================================

if menu == "Dashboard":

    st.title("📊 Dashboard")

    medicines = pd.read_sql("SELECT * FROM medicines", conn)
    stock = pd.read_sql("SELECT * FROM stock", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)
    expenses = pd.read_sql("SELECT * FROM expenses", conn)

    total_medicines = len(medicines)

    low_stock = stock[stock["balance"] < 50] if not stock.empty else pd.DataFrame()

    today = pd.to_datetime(date.today())

    if not stock.empty:
        stock["expiry"] = pd.to_datetime(stock["expiry"])
        expired = stock[stock["expiry"] < today]
    else:
        expired = pd.DataFrame()

    total_sales = sales["total"].sum() if not sales.empty else 0
    total_expenses = expenses["total_cost"].sum() if not expenses.empty else 0
    profit = total_sales - total_expenses

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Medicines", total_medicines)
    col2.metric("Low Stock", len(low_stock))
    col3.metric("Expired Medicines", len(expired))
    col4.metric("Profit", f"MK {profit}")

    st.divider()

    if not sales.empty:

        sales_chart = sales.groupby("medicine")["total"].sum().reset_index()

        fig = px.bar(
            sales_chart,
            x="medicine",
            y="total",
            title="Sales by Medicine"
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# MEDICINE DATABASE
# =========================================================

elif menu == "Medicine Database":

    st.title("💊 Medicine Database")

    with st.form("medicine_form"):

        generic = st.text_input("Generic Name")
        brand = st.text_input("Brand Name")
        strength = st.text_input("Strength")
        dosage = st.text_input("Dosage Form")

        indications = st.text_area("Indications")
        contraindications = st.text_area("Contraindications")
        side_effects = st.text_area("Side Effects")
        mode = st.text_area("Mode of Action")

        submitted = st.form_submit_button("Save Medicine")

        if submitted:

            cursor.execute("""
            INSERT INTO medicines (
                generic_name,
                brand_name,
                strength,
                dosage_form,
                indications,
                contraindications,
                side_effects,
                mode_of_action
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                generic,
                brand,
                strength,
                dosage,
                indications,
                contraindications,
                side_effects,
                mode
            ))

            conn.commit()

            st.success("Medicine saved successfully!")

    data = pd.read_sql("SELECT * FROM medicines", conn)
    st.dataframe(data, use_container_width=True)

# =========================================================
# STOCK MANAGEMENT
# =========================================================

elif menu == "Stock Management":

    st.title("📦 Stock Management")

    medicine = st.text_input("Medicine Name")
    batch = st.text_input("Batch Number")
    expiry = st.date_input("Expiry Date")

    transaction = st.selectbox(
        "Transaction Type",
        ["Received", "Issued", "Loss"]
    )

    quantity = st.number_input("Quantity", min_value=1)

    if st.button("Add Stock"):

        cursor.execute("""
        SELECT balance FROM stock
        WHERE medicine=?
        ORDER BY id DESC LIMIT 1
        """, (medicine,))

        last = cursor.fetchone()

        current_balance = last[0] if last else 0

        if transaction == "Received":
            balance = current_balance + quantity

        else:

            if quantity > current_balance:
                st.error("Not enough stock")
                st.stop()

            balance = current_balance - quantity

        cursor.execute("""
        INSERT INTO stock (
            medicine,
            batch,
            expiry,
            transaction_type,
            quantity,
            balance,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            medicine,
            batch,
            str(expiry),
            transaction,
            quantity,
            balance,
            str(date.today())
        ))

        conn.commit()

        st.success("Stock updated!")

    stock = pd.read_sql("SELECT * FROM stock", conn)

    search = st.text_input("Search Medicine")

    if search:
        stock = stock[
            stock["medicine"].str.contains(search, case=False)
        ]

    st.dataframe(stock, use_container_width=True)

# =========================================================
# SALES
# =========================================================

elif menu == "Sales & Dispensing":

    st.title("🧾 Sales & Dispensing")

    medicine = st.text_input("Medicine")
    patient = st.text_input("Patient Name")

    quantity = st.number_input("Quantity Sold", min_value=1)

    price = st.number_input("Selling Price", min_value=0.0)

    total = quantity * price

    st.write(f"### Total = MK {total}")

    if st.button("Record Sale"):

        cursor.execute("""
        SELECT balance FROM stock
        WHERE medicine=?
        ORDER BY id DESC LIMIT 1
        """, (medicine,))

        result = cursor.fetchone()

        balance = result[0] if result else 0

        if quantity > balance:
            st.error("Insufficient stock")
            st.stop()

        new_balance = balance - quantity

        cursor.execute("""
        INSERT INTO stock (
            medicine,
            batch,
            expiry,
            transaction_type,
            quantity,
            balance,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            medicine,
            "",
            "",
            "Issued",
            quantity,
            new_balance,
            str(date.today())
        ))

        cursor.execute("""
        INSERT INTO sales (
            medicine,
            quantity,
            price,
            total,
            patient,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            medicine,
            quantity,
            price,
            total,
            patient,
            str(date.today())
        ))

        conn.commit()

        st.success("Sale recorded!")

    sales = pd.read_sql("SELECT * FROM sales", conn)
    st.dataframe(sales, use_container_width=True)

# =========================================================
# EXPENSE TRACKER
# =========================================================

elif menu == "Expense Tracker":

    st.title("💰 Expense Tracker")

    item = st.text_input("Item")

    qty = st.number_input("Quantity", min_value=1)

    unit_price = st.number_input("Unit Price", min_value=0.0)

    total_cost = qty * unit_price

    st.write(f"### Total Cost = MK {total_cost}")

    if st.button("Add Expense"):

        cursor.execute("""
        INSERT INTO expenses (
            item,
            quantity,
            unit_price,
            total_cost,
            date
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            item,
            qty,
            unit_price,
            total_cost,
            str(date.today())
        ))

        conn.commit()

        st.success("Expense added!")

    expenses = pd.read_sql("SELECT * FROM expenses", conn)

    st.dataframe(expenses, use_container_width=True)

# =========================================================
# PATIENTS
# =========================================================

elif menu == "Patients":

    st.title("🧑‍⚕️ Patient Management")

    patient_name = st.text_input("Patient Name")

    phone = st.text_input("Phone Number")

    diagnosis = st.text_area("Diagnosis")

    allergies = st.text_area("Allergies")

    if st.button("Save Patient"):

        cursor.execute("""
        INSERT INTO patients (
            patient_name,
            phone,
            diagnosis,
            allergies,
            date
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            patient_name,
            phone,
            diagnosis,
            allergies,
            str(date.today())
        ))

        conn.commit()

        st.success("Patient saved!")

    patients = pd.read_sql("SELECT * FROM patients", conn)

    st.dataframe(patients, use_container_width=True)

# =========================================================
# SUPPLIERS
# =========================================================

elif menu == "Suppliers":

    st.title("🚚 Supplier Management")

    supplier = st.text_input("Supplier Name")

    contact = st.text_input("Contact")

    address = st.text_area("Address")

    products = st.text_area("Products Supplied")

    if st.button("Save Supplier"):

        cursor.execute("""
        INSERT INTO suppliers (
            supplier_name,
            contact,
            address,
            products
        )
        VALUES (?, ?, ?, ?)
        """, (
            supplier,
            contact,
            address,
            products
        ))

        conn.commit()

        st.success("Supplier saved!")

    suppliers = pd.read_sql("SELECT * FROM suppliers", conn)

    st.dataframe(suppliers, use_container_width=True)

# =========================================================
# EXPIRY ALERTS
# =========================================================

elif menu == "Expiry Alerts":

    st.title("⚠️ Expiry Alerts")

    stock = pd.read_sql("SELECT * FROM stock", conn)

    if stock.empty:
        st.info("No stock records")
    else:

        stock["expiry"] = pd.to_datetime(
            stock["expiry"],
            errors="coerce"
        )

        today = pd.to_datetime(date.today())

        expired = stock[stock["expiry"] < today]

        expiring_soon = stock[
            (stock["expiry"] >= today)
            &
            (stock["expiry"] <= today + pd.Timedelta(days=30))
        ]

        st.subheader("❌ Expired Medicines")

        st.dataframe(expired, use_container_width=True)

        st.subheader("⏳ Expiring Soon")

        st.dataframe(expiring_soon, use_container_width=True)

# =========================================================
# REPORTS
# =========================================================

elif menu == "Reports":

    st.title("📈 Reports")

    sales = pd.read_sql("SELECT * FROM sales", conn)
    expenses = pd.read_sql("SELECT * FROM expenses", conn)
    stock = pd.read_sql("SELECT * FROM stock", conn)

    total_sales = sales["total"].sum() if not sales.empty else 0

    total_expenses = (
        expenses["total_cost"].sum()
        if not expenses.empty
        else 0
    )

    profit = total_sales - total_expenses

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Sales", f"MK {total_sales}")
    col2.metric("Expenses", f"MK {total_expenses}")
    col3.metric("Profit", f"MK {profit}")

    st.divider()

    st.subheader("Download Reports")

    sales_csv = sales.to_csv(index=False).encode("utf-8")
    expense_csv = expenses.to_csv(index=False).encode("utf-8")
    stock_csv = stock.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Sales Report",
        sales_csv,
        "sales_report.csv",
        "text/csv"
    )

    st.download_button(
        "Download Expense Report",
        expense_csv,
        "expense_report.csv",
        "text/csv"
    )

    st.download_button(
        "Download Stock Report",
        stock_csv,
        "stock_report.csv",
        "text/csv"
    )

# =========================================================
# BACKUP
# =========================================================

elif menu == "Backup":

    st.title("💾 Backup Database")

    with open("pharmoya.db", "rb") as file:

        st.download_button(
            "Download Database Backup",
            file,
            "pharmoya_backup.db"
        )

# =========================================================
# LOGOUT
# =========================================================

elif menu == "Logout":

    st.session_state.logged_in = False

    st.success("Logged out successfully!")

    st.rerun()


