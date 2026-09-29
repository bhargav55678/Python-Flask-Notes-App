from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "notes.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def index():
    connection = get_db_connection()
    notes = connection.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return render_template("index.html", notes=notes)


@app.route("/add", methods=["POST"])
def add_note():
    title = request.form["title"].strip()
    content = request.form["content"].strip()

    if title and content:
        connection = get_db_connection()

        connection.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content)
        )

        connection.commit()
        connection.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):

    connection = get_db_connection()

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if title and content:
            connection.execute(
                """
                UPDATE notes
                SET title = ?, content = ?
                WHERE id = ?
                """,
                (title, content, note_id)
            )

            connection.commit()

        connection.close()

        return redirect(url_for("index"))

    note = connection.execute(
        "SELECT * FROM notes WHERE id = ?",
        (note_id,)
    ).fetchone()

    connection.close()

    return render_template("edit.html", note=note)


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    initialize_database()

    app.run(debug=True)