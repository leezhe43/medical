
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os





# =========================================================
# Flask 設定
# =========================================================

app = Flask(__name__)

app.secret_key = "family-health-secret-key"


# =========================================================
# 資料庫路徑
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "booking.db")


# =========================================================
# 資料庫連線
# =========================================================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    # 讓查詢結果可以使用：
    # booking["name"]
    # booking["phone"]
    # booking["email"]

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# 初始化資料庫
# =========================================================

def init_db():

    conn = sqlite3.connect(DATABASE)


    # -----------------------------------------------------
    # 建立資料表
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            phone TEXT NOT NULL,

            email TEXT,

            booking_date TEXT NOT NULL,

            booking_time TEXT,

            service TEXT,

            message TEXT,

            status TEXT DEFAULT '待確認',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # -----------------------------------------------------
    # 檢查目前資料表有哪些欄位
    # -----------------------------------------------------

    columns = conn.execute(
        "PRAGMA table_info(bookings)"
    ).fetchall()


    # 注意：
    # sqlite3.connect() 沒有設定 row_factory
    # 所以這裡的 column 是 tuple。
    #
    # column[0] = cid
    # column[1] = name
    # column[2] = type
    #
    # 所以要使用 column[1]

    column_names = [
        column[1]
        for column in columns
    ]


    # -----------------------------------------------------
    # 如果舊資料庫沒有 booking_time
    # 就新增欄位
    # -----------------------------------------------------

    if "booking_time" not in column_names:

        conn.execute("""
            ALTER TABLE bookings
            ADD COLUMN booking_time TEXT
        """)


    # -----------------------------------------------------
    # 如果舊資料庫沒有 service
    # 就新增欄位
    # -----------------------------------------------------

    if "service" not in column_names:

        conn.execute("""
            ALTER TABLE bookings
            ADD COLUMN service TEXT
        """)


    # -----------------------------------------------------
    # 如果舊資料庫沒有 status
    # 就新增欄位
    # -----------------------------------------------------

    if "status" not in column_names:

        conn.execute("""
            ALTER TABLE bookings
            ADD COLUMN status TEXT DEFAULT '待確認'
        """)


    conn.commit()

    conn.close()


# =========================================================
# 首頁
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# 新增預約
# =========================================================

@app.route("/booking", methods=["POST"])
def booking():

    # -----------------------------------------------------
    # 取得表單資料
    # -----------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()


    phone = request.form.get(
        "phone",
        ""
    ).strip()


    email = request.form.get(
        "email",
        ""
    ).strip()


    booking_date = request.form.get(
        "booking_date",
        ""
    ).strip()


    booking_time = request.form.get(
        "booking_time",
        ""
    ).strip()


    service = request.form.get(
        "service",
        ""
    ).strip()


    message = request.form.get(
        "message",
        ""
    ).strip()


    # -----------------------------------------------------
    # 基本驗證
    # -----------------------------------------------------

    if not name:

        flash(
            "請填寫姓名。",
            "danger"
        )

        return redirect(
            url_for("home") + "#booking"
        )


    if not phone:

        flash(
            "請填寫電話。",
            "danger"
        )

        return redirect(
            url_for("home") + "#booking"
        )


    if not booking_date:

        flash(
            "請選擇預約日期。",
            "danger"
        )

        return redirect(
            url_for("home") + "#booking"
        )


    if not booking_time:

        flash(
            "請選擇預約時間。",
            "danger"
        )

        return redirect(
            url_for("home") + "#booking"
        )


    if not service:

        flash(
            "請選擇預約服務。",
            "danger"
        )

        return redirect(
            url_for("home") + "#booking"
        )


    # -----------------------------------------------------
    # 寫入資料庫
    # -----------------------------------------------------

    conn = get_db_connection()


    conn.execute("""
        INSERT INTO bookings
        (
            name,
            phone,
            email,
            booking_date,
            booking_time,
            service,
            message,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        booking_date,
        booking_time,
        service,
        message,
        "待確認"
    ))


    conn.commit()

    conn.close()


    # -----------------------------------------------------
    # 成功訊息
    # -----------------------------------------------------

    flash(
        "預約成功！我們已收到您的資料。",
        "success"
    )


    return redirect(
        url_for("home") + "#booking"
    )


# =========================================================



# AI 查詢預約資料
# =========================================================

@app.route("/ai-query", methods=["GET", "POST"])
def ai_query():

    result = None
    question = ""

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        if not question:

            result = "請輸入問題。"

        else:

            # -------------------------------------------------
            # 查詢預約總數
            # -------------------------------------------------

            if "幾筆" in question or "多少筆" in question:

                conn = get_db_connection()

                count = conn.execute("""
                    SELECT COUNT(*)
                    FROM bookings
                """).fetchone()[0]

                conn.close()

                result = f"目前共有 {count} 筆預約。"

            else:

                result = (
                    "目前可以查詢預約總數，"
                    "例如：「目前有幾筆預約？」"
                )

    return render_template(
        "ai_query.html",
        question=question,
        result=result
    )
    
# =========================================================
# 管理後台
# =========================================================

@app.route("/admin")
def admin():

    conn = get_db_connection()


    bookings = conn.execute("""
        SELECT *
        FROM bookings
        ORDER BY id DESC
    """).fetchall()


    conn.close()


    return render_template(
        "admin.html",
        bookings=bookings
    )


# =========================================================
# 刪除預約
# =========================================================

@app.route(
    "/admin/delete/<int:booking_id>",
    methods=["POST"]
)
def delete_booking(booking_id):

    conn = get_db_connection()


    conn.execute(
        """
        DELETE FROM bookings
        WHERE id = ?
        """,
        (booking_id,)
    )


    conn.commit()

    conn.close()


    flash(
        "預約資料已刪除。",
        "success"
    )


    return redirect(
        url_for("admin")
    )


# =========================================================
# 修改預約狀態
# =========================================================

@app.route(
    "/admin/status/<int:booking_id>",
    methods=["POST"]
)
def update_status(booking_id):

    status = request.form.get(
        "status",
        ""
    ).strip()


    # 允許的狀態

    allowed_status = [

        "待確認",

        "已確認",

        "已完成",

        "已取消"

    ]


    # -----------------------------------------------------
    # 檢查狀態是否合法
    # -----------------------------------------------------

    if status not in allowed_status:

        flash(
            "無效的預約狀態。",
            "danger"
        )

        return redirect(
            url_for("admin")
        )


    # -----------------------------------------------------
    # 更新資料庫
    # -----------------------------------------------------

    conn = get_db_connection()


    conn.execute(
        """
        UPDATE bookings
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            booking_id
        )
    )


    conn.commit()

    conn.close()


    flash(
        "預約狀態已更新。",
        "success"
    )


    return redirect(
        url_for("admin")
    )


# =========================================================
# 初始化資料庫
# =========================================================

init_db()


# =========================================================
# 啟動 Flask
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )

