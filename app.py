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

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="MediCare Plus",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DATABASE ----------------

initialize_database()


def load_sales():
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT * FROM sales ORDER BY sale_date DESC",
            conn
        )
    finally:
        conn.close()


# ---------------- PDF GENERATION ----------------

def create_invoice_pdf(invoice):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle("MediCare Plus Invoice")

    pdf.setFillColorRGB(0.10, 0.16, 0.32)
    pdf.rect(0, height - 115, width, 115, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(50, height - 55, "MEDICARE PLUS")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(
        50, height - 78,
        "Pharmacy Management System"
    )

    pdf.setFillColorRGB(0.10, 0.16, 0.32)
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(50, height - 155, "CUSTOMER INVOICE")

    y = height - 195

    pdf.setFillColorRGB(0.12, 0.12, 0.18)
    pdf.setFont("Helvetica", 11)

    details = [
        ("Invoice Number", invoice["invoice_no"]),
        ("Date", invoice["date"]),
        ("Customer Name", invoice["customer"]),
        ("Medicine", invoice["medicine"]),
        ("Quantity", str(invoice["quantity"])),
        ("Unit Price", f"Rs. {invoice['unit_price']:.2f}"),
        ("Subtotal", f"Rs. {invoice['subtotal']:.2f}"),
        (
            f"GST ({invoice['gst_rate']}%)",
            f"Rs. {invoice['gst_amount']:.2f}"
        )
    ]

    for label, value in details:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(50, y, f"{label}:")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(190, y, str(value))

        y -= 27

    pdf.setStrokeColorRGB(0.35, 0.40, 0.55)
    pdf.line(50, y, width - 50, y)

    y -= 38

    pdf.setFillColorRGB(0.10, 0.16, 0.32)
    pdf.setFont("Helvetica-Bold", 17)

    pdf.drawString(
        50, y,
        f"TOTAL AMOUNT: Rs. {invoice['total']:.2f}"
    )

    y -= 65

    pdf.setFillColorRGB(0.25, 0.25, 0.30)
    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawString(
        50, y,
        "Thank you for visiting MediCare Plus!"
    )

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background: linear-gradient(
        135deg,
        #10182f 0%,
        #142b50 55%,
        #101a35 100%
    );
    color: #f5f7ff;
}

/* HEADER */

[data-testid="stHeader"] {
    background: rgba(10, 18, 38, 0.92);
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #111a36 0%,
        #192b50 100%
    );
    border-right: 1px solid rgba(180, 205, 255, 0.20);
}

section[data-testid="stSidebar"] * {
    color: #f2f5ff !important;
}

/* GENERAL TEXT */

.stApp p,
.stApp label,
.stApp .stMarkdown,
.stApp [data-testid="stCaptionContainer"] {
    color: #e5eaff;
}

/* HEADINGS */

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #f3f5ff !important;
}

/* INPUT FIELDS - BLACK TEXT */

.stApp input,
.stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    caret-color: #000000 !important;
    border-color: #9eacc2 !important;
}

/* INPUT PLACEHOLDERS */

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #666666 !important;
    -webkit-text-fill-color: #666666 !important;
    opacity: 1 !important;
}

/* DROPDOWN SELECTED TEXT */

.stApp [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
}

.stApp [data-baseweb="select"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* DROPDOWN MENU */

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background-color: #ffffff !important;
}

[data-baseweb="menu"] * {
    color: #000000 !important;
}

/* DATE PICKER */

[data-baseweb="calendar"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

[data-baseweb="calendar"] * {
    color: #000000 !important;
}

/* METRIC CARDS */

div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #244b7c,
        #263b68
    );
    border: 1px solid rgba(180, 210, 255, 0.28);
    padding: 17px 18px;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.18);
}

div[data-testid="stMetricLabel"] {
    color: #dbe8ff !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

/* SECTION CARDS */

.section-card {
    background: linear-gradient(
        145deg,
        #203b68,
        #1b2e55
    );
    border: 1px solid rgba(180, 210, 255, 0.22);
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
}

.section-card h2,
.section-card h3,
.section-card p {
    color: #ffffff !important;
}

/* WELCOME BANNER */

.welcome-banner {
    background: linear-gradient(
        105deg,
        #2454a0,
        #087eae
    );
    padding: 25px 30px;
    border-radius: 18px;
    margin: 5px 0 25px 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.20);
}

.welcome-banner h2 {
    color: #ffffff !important;
    margin: 0 0 8px 0;
}

.welcome-banner p {
    color: #eaf4ff !important;
    margin: 0;
}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(
        90deg,
        #356bc0,
        #1687b7
    ) !important;
    color: #ffffff !important;
    border: 0;
    border-radius: 9px;
    font-weight: 600;
}

.stButton > button *,
.stDownloadButton > button *,
.stFormSubmitButton > button * {
    color: #ffffff !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(
        90deg,
        #427bd2,
        #20a0d0
    ) !important;
    color: #ffffff !important;
}

/* ALERTS */

[data-testid="stAlert"] {
    border-radius: 10px;
}

/* ALERT TEXT */

[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #172033 !important;
}

/* TABLES */

div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    border: 1px solid rgba(180, 210, 255, 0.20);
    border-radius: 10px;
}

/* EXPANDERS */

[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 10px;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: #172033 !important;
}

/* CHECKBOXES AND RADIO BUTTONS */

.stApp [data-testid="stCheckbox"] label,
.stApp [data-testid="stRadio"] label {
    color: #f2f5ff !important;
}

/* DIVIDERS */

hr {
    border-color: rgba(210, 225, 255, 0.28);
}

/* CAPTIONS */

.stApp [data-testid="stCaptionContainer"] {
    color: #c6d7ff !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

medicines = get_medicines()
sales = load_sales()


# ---------------- SIDEBAR ----------------

st.sidebar.markdown(
    """
    <div style='text-align:center;padding:16px 4px 22px 4px;'>
        <div style='font-size:42px;'>💊</div>
        <h2 style='margin:4px 0;color:white;'>
            MediCare Plus
        </h2>
        <div style='font-size:11px;letter-spacing:1px;color:#c6d7ff;'>
            SMART PHARMACY SYSTEM
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### MAIN MENU")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "💊 Medicine Inventory",
        "➕ Add Medicine",
        "🧾 Billing",
        "⚠️ Expiry Alerts",
        "📊 Sales Reports"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.markdown("✦ **Pharmacy Management**")
st.sidebar.caption("Version 1.0 | Academic Project")


# ---------------- HEADER ----------------

st.markdown(
    """
    <div class="welcome-banner">
        <h2>Welcome to MediCare Plus 👋</h2>
        <p>Your intelligent pharmacy management workspace</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.subheader("📈 Business Overview")

    total_medicines = len(medicines)

    total_stock = sum(
        int(m[4]) for m in medicines
    )

    total_revenue = (
        sales["total"].sum()
        if not sales.empty else 0
    )

    total_transactions = len(sales)

    a, b, c, d = st.columns(4)

    a.metric("💊 Products", total_medicines)
    b.metric("📦 Stock Units", total_stock)
    c.metric("💰 Revenue", f"₹{total_revenue:,.2f}")
    d.metric("🧾 Transactions", total_transactions)

    st.divider()

    left, right = st.columns([1.5, 1])

    with left:

        st.subheader("📊 Sales Performance")

        if not sales.empty:

            chart_data = sales.copy()

            chart_data["sale_date"] = pd.to_datetime(
                chart_data["sale_date"],
                errors="coerce"
            )

            daily = (
                chart_data.dropna(subset=["sale_date"])
                .groupby("sale_date")["total"]
                .sum()
                .reset_index()
            )

            if not daily.empty:

                fig = px.bar(
                    daily,
                    x="sale_date",
                    y="total",
                    title="Revenue Trend",
                    template="plotly_dark"
                )

                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#ffffff"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:
                st.info(
                    "Sales dates are not available for the chart."
                )

        else:
            st.info(
                "Sales performance will appear after the first invoice."
            )

    with right:

        st.subheader("🚨 Stock Alerts")

        low_stock = [
            m for m in medicines if int(m[4]) <= 10
        ]

        if low_stock:

            for med in low_stock[:8]:
                st.warning(
                    f"{med[1]} — Only {med[4]} left"
                )

        else:
            st.success(
                "All medicine stock levels are healthy."
            )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📦 Low Stock Medicines")

        if low_stock:

            st.dataframe(
                pd.DataFrame(
                    low_stock,
                    columns=[
                        "ID", "Medicine", "Category",
                        "Price", "Stock", "Expiry", "Supplier"
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.success("No low-stock medicines.")

    with col2:

        st.subheader("🕒 Recently Added Medicines")

        if medicines:

            st.dataframe(
                pd.DataFrame(
                    medicines[-5:],
                    columns=[
                        "ID", "Medicine", "Category",
                        "Price", "Stock", "Expiry", "Supplier"
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No medicines available.")


# ==================================================
# MEDICINE INVENTORY
# ==================================================

elif page == "💊 Medicine Inventory":

    st.subheader("💊 Medicine Inventory")

    if medicines:

        df = pd.DataFrame(
            medicines,
            columns=[
                "ID", "Medicine", "Category",
                "Price", "Stock", "Expiry", "Supplier"
            ]
        )

        search = st.text_input("🔍 Search Medicine")

        if search:

            df = df[
                df["Medicine"].astype(str).str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🗑️ Remove Medicine")

        medicine_options = {
            f"{m[1]} (ID: {m[0]})": m[0]
            for m in medicines
        }

        selected_name = st.selectbox(
            "Select Medicine to Remove",
            list(medicine_options.keys())
        )

        if st.button("Delete Medicine"):

            medicine_id = medicine_options[selected_name]

            conn = get_connection()
            cursor = conn.cursor()

            try:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM sales
                    WHERE medicine_id = ?
                    """,
                    (medicine_id,)
                )

                if cursor.fetchone()[0] > 0:

                    st.error(
                        "This medicine has sales records "
                        "and cannot be deleted."
                    )

                else:

                    cursor.execute(
                        "DELETE FROM medicines WHERE id = ?",
                        (medicine_id,)
                    )

                    conn.commit()

                    st.success(
                        "Medicine deleted successfully!"
                    )

                    st.rerun()

            except Exception as e:

                conn.rollback()
                st.error(
                    f"Unable to delete medicine: {e}"
                )

            finally:
                conn.close()

    else:
        st.info(
            "No medicines available. Please add medicines."
        )


# ==================================================
# ADD MEDICINE
# ==================================================

elif page == "➕ Add Medicine":

    st.subheader("➕ Add New Medicine")

    with st.form("add_medicine_form"):

        name = st.text_input("Medicine Name")

        category = st.selectbox(
            "Category",
            [
                "Tablet",
                "Capsule",
                "Syrup",
                "Injection",
                "Powder",
                "Gel",
                "Cream",
                "Other"
            ]
        )

        price = st.number_input(
            "Price (₹)",
            min_value=0.01,
            step=1.0
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0,
            step=1
        )

        expiry = st.date_input("Expiry Date")

        supplier = st.text_input("Supplier Name")

        submitted = st.form_submit_button(
            "Add Medicine"
        )

        if submitted:

            if not name.strip():

                st.error("Enter medicine name.")

            elif not supplier.strip():

                st.error("Enter supplier name.")

            else:

                try:

                    add_medicine(
                        name.strip(),
                        category,
                        price,
                        quantity,
                        str(expiry),
                        supplier.strip()
                    )

                    st.success(
                        "Medicine added successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Unable to add medicine: {e}"
                    )


# ==================================================
# BILLING
# ==================================================

elif page == "🧾 Billing":

    st.subheader("🧾 Customer Billing")

    st.write(
        "Create a new pharmacy invoice."
    )

    available = [
        m for m in medicines if int(m[4]) > 0
    ]

    if available:

        with st.form("billing_form"):

            customer = st.text_input(
                "Customer Name"
            )

            selected = st.selectbox(
                "Select Medicine",
                available,
                format_func=lambda m:
                    f"{m[1]} | ₹{float(m[3]):.2f} | Stock: {m[4]}"
            )

            qty = st.number_input(
                "Quantity",
                min_value=1,
                max_value=int(selected[4]),
                step=1
            )

            gst_rate = st.selectbox(
                "GST Rate (%)",
                [0, 5, 12, 18, 28]
            )

            subtotal = (
                float(selected[3]) * int(qty)
            )

            gst_amount = (
                subtotal * gst_rate / 100
            )

            total = (
                subtotal + gst_amount
            )

            st.markdown(
                f"""
                <div class="section-card">
                    <h3>Invoice Preview</h3>
                    <p>Subtotal: ₹{subtotal:.2f}</p>
                    <p>GST ({gst_rate}%): ₹{gst_amount:.2f}</p>
                    <h2>Total: ₹{total:.2f}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

            submitted = st.form_submit_button(
                "🧾 Generate Invoice"
            )

        if submitted:

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
                        (
                            int(qty),
                            selected[0],
                            int(qty)
                        )
                    )

                    if cursor.rowcount == 1:

                        invoice_no = datetime.now().strftime(
                            "%Y%m%d%H%M%S%f"
                        )

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
                                customer.strip(),
                                selected[0],
                                selected[1],
                                int(qty),
                                float(selected[3]),
                                gst_amount,
                                total,
                                str(date.today())
                            )
                        )

                        conn.commit()

                        st.session_state[
                            "generated_invoice"
                        ] = {
                            "invoice_no": invoice_no,
                            "customer": customer.strip(),
                            "medicine": selected[1],
                            "quantity": int(qty),
                            "unit_price": float(selected[3]),
                            "subtotal": subtotal,
                            "gst_rate": gst_rate,
                            "gst_amount": gst_amount,
                            "total": total,
                            "date": str(date.today())
                        }

                        st.success(
                            "Invoice generated successfully!"
                        )

                        st.rerun()

                    else:

                        conn.rollback()

                        st.error(
                            "Insufficient stock. "
                            "Please refresh and try again."
                        )

                except Exception as e:

                    conn.rollback()

                    st.error(
                        f"Unable to generate invoice: {e}"
                    )

                finally:
                    conn.close()

        # DISPLAY GENERATED INVOICE

        invoice = st.session_state.get(
            "generated_invoice"
        )

        if invoice:

            st.divider()

            st.success(
                "Invoice generated successfully!"
            )

            st.subheader("🧾 Generated Invoice")

            st.write(
                "**Invoice Number:**",
                invoice["invoice_no"]
            )

            st.write(
                "**Date:**",
                invoice["date"]
            )

            st.write(
                "**Customer:**",
                invoice["customer"]
            )

            st.write(
                "**Medicine:**",
                invoice["medicine"]
            )

            st.write(
                "**Quantity:**",
                invoice["quantity"]
            )

            st.write(
                "**Unit Price:**",
                f"₹{invoice['unit_price']:.2f}"
            )

            st.write(
                "**Subtotal:**",
                f"₹{invoice['subtotal']:.2f}"
            )

            st.write(
                f"**GST ({invoice['gst_rate']}%):**",
                f"₹{invoice['gst_amount']:.2f}"
            )

            st.markdown(
                f"## Total: ₹{invoice['total']:.2f}"
            )

            pdf_file = create_invoice_pdf(invoice)

            st.download_button(
                label="⬇️ Download Invoice PDF",
                data=pdf_file,
                file_name=(
                    f"Invoice_{invoice['invoice_no']}.pdf"
                ),
                mime="application/pdf"
            )

            if st.button("Clear Invoice"):

                del st.session_state[
                    "generated_invoice"
                ]

                st.rerun()

    else:

        st.warning(
            "Please add medicines before billing."
        )


# ==================================================
# EXPIRY ALERTS
# ==================================================

elif page == "⚠️ Expiry Alerts":

    st.subheader(
        "⚠️ Medicine Expiry Management"
    )

    if medicines:

        df = pd.DataFrame(
            medicines,
            columns=[
                "ID", "Medicine", "Category",
                "Price", "Stock", "Expiry", "Supplier"
            ]
        )

        df["Expiry"] = pd.to_datetime(
            df["Expiry"],
            errors="coerce"
        )

        today = pd.Timestamp(date.today())

        expired = df[
            df["Expiry"] < today
        ]

        upcoming = df[
            (df["Expiry"] >= today) &
            (
                df["Expiry"] <=
                today + pd.Timedelta(days=90)
            )
        ]

        a, b = st.columns(2)

        a.metric(
            "Expired Medicines",
            len(expired)
        )

        b.metric(
            "Expiring Soon",
            len(upcoming)
        )

        st.subheader(
            "🚨 Expired Medicines"
        )

        st.dataframe(
            expired,
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "⏳ Expiring Within 90 Days"
        )

        st.dataframe(
            upcoming,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No medicine records found."
        )


# ==================================================
# SALES REPORTS
# ==================================================

elif page == "📊 Sales Reports":

    st.subheader(
        "📊 Sales Analytics"
    )

    if not sales.empty:

        report_sales = sales.copy()

        report_sales["sale_date"] = pd.to_datetime(
            report_sales["sale_date"],
            errors="coerce"
        )

        a, b, c = st.columns(3)

        a.metric(
            "Total Revenue",
            f"₹{report_sales['total'].sum():,.2f}"
        )

        b.metric(
            "Transactions",
            len(report_sales)
        )

        c.metric(
            "Items Sold",
            int(report_sales["quantity"].sum())
        )

        daily = (
            report_sales.dropna(subset=["sale_date"])
            .groupby("sale_date")["total"]
            .sum()
            .reset_index()
        )

        if not daily.empty:

            fig = px.bar(
                daily,
                x="sale_date",
                y="total",
                template="plotly_dark",
                title="Daily Revenue"
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader("Sales History")

        st.dataframe(
            report_sales,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Sales CSV",
            report_sales.to_csv(index=False),
            "pharmacy_sales.csv",
            "text/csv"
        )

    else:

        st.info(
            "Sales reports will appear after generating invoices."
        )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "💜 MediCare Plus | Pharmacy Management System"
)