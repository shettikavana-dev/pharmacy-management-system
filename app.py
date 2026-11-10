import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from database import (
    initialize_database,
    get_connection,
    get_medicines,
    add_medicine
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MediCare Plus",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_database()


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #10182f;
    color: #ffffff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #142b50;
}

/* Headings and normal text */
h1, h2, h3, h4, p, label {
    color: #ffffff !important;
}

/* Text entry fields */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Dropdown fields */
[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
}

[data-baseweb="select"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Dropdown selected text */
[data-baseweb="select"] span {
    color: #000000 !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    color: #000000 !important;
}

/* Buttons */
.stButton > button {
    background-color: #2474d2;
    color: #ffffff !important;
    border-radius: 8px;
}

.stButton > button:hover {
    background-color: #1459aa;
    color: #ffffff !important;
}

/* Metric cards */
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

[data-testid="stMetricLabel"] {
    color: #ffffff !important;
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div {
    color: #172033 !important;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def load_sales():

    conn = get_connection()

    try:
        df = pd.read_sql_query(
            "SELECT * FROM sales ORDER BY sale_date DESC",
            conn
        )
        return df

    finally:
        conn.close()


def load_medicine_dataframe():

    medicines = get_medicines()

    return pd.DataFrame(
        medicines,
        columns=[
            "ID",
            "Medicine",
            "Category",
            "Price",
            "Quantity",
            "Expiry Date",
            "Supplier"
        ]
    )


# ==================================================
# PDF INVOICE
# ==================================================

def generate_invoice(invoice):

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    y = height - 70

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(50, y, "MediCare Plus")

    y -= 35

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "PHARMACY INVOICE")

    y -= 40

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        50, y,
        f"Invoice No: {invoice['invoice_no']}"
    )

    y -= 22

    pdf.drawString(
        50, y,
        f"Date: {invoice['date']}"
    )

    y -= 22

    pdf.drawString(
        50, y,
        f"Customer: {invoice['customer']}"
    )

    y -= 45

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(50, y, "Medicine")
    pdf.drawString(270, y, "Price")
    pdf.drawString(350, y, "Qty")
    pdf.drawString(420, y, "Amount")

    y -= 20

    pdf.setFont("Helvetica", 11)

    pdf.drawString(50, y, invoice["medicine"])

    pdf.drawString(
        270, y,
        f"Rs. {invoice['price']:.2f}"
    )

    pdf.drawString(
        350, y,
        str(invoice["quantity"])
    )

    pdf.drawString(
        420, y,
        f"Rs. {invoice['subtotal']:.2f}"
    )

    y -= 40

    pdf.drawString(
        300, y,
        f"Subtotal: Rs. {invoice['subtotal']:.2f}"
    )

    y -= 22

    pdf.drawString(
        300, y,
        f"GST ({invoice['gst_rate']:.2f}%): "
        f"Rs. {invoice['gst_amount']:.2f}"
    )

    y -= 25

    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawString(
        300, y,
        f"Grand Total: Rs. {invoice['grand_total']:.2f}"
    )

    y -= 55

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        50, y,
        "Thank you for choosing MediCare Plus!"
    )

    pdf.save()

    buffer.seek(0)

    return buffer


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("💊 MediCare Plus")

st.sidebar.write("Pharmacy Management System")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Medicine Inventory",
        "Add Medicine",
        "Billing",
        "Expiry Alerts",
        "Sales Reports"
    ]
)


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.title("💊 Pharmacy Dashboard")

    st.markdown("""
    <div class="welcome-banner">
        <h2>Welcome to MediCare Plus</h2>
        <p>Manage medicines, billing, inventory and sales easily.</p>
    </div>
    """, unsafe_allow_html=True)

    medicines_df = load_medicine_dataframe()
    sales_df = load_sales()

    total_medicines = len(medicines_df)

    total_stock = (
        int(medicines_df["Quantity"].sum())
        if not medicines_df.empty else 0
    )

    low_stock = (
        int((medicines_df["Quantity"] <= 10).sum())
        if not medicines_df.empty else 0
    )

    total_sales = (
        float(sales_df["total"].sum())
        if not sales_df.empty else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Medicines", total_medicines)
    col2.metric("Total Stock", total_stock)
    col3.metric("Low Stock Items", low_stock)
    col4.metric("Total Sales", f"₹{total_sales:,.2f}")

    st.divider()

    if not medicines_df.empty:

        st.subheader("Inventory Overview")

        st.dataframe(
            medicines_df,
            use_container_width=True,
            hide_index=True
        )

        fig = px.bar(
            medicines_df,
            x="Medicine",
            y="Quantity",
            color="Category",
            title="Medicine Stock Overview"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10182f",
            plot_bgcolor="#10182f",
            font_color="#ffffff"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No medicines have been added yet.")


# ==================================================
# MEDICINE INVENTORY
# ==================================================

elif page == "Medicine Inventory":

    st.title("📦 Medicine Inventory")

    medicines_df = load_medicine_dataframe()

    if medicines_df.empty:

        st.info("Inventory is currently empty.")

    else:

        search = st.text_input(
            "Search Medicine"
        )

        if search:

            medicines_df = medicines_df[
                medicines_df["Medicine"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            medicines_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Stock Status")

        low_stock_df = medicines_df[
            medicines_df["Quantity"] <= 10
        ]

        if not low_stock_df.empty:

            st.warning("Some medicines have low stock.")

            st.dataframe(
                low_stock_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success("All displayed medicines have sufficient stock.")


# ==================================================
# ADD MEDICINE
# ==================================================

elif page == "Add Medicine":

    st.title("➕ Add New Medicine")

    with st.form("add_medicine_form"):

        name = st.text_input(
            "Medicine Name"
        )

        category = st.selectbox(
            "Category",
            [
                "Tablet",
                "Capsule",
                "Syrup",
                "Injection",
                "Ointment",
                "Other"
            ]
        )

        price = st.number_input(
            "Price (₹)",
            min_value=0.01,
            value=1.0,
            step=1.0
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0,
            value=1,
            step=1
        )

        expiry = st.date_input(
            "Expiry Date",
            min_value=date.today()
        )

        supplier = st.text_input(
            "Supplier Name"
        )

        submitted = st.form_submit_button(
            "Add Medicine"
        )

        if submitted:

            if not name.strip():

                st.error("Please enter the medicine name.")

            elif not supplier.strip():

                st.error("Please enter the supplier name.")

            else:

                try:

                    add_medicine(
                        name.strip(),
                        category,
                        float(price),
                        int(quantity),
                        expiry.isoformat(),
                        supplier.strip()
                    )

                    st.success(
                        f"{name} added successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Unable to add medicine: {e}"
                    )


# ==================================================
# BILLING
# ==================================================

elif page == "Billing":

    st.title("🧾 Medicine Billing")

    medicines = get_medicines()

    if not medicines:

        st.warning(
            "No medicines available. Add medicines to inventory first."
        )

    else:

        medicine_options = {
            f"{m[1]} | ID: {m[0]} | ₹{float(m[3]):.2f}": m
            for m in medicines
        }

        selected_medicine = st.selectbox(
            "Select Medicine",
            list(medicine_options.keys())
        )

        medicine = medicine_options[selected_medicine]

        medicine_id = int(medicine[0])
        medicine_name = medicine[1]
        price = float(medicine[3])
        available_quantity = int(medicine[4])

        st.write(f"**Medicine:** {medicine_name}")

        st.write(f"**Price per unit:** ₹{price:.2f}")

        st.write(
            f"**Available Stock:** {available_quantity}"
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        if available_quantity > 0:

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=available_quantity,
                value=1,
                step=1
            )

        else:

            quantity = 0

            st.error(
                "This medicine is out of stock."
            )

        gst_rate = st.number_input(
            "GST Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5
        )

        # BILL CALCULATION

        subtotal = round(
            price * quantity,
            2
        )

        gst_amount = round(
            subtotal * gst_rate / 100,
            2
        )

        grand_total = round(
            subtotal + gst_amount,
            2
        )

        st.divider()

        st.subheader("Bill Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Medicine Amount",
            f"₹{subtotal:,.2f}"
        )

        col2.metric(
            f"GST ({gst_rate}%)",
            f"₹{gst_amount:,.2f}"
        )

        col3.metric(
            "Grand Total",
            f"₹{grand_total:,.2f}"
        )

        st.caption(
            "Select the applicable GST rate according to the medicine's "
            "HSN classification. The default rate is only an example."
        )

        if st.button(
            "Generate Bill",
            disabled=(available_quantity <= 0 or quantity <= 0)
        ):

            if not customer_name.strip():

                st.error(
                    "Please enter the customer name."
                )

            else:

                conn = get_connection()

                try:

                    cursor = conn.cursor()

                    # Check and update stock safely

                    cursor.execute(
                        """
                        UPDATE medicines
                        SET quantity = quantity - ?
                        WHERE id = ? AND quantity >= ?
                        """,
                        (
                            int(quantity),
                            medicine_id,
                            int(quantity)
                        )
                    )

                    if cursor.rowcount != 1:

                        conn.rollback()

                        st.error(
                            "Insufficient stock. Refresh and try again."
                        )

                    else:

                        sale_date = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        # Save GST amount in the existing gst column

                        cursor.execute(
                            """
                            INSERT INTO sales
                            (
                                customer_name,
                                medicine_id,
                                medicine_name,
                                quantity,
                                unit_price,
                                gst,
                                total,
                                sale_date
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                customer_name.strip(),
                                medicine_id,
                                medicine_name,
                                int(quantity),
                                price,
                                gst_amount,
                                grand_total,
                                sale_date
                            )
                        )

                        invoice_no = cursor.lastrowid

                        conn.commit()

                        st.session_state["last_invoice"] = {
                            "invoice_no": invoice_no,
                            "customer": customer_name.strip(),
                            "medicine": medicine_name,
                            "price": price,
                            "quantity": int(quantity),
                            "subtotal": subtotal,
                            "gst_rate": gst_rate,
                            "gst_amount": gst_amount,
                            "grand_total": grand_total,
                            "date": sale_date
                        }

                        st.success(
                            "Bill generated successfully!"
                        )

                except Exception as e:

                    conn.rollback()

                    st.error(
                        f"Billing error: {e}"
                    )

                finally:

                    conn.close()

        # SHOW AND DOWNLOAD INVOICE

        if "last_invoice" in st.session_state:

            invoice = st.session_state["last_invoice"]

            st.divider()

            st.subheader("Generated Invoice")

            st.write(
                f"Invoice Number: {invoice['invoice_no']}"
            )

            st.write(
                f"Customer: {invoice['customer']}"
            )

            st.write(
                f"Medicine: {invoice['medicine']}"
            )

            st.write(
                f"Medicine Amount: ₹{invoice['subtotal']:.2f}"
            )

            st.write(
                f"GST Amount: ₹{invoice['gst_amount']:.2f}"
            )

            st.subheader(
                f"Final Total: ₹{invoice['grand_total']:.2f}"
            )

            pdf_file = generate_invoice(invoice)

            st.download_button(
                label="Download PDF Invoice",
                data=pdf_file,
                file_name=f"invoice_{invoice['invoice_no']}.pdf",
                mime="application/pdf"
            )


# ==================================================
# EXPIRY ALERTS
# ==================================================

elif page == "Expiry Alerts":

    st.title("⚠️ Medicine Expiry Alerts")

    medicines_df = load_medicine_dataframe()

    if medicines_df.empty:

        st.info("No medicines available.")

    else:

        medicines_df["Expiry Date"] = pd.to_datetime(
            medicines_df["Expiry Date"],
            errors="coerce"
        )

        today = pd.Timestamp(date.today())

        expired = medicines_df[
            medicines_df["Expiry Date"] < today
        ]

        expiring_soon = medicines_df[
            (medicines_df["Expiry Date"] >= today)
            &
            (medicines_df["Expiry Date"] <= today + pd.Timedelta(days=30))
        ]

        st.subheader("Expired Medicines")

        if expired.empty:

            st.success("No expired medicines.")

        else:

            st.error(
                f"{len(expired)} expired medicine(s) found."
            )

            st.dataframe(
                expired,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader("Expiring Within 30 Days")

        if expiring_soon.empty:

            st.success(
                "No medicines expiring within 30 days."
            )

        else:

            st.warning(
                f"{len(expiring_soon)} medicine(s) expiring soon."
            )

            st.dataframe(
                expiring_soon,
                use_container_width=True,
                hide_index=True
            )


# ==================================================
# SALES REPORTS
# ==================================================

elif page == "Sales Reports":

    st.title("📊 Sales Reports")

    sales_df = load_sales()

    if sales_df.empty:

        st.info(
            "No sales records available yet."
        )

    else:

        sales_df["sale_date"] = pd.to_datetime(
            sales_df["sale_date"],
            errors="coerce"
        )

        total_revenue = float(
            sales_df["total"].sum()
        )

        total_gst = float(
            sales_df["gst"].sum()
        )

        total_items_sold = int(
            sales_df["quantity"].sum()
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Revenue",
            f"₹{total_revenue:,.2f}"
        )

        col2.metric(
            "Total GST",
            f"₹{total_gst:,.2f}"
        )

        col3.metric(
            "Items Sold",
            total_items_sold
        )

        st.divider()

        st.subheader("Sales History")

        st.dataframe(
            sales_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Medicine-wise Sales")

        medicine_sales = (
            sales_df.groupby("medicine_name")["quantity"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            medicine_sales,
            x="medicine_name",
            y="quantity",
            title="Quantity of Medicines Sold",
            labels={
                "medicine_name": "Medicine",
                "quantity": "Quantity Sold"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10182f",
            plot_bgcolor="#10182f",
            font_color="#ffffff"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Revenue Overview")

        daily_sales = (
            sales_df.dropna(subset=["sale_date"])
            .groupby(
                sales_df["sale_date"].dt.date
            )["total"]
            .sum()
            .reset_index()
        )

        daily_sales.columns = [
            "Date",
            "Revenue"
        ]

        fig2 = px.line(
            daily_sales,
            x="Date",
            y="Revenue",
            markers=True,
            title="Daily Revenue"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10182f",
            plot_bgcolor="#10182f",
            font_color="#ffffff"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        csv_data = sales_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Sales Report (CSV)",
            data=csv_data,
            file_name="pharmacy_sales_report.csv",
            mime="text/csv"
        )


# ==================================================
# FOOTER
# ==================================================

st.sidebar.divider()

st.sidebar.caption(
    "MediCare Plus | Pharmacy Management System"
)