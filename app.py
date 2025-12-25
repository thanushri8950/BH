from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/search")
def search():
    return render_template("search.html", books=[])

if __name__ == "__main__":
    app.run(debug=True)
