from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date, datetime
import os

app = Flask(__name__)

# -------------------------------
# Database Connection (SAFE PATH)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------
# Home Page (User Search)
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------
# Admin Dashboard
# -------------------------------
@app.route("/admin")
def admin():
    return render_template("admin.html")

# -------------------------------
# Add Book
# -------------------------------
@app.route("/admin/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        book_id = int(request.form["book_id"])
        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO books (id, title, author, category, available, issue_date) VALUES (?, ?, ?, ?, 1, NULL)",
            (book_id, title, author, category)
        )
        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("add_book.html")

# -------------------------------
# Search Books (ID + Text)
# -------------------------------
@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    conn = get_db_connection()

    if query.isdigit():
        books = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (int(query),)
        ).fetchall()
    else:
        books = conn.execute(
            """
            SELECT * FROM books
            WHERE LOWER(title) LIKE ?
               OR LOWER(author) LIKE ?
               OR LOWER(category) LIKE ?
            ORDER BY title
            """,
            (f"%{query.lower()}%", f"%{query.lower()}%", f"%{query.lower()}%")
        ).fetchall()

    conn.close()
    return render_template("search.html", books=books)

# -------------------------------
# Issue Book (stores issue_date)
# -------------------------------
@app.route("/admin/issue", methods=["GET", "POST"])
def issue_book():
    message = None

    if request.method == "POST":
        try:
            book_id = int(request.form["book_id"])
        except ValueError:
            message = "Invalid Book ID."
            return render_template("issue_book.html", message=message)

        conn = get_db_connection()
        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book and book["available"] == 1:
            today = date.today().isoformat()

            conn.execute(
                "UPDATE books SET available = 0, issue_date = ? WHERE id = ?",
                (today, book_id)
            )
            conn.commit()
            message = "Book issued successfully."
        else:
            message = "Book not found or already issued."

        conn.close()

    return render_template("issue_book.html", message=message)

# -------------------------------
# Return Book + Fine Calculation
# -------------------------------
@app.route("/admin/return", methods=["GET", "POST"])
def return_book():
    message = None

    if request.method == "POST":
        try:
            book_id = int(request.form["book_id"])
        except ValueError:
            message = "Invalid Book ID."
            return render_template("return_book.html", message=message)

        conn = get_db_connection()
        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book and book["available"] == 0:
            issue_date = datetime.strptime(book["issue_date"], "%Y-%m-%d").date()
            today = date.today()
            days_kept = (today - issue_date).days

            fine = 0
            if days_kept > 7:
                fine = (days_kept - 7) * 5   # ₹5 per extra day

            conn.execute(
                "UPDATE books SET available = 1, issue_date = NULL WHERE id = ?",
                (book_id,)
            )
            conn.commit()

            message = f"Book returned successfully. Fine: ₹{fine}"
        else:
            message = "Book not found or already available."

        conn.close()

    return render_template("return_book.html", message=message)

# -------------------------------
# Delete Book
# -------------------------------
@app.route("/admin/delete", methods=["GET", "POST"])
def delete_book():
    message = None

    if request.method == "POST":
        try:
            book_id = int(request.form["book_id"])
        except ValueError:
            message = "Invalid Book ID."
            return render_template("delete_book.html", message=message)

        conn = get_db_connection()
        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book:
            conn.execute(
                "DELETE FROM books WHERE id = ?",
                (book_id,)
            )
            conn.commit()
            message = "Book deleted successfully."
        else:
            message = "Book not found."

        conn.close()

    return render_template("delete_book.html", message=message)

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
