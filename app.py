from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "family-health-secret-key"

DATABASE = "booking.db"


# =========================
# 建立資料庫
# =========================
def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            booking_date TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =========================
# 首頁
# =========================
@app.route("/")
def home():
    return render_template("index.template")


# =========================
# 線上預約
# =========================
@app.route("/booking", methods=["POST"])
def booking():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    booking_date = request.form.get("booking_date", "").strip()
    message = request.form.get("message", "").strip()

    # 基本檢查
    if not name or not phone or not booking_date:
        flash("請填寫姓名、電話與預約日期。")
        return redirect(url_for("home") + "#booking")

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO bookings
        (name, phone, email, booking_date, message)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        booking_date,
        message
    ))

    conn.commit()
    conn.close()

    flash("預約成功！我們已收到您的資料。")

    return redirect(url_for("home") + "#booking")


# =========================
# 管理員查看預約
# =========================
@app.route("/admin")
def admin():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    bookings = conn.execute("""
        SELECT *
        FROM bookings
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin.template",
        bookings=bookings
    )


# =========================
# 刪除預約
# =========================
@app.route("/admin/delete/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "DELETE FROM bookings WHERE id = ?",
        (booking_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# =========================
# 程式開始
# =========================
if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )