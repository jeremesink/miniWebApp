from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from utils import generate_invoice_pdf


app = Flask(__name__)

db_path = 'project.db'

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/intake", methods=["GET", "POST"])
def intake_form():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch dropdown options
    cursor.execute("SELECT customer_id, business_name FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT SKU_ID, SKU_Name FROM SKUs")
    skus = cursor.fetchall()

    if request.method == "POST":
        customer_id = request.form["customerID"]
        sku_id = request.form["skuID"]
        job_description = request.form["description"]
        cost = request.form["cost"]

        cursor.execute("""
            INSERT INTO job_requests (customer_id, SKU_ID, job_description, job_cost)
            VALUES (?, ?, ?, ?)
        """, (customer_id, sku_id, job_description, cost))
        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()
    return render_template("form.html", customers=customers, skus=skus)

@app.route("/notifications")
def show_notifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT customer_id, SKU_ID, job_description, job_cost
        FROM job_requests
        ORDER BY customer_id DESC
    """)
    notifications = cursor.fetchall()
    conn.close()

    return render_template("notifications.html", notifications=notifications)

@app.route("/bids")
def show_bids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bid_id, job_id, pros_id, bid_amount, bid_status, bid_date
        FROM bids
        ORDER BY bid_id
    """)
    bids = cursor.fetchall()
    conn.close()

    return render_template("bids.html", bids=bids)

@app.route("/bid_on_job", methods=["GET", "POST"])
def bid_on_job():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT job_id FROM job_requests")
    job_ids = [row["job_id"] for row in cursor.fetchall()]

    cursor.execute("SELECT pros_id FROM pros")
    pros_ids = [row["pros_id"] for row in cursor.fetchall()]

    if request.method == "POST":
        job_id = request.form["job_id"]
        pros_id = request.form["pros_id"]
        bid_amount = request.form["bid_amount"]
        bid_status = request.form["bid_status"]
        bid_date = request.form["bid_date"]

        cursor.execute("""
            INSERT INTO bids (job_id, pros_id, bid_amount, bid_status, bid_date)
            VALUES (?, ?, ?, ?, ?)
        """, (job_id, pros_id, bid_amount, bid_status, bid_date))
        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()
    return render_template("bid_on_job.html", job_ids=job_ids, pros_ids=pros_ids)

@app.route("/draft_invoice", methods=["GET", "POST"])
def draft_invoice():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all customers
    cursor.execute("SELECT customer_id, business_name FROM customers")
    customers = cursor.fetchall()

    selected_customer_id = None
    drafts = []

    if request.method == "POST":
        selected_customer_id = request.form["customer_id"]
        description = request.form["description"]
        cost = request.form["cost"]

        cursor.execute("""
            INSERT INTO draft_invoices (customer_id, description, cost)
            VALUES (?, ?, ?)
        """, (selected_customer_id, description, cost))
        conn.commit()

        # ✅ These lines must be **indented under the POST block**
        invoice_id = cursor.lastrowid
        generate_invoice_pdf(invoice_id, selected_customer_id, description, float(cost))
        conn.close()

        return redirect(url_for("draft_invoice", customer_id=selected_customer_id))

    # --- GET request (or after redirect) ---
    selected_customer_id = request.args.get("customer_id")
    if selected_customer_id:
        cursor.execute("""
            SELECT invoice_id, description, cost
            FROM draft_invoices
            WHERE customer_id = ?
        """, (selected_customer_id,))
        drafts = cursor.fetchall()

    conn.close()

    return render_template("draft_invoice.html",
                           customers=customers,
                           selected_customer_id=selected_customer_id,
                           drafts=drafts)

@app.route("/view_invoices")
def view_invoices():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT invoice_id, customer_id, description, cost
        FROM draft_invoices
        ORDER BY customer_id DESC
    """)
    invoices = cursor.fetchall()

    conn.close()

    # Pass 'invoices' (list of all rows) to the template
    return render_template("view_invoices.html", invoices=invoices)

if __name__ == "__main__":
    app.run(debug=True)
