from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# -------------------------------
# Database Connection Function
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------
# Home Page (User Search Page)
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
# Add Book (Admin)
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
            "INSERT INTO books (id, title, author, category, available) VALUES (?, ?, ?, ?, 1)",
            (book_id, title, author, category)
        )
        conn.commit()
        conn.close()
        return redirect("/admin")
    return render_template("add_book.html")


# -------------------------------
# Search Books (User)
# -------------------------------
@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    conn = get_db_connection()

    # CASE 1: Numeric input → search by ID
    if query.isdigit():
        books = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (int(query),)
        ).fetchall()
    else:
        # CASE 2: Text input → search by title, author, category
        books = conn.execute(
            """
            SELECT * FROM books
            WHERE LOWER(title) LIKE LOWER(?)
               OR LOWER(author) LIKE LOWER(?)
               OR LOWER(category) LIKE LOWER(?)
            ORDER BY title
            """,
            (f"%{query}%", f"%{query}%", f"%{query}%")
        ).fetchall()

    conn.close()
    return render_template("search.html", books=books)

# -------------------------------
# Issue Book (Admin)
# -------------------------------
@app.route("/admin/issue", methods=["GET", "POST"])
def issue_book():
    message = None
    if request.method == "POST":
        book_id = request.form["book_id"]
        try:
            book_id = int(book_id)
        except ValueError:
            message = "Invalid Book ID."
            return render_template("issue_book.html", message=message)

        conn = get_db_connection()
        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book and book["available"] == 1:
            conn.execute(
                "UPDATE books SET available = 0 WHERE id = ?",
                (book_id,)
            )
            conn.commit()
            message = "Book issued successfully."
        else:
            message = "Book not found or already issued."

        conn.close()
    return render_template("issue_book.html", message=message)

# -------------------------------
# Return Book (Admin)
# -------------------------------
@app.route("/admin/return", methods=["GET", "POST"])
def return_book():
    message = None
    if request.method == "POST":
        book_id = request.form["book_id"]
        try:
            book_id = int(book_id)
        except ValueError:
            message = "Invalid Book ID."
            return render_template("return_book.html", message=message)

        conn = get_db_connection()
        book = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book and book["available"] == 0:
            conn.execute(
                "UPDATE books SET available = 1 WHERE id = ?",
                (book_id,)
            )
            conn.commit()
            message = "Book returned successfully."
        else:
            message = "Book not found or already available."

        conn.close()
    return render_template("return_book.html", message=message)

# -------------------------------
# Delete Book (Admin)
# -------------------------------
@app.route("/admin/delete", methods=["GET", "POST"])
def delete_book():
    message = None
    if request.method == "POST":
        book_id = request.form["book_id"]
        try:
            book_id = int(book_id)
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
            message = f"Book ID {book_id} deleted successfully."
        else:
            message = "Book not found."

        conn.close()
    return render_template("delete_book.html", message=message)

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
