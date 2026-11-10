import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    initialize_database,
    get_connection,
    get_medicines,
    add_medicine
)

# ---------- PAGE SETTINGS ----------

st.set_page_config(
    page_title="MediCare Plus",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- PREMIUM STYLING ----------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg,#0b1020,#171b38,#211b45);
    color: #ffffff;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#17132f,#10172c);
    border-right: 1px solid #34305b;
}

[data-testid="stSidebar"] * {
    color: #f1f0ff !important;
}

h1,h2,h3 {
    color: #ffffff !important;
    font-weight: 700 !important;
}

p,label {
    color: #c4c6df;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg,#282653,#302e61);
    border: 1px solid #514a88;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 25px #00000035;
}

div[data-testid="stMetricLabel"] {
    color: #c4c6df !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

.stButton>button {
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton>button:hover {
    background: linear-gradient(90deg,#9333ea,#6366f1);
    color: white;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: #222541;
    color: white;
    border: 1px solid #55527c;
    border-radius: 9px;
}

div[data-testid="stSelectbox"] div {
    border-radius: 9px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #414168;
    border-radius: 12px;
}

hr {
    border-color: #414168;
}

.hero {
    background: linear-gradient(110deg,#5225a8,#3734a5,#176c91);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 12px 35px #00000045;
}

.hero h1 {
    color: white !important;
    font-size: 32px;
}

.hero p {
    color: #e4e7ff;
    margin-bottom: 0;
}

.section-card {
    background: #202442;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #414168;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)


# ---------- DATABASE INITIALIZATION ----------

initialize_database()


# ---------- SIDEBAR ----------

st.sidebar.markdown("""
<div style="text-align:center;padding:20px 5px;">
    <div style="font-size:48px;">💊</div>
    <h2 style="margin:5px 0;">MediCare Plus</h2>
    <p style="color:#aaaaff;font-size:12px;">
        SMART PHARMACY SYSTEM
    </p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "🏠 Dashboard",
        "💊 Medicine Inventory",
        "➕ Add Medicine",
        "🧾 Billing",
        "⚠️ Expiry Alerts",
        "📊 Sales Reports"
    ]
)

st.sidebar.divider()
st.sidebar.caption("✨ Pharmacy Management")
st.sidebar.caption("Version 1.0 | Academic Project")


# ---------- COMMON DATA ----------

medicines = get_medicines()

conn = get_connection()
sales = pd.read_sql_query("SELECT * FROM sales", conn)
conn.close()


# ---------- HEADER ----------

st.markdown("""
<div class="hero">
    <h1>Welcome to MediCare Plus 👋</h1>
    <p>Your intelligent pharmacy management workspace</p>
</div>
""", unsafe_allow_html=True)


# ---------- DASHBOARD ----------

if page == "🏠 Dashboard":

    st.subheader("📈 Business Overview")

    total_products = len(medicines)
    total_stock = sum(m[4] for m in medicines)
    revenue = sales["total"].sum() if not sales.empty else 0
    transactions = len(sales)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💊 Products", total_products)
    c2.metric("📦 Stock Units", total_stock)
    c3.metric("💰 Revenue", f"₹{revenue:,.2f}")
    c4.metric("🧾 Transactions", transactions)

    st.divider()

    left, right = st.columns([1.4, 1])

    with left:
        st.subheader("📊 Sales Performance")

        if not sales.empty:

            chart_data = sales.copy()
            chart_data["sale_date"] = pd.to_datetime(
                chart_data["sale_date"]
            )

            daily = chart_data.groupby(
                "sale_date"
            )["total"].sum().reset_index()

            fig = px.area(
                daily,
                x="sale_date",
                y="total",
                template="plotly_dark",
                color_discrete_sequence=["#a78bfa"],
                title="Revenue Trend"
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Sales chart will appear after your first bill.")

    with right:
        st.subheader("🚨 Stock Alerts")

        low_stock = [m for m in medicines if m[4] <= 10]

        if low_stock:
            for m in low_stock:
                st.warning(f"{m[1]} — Only {m[4]} left")
        else:
            st.success("No low-stock medicines.")

        st.subheader("⚡ Quick Actions")
        st.write("Use the sidebar to add medicines or generate bills.")

    st.divider()

    st.subheader("🕒 Recently Added Medicines")

    if medicines:
        df = pd.DataFrame(medicines, columns=[
            "ID", "Medicine", "Category", "Price",
            "Stock", "Expiry", "Supplier"
        ])

        st.dataframe(df.tail(5), use_container_width=True)

    else:
        st.info("Start by adding your first medicine.")


# ---------- MEDICINE INVENTORY AND REMOVAL ----------

elif page == "💊 Medicine Inventory":

    st.subheader("💊 Medicine Inventory")

    search = st.text_input("🔍 Search medicine by name")

    if medicines:

        df = pd.DataFrame(medicines, columns=[
            "ID", "Medicine", "Category", "Price",
            "Stock", "Expiry", "Supplier"
        ])

        if search:
            df = df[df["Medicine"].str.contains(
                search, case=False, na=False
            )]

        st.dataframe(df, use_container_width=True)

        st.caption(f"Showing {len(df)} medicine records.")

        st.divider()

        st.subheader("🗑️ Remove Incorrect Medicine")

        selected_medicine = st.selectbox(
            "Select medicine to remove",
            options=medicines,
            format_func=lambda m: f"{m[1]} (ID: {m[0]})",
            key="delete_medicine_select"
        )

        confirm_delete = st.checkbox(
            f"I confirm that I want to remove {selected_medicine[1]}",
            key="confirm_medicine_delete"
        )

        if st.button("🗑️ Remove Medicine"):

            if not confirm_delete:

                st.warning("Please confirm before removing.")

            else:

                conn = get_connection()
                cursor = conn.cursor()

                try:

                    cursor.execute(
                        "SELECT COUNT(*) FROM sales WHERE medicine_id = ?",
                        (selected_medicine[0],)
                    )

                    sold_count = cursor.fetchone()[0]

                    if sold_count > 0:

                        st.warning(
                            "This medicine has previous sales records. "
                            "It cannot be removed because sales history "
                            "must be preserved."
                        )

                    else:

                        cursor.execute(
                            "DELETE FROM medicines WHERE id = ?",
                            (selected_medicine[0],)
                        )

                        conn.commit()

                        if cursor.rowcount > 0:
                            st.success(
                                f"{selected_medicine[1]} removed successfully!"
                            )
                        else:
                            st.warning("Medicine was not found.")

                        st.rerun()

                except Exception as e:

                    conn.rollback()
                    st.error(f"Unable to remove medicine: {e}")

                finally:
                    conn.close()

    else:
        st.info("No medicines available.")


# ---------- ADD MEDICINE ----------

elif page == "➕ Add Medicine":

    st.subheader("➕ Add New Medicine")
    st.write("Enter medicine details to update your inventory.")

    with st.form("add_medicine_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input("Medicine Name")

            category = st.selectbox(
                "Category",
                ["Tablet", "Syrup", "Capsule", "Injection", "Other"]
            )

            price = st.number_input(
                "Price (₹)",
                min_value=0.01,
                value=10.0
            )

        with col2:

            quantity = st.number_input(
                "Available Quantity",
                min_value=0,
                step=1
            )

            expiry = st.date_input("Expiry Date")
            supplier = st.text_input("Supplier Name")

        submitted = st.form_submit_button(
            "➕ Save Medicine",
            use_container_width=True
        )

        if submitted:

            if name.strip() and supplier.strip():

                add_medicine(
                    name,
                    category,
                    price,
                    quantity,
                    str(expiry),
                    supplier
                )

                st.success(f"🎉 {name} added successfully!")
                st.rerun()

            else:
                st.error("Please enter medicine and supplier details.")


# ---------- BILLING ----------

elif page == "🧾 Billing":

    st.subheader("🧾 Customer Billing")
    st.write("Create a new pharmacy invoice.")

    available = [m for m in medicines if m[4] > 0]

    if available:

        customer = st.text_input("Customer Name")

        selected = st.selectbox(
            "Select Medicine",
            available,
            format_func=lambda m:
                f"{m[1]} | ₹{m[3]:.2f} | Stock: {m[4]}"
        )

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=selected[4],
            step=1
        )

        gst_rate = st.selectbox("GST Rate (%)", [0, 5, 12, 18, 28])

        subtotal = selected[3] * qty
        gst_amount = subtotal * gst_rate / 100
        total = subtotal + gst_amount

        st.markdown(
            f'<div class="section-card">'
            f'<h3>Invoice Preview</h3>'
            f'<p>Subtotal: ₹{subtotal:.2f}</p>'
            f'<p>GST: ₹{gst_amount:.2f}</p>'
            f'<h2>Total: ₹{total:.2f}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )

        if st.button("🧾 Generate Invoice"):

            if not customer.strip():

                st.error("Enter customer name.")

            else:

                conn = get_connection()
                cursor = conn.cursor()

                try:

                    cursor.execute(
                        """
                        UPDATE medicines
                        SET quantity = quantity - ?
                        WHERE id = ? AND quantity >= ?
                        """,
                        (qty, selected[0], qty)
                    )

                    if cursor.rowcount == 1:

                        cursor.execute(
                            """
                            INSERT INTO sales
                            (customer_name, medicine_id, medicine_name,
                             quantity, unit_price, gst, total, sale_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                customer,
                                selected[0],
                                selected[1],
                                qty,
                                selected[3],
                                gst_amount,
                                total,
                                str(date.today())
                            )
                        )

                        conn.commit()

                        st.success("Invoice generated successfully!")
                        st.write(f"Customer: {customer}")
                        st.write(f"Medicine: {selected[1]}")
                        st.write(f"Quantity: {qty}")
                        st.write(f"Total: ₹{total:.2f}")

                        st.rerun()

                    else:

                        conn.rollback()
                        st.error("Insufficient stock.")

                except Exception as e:

                    conn.rollback()
                    st.error(f"Unable to generate invoice: {e}")

                finally:
                    conn.close()

    else:
        st.warning("Please add medicines before billing.")


# ---------- EXPIRY ALERTS ----------

elif page == "⚠️ Expiry Alerts":

    st.subheader("⚠️ Medicine Expiry Management")

    if medicines:

        df = pd.DataFrame(medicines, columns=[
            "ID", "Medicine", "Category", "Price",
            "Stock", "Expiry", "Supplier"
        ])

        df["Expiry"] = pd.to_datetime(
            df["Expiry"],
            errors="coerce"
        )

        today = pd.Timestamp(date.today())

        expired = df[df["Expiry"] < today]

        upcoming = df[
            (df["Expiry"] >= today) &
            (df["Expiry"] <= today + pd.Timedelta(days=90))
        ]

        a, b = st.columns(2)

        a.metric("Expired Medicines", len(expired))
        b.metric("Expiring Soon", len(upcoming))

        st.subheader("🚨 Expired")
        st.dataframe(expired, use_container_width=True)

        st.subheader("⏳ Expiring Within 90 Days")
        st.dataframe(upcoming, use_container_width=True)

    else:
        st.info("No medicine records found.")


# ---------- SALES REPORTS ----------

elif page == "📊 Sales Reports":

    st.subheader("📊 Sales Analytics")

    if not sales.empty:

        sales["sale_date"] = pd.to_datetime(
            sales["sale_date"]
        )

        a, b, c = st.columns(3)

        a.metric(
            "Total Revenue",
            f"₹{sales['total'].sum():,.2f}"
        )

        b.metric("Transactions", len(sales))

        c.metric(
            "Items Sold",
            int(sales["quantity"].sum())
        )

        daily = sales.groupby(
            "sale_date"
        )["total"].sum().reset_index()

        fig = px.bar(
            daily,
            x="sale_date",
            y="total",
            template="plotly_dark",
            color="total",
            title="Daily Revenue",
            color_continuous_scale="Purples"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sales History")
        st.dataframe(sales, use_container_width=True)

        st.download_button(
            "⬇️ Download Sales CSV",
            sales.to_csv(index=False),
            "pharmacy_sales.csv",
            "text/csv"
        )

    else:
        st.info("Sales reports will appear after generating invoices.")


# ---------- FOOTER ----------

st.divider()
st.caption("💜 MediCare Plus | Pharmacy Management System")