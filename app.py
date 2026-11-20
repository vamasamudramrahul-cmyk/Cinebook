"""
app.py
------
CINEBOOK - a beginner-friendly Flask + SQLite movie booking demo.

This is a LEARNING / REFERENCE project. It simulates a cinema booking
flow (browse movies -> pick a show -> pick seats -> confirm booking)
using entirely fictional sample data. It does NOT process real
payments and is not connected to any real cinema.

Run with:
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cinebook-demo-secret-key"  # fine for a local demo project only

DB_PATH = os.path.join("database", "cinebook.db")


# ----------------------------------------------------------------
# Database helper
# ----------------------------------------------------------------
def get_db_connection():
    """
    Opens a new connection to the SQLite database.
    row_factory = sqlite3.Row lets us access columns by name,
    e.g. row["title"] instead of row[0]. This makes templates
    much easier to read.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ----------------------------------------------------------------
# Home page
# ----------------------------------------------------------------
@app.route("/")
def home():
    conn = get_db_connection()
    movies = conn.execute("SELECT * FROM movies ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", movies=movies)


# ----------------------------------------------------------------
# Movie listing (all movies)
# ----------------------------------------------------------------
@app.route("/movies")
def movies_list():
    conn = get_db_connection()
    movies = conn.execute("SELECT * FROM movies ORDER BY title").fetchall()
    conn.close()
    return render_template("movies.html", movies=movies)


# ----------------------------------------------------------------
# Movie details + its shows
# ----------------------------------------------------------------
@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):
    conn = get_db_connection()
    movie = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()

    if movie is None:
        conn.close()
        flash("That movie does not exist.")
        return redirect(url_for("movies_list"))

    shows = conn.execute(
        """SELECT shows.id, shows.show_date, shows.show_time, shows.price,
                  theatres.name AS theatre_name, theatres.location AS theatre_location,
                  (SELECT COUNT(*) FROM seats
                   WHERE seats.show_id = shows.id AND seats.is_booked = 0) AS seats_available
           FROM shows
           JOIN theatres ON shows.theatre_id = theatres.id
           WHERE shows.movie_id = ?
           ORDER BY shows.show_date, shows.show_time""",
        (movie_id,),
    ).fetchall()
    conn.close()

    return render_template("movie_details.html", movie=movie, shows=shows)


# ----------------------------------------------------------------
# Seat selection for a specific show
# ----------------------------------------------------------------
@app.route("/show/<int:show_id>/seats")
def select_seats(show_id):
    conn = get_db_connection()

    show = conn.execute(
        """SELECT shows.id, shows.show_date, shows.show_time, shows.price,
                  movies.title AS movie_title, movies.id AS movie_id,
                  theatres.name AS theatre_name
           FROM shows
           JOIN movies ON shows.movie_id = movies.id
           JOIN theatres ON shows.theatre_id = theatres.id
           WHERE shows.id = ?""",
        (show_id,),
    ).fetchone()

    if show is None:
        conn.close()
        flash("That show does not exist.")
        return redirect(url_for("movies_list"))

    seats = conn.execute(
        "SELECT * FROM seats WHERE show_id = ? ORDER BY seat_label", (show_id,)
    ).fetchall()
    conn.close()

    # Group seats by row letter (A, B, C, D) so the template can
    # print one row at a time - purely a display convenience.
    seat_rows = {}
    for seat in seats:
        row_letter = seat["seat_label"][0]
        seat_rows.setdefault(row_letter, []).append(seat)

    return render_template("seats.html", show=show, seat_rows=seat_rows)


# ----------------------------------------------------------------
# Booking: receives selected seats from the seat-selection form
# ----------------------------------------------------------------
@app.route("/show/<int:show_id>/book", methods=["POST"])
def create_booking(show_id):
    conn = get_db_connection()

    show = conn.execute("SELECT * FROM shows WHERE id = ?", (show_id,)).fetchone()
    if show is None:
        conn.close()
        flash("That show does not exist.")
        return redirect(url_for("movies_list"))

    selected_seat_ids = request.form.getlist("seat_ids")  # list of strings
    customer_name = request.form.get("customer_name", "").strip()

    # ---- Validation -------------------------------------------------
    if not customer_name:
        conn.close()
        flash("Please enter a name for the booking.")
        return redirect(url_for("select_seats", show_id=show_id))

    if len(selected_seat_ids) == 0:
        conn.close()
        flash("Please select at least one seat.")
        return redirect(url_for("select_seats", show_id=show_id))

    # Re-check seat availability on the server (never trust the client).
    # This prevents double-booking if two people select the same seat
    # at nearly the same time.
    placeholders = ",".join("?" for _ in selected_seat_ids)
    seats = conn.execute(
        f"SELECT * FROM seats WHERE id IN ({placeholders}) AND show_id = ?",
        (*selected_seat_ids, show_id),
    ).fetchall()

    if len(seats) != len(selected_seat_ids):
        conn.close()
        flash("One or more selected seats are invalid. Please try again.")
        return redirect(url_for("select_seats", show_id=show_id))

    already_booked = [s for s in seats if s["is_booked"] == 1]
    if already_booked:
        conn.close()
        flash("Sorry, one or more selected seats were just booked by someone else. "
              "Please choose different seats.")
        return redirect(url_for("select_seats", show_id=show_id))

    # ---- Calculate total ---------------------------------------------
    num_seats = len(seats)
    total_amount = num_seats * show["price"]

    # ---- Save booking (simulated - no real payment) -------------------
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        """INSERT INTO bookings (show_id, customer_name, num_seats, total_amount, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (show_id, customer_name, num_seats, total_amount, created_at),
    )
    booking_id = cursor.lastrowid

    for seat in seats:
        conn.execute(
            "INSERT INTO booking_seats (booking_id, seat_id) VALUES (?, ?)",
            (booking_id, seat["id"]),
        )
        conn.execute("UPDATE seats SET is_booked = 1 WHERE id = ?", (seat["id"],))

    conn.commit()
    conn.close()

    return redirect(url_for("booking_confirmation", booking_id=booking_id))


# ----------------------------------------------------------------
# Booking confirmation page
# ----------------------------------------------------------------
@app.route("/booking/<int:booking_id>/confirmation")
def booking_confirmation(booking_id):
    conn = get_db_connection()

    booking = conn.execute(
        """SELECT bookings.*, shows.show_date, shows.show_time,
                  movies.title AS movie_title, theatres.name AS theatre_name
           FROM bookings
           JOIN shows ON bookings.show_id = shows.id
           JOIN movies ON shows.movie_id = movies.id
           JOIN theatres ON shows.theatre_id = theatres.id
           WHERE bookings.id = ?""",
        (booking_id,),
    ).fetchone()

    if booking is None:
        conn.close()
        flash("That booking does not exist.")
        return redirect(url_for("movies_list"))

    seat_labels = conn.execute(
        """SELECT seats.seat_label FROM booking_seats
           JOIN seats ON booking_seats.seat_id = seats.id
           WHERE booking_seats.booking_id = ?
           ORDER BY seats.seat_label""",
        (booking_id,),
    ).fetchall()
    conn.close()

    seat_list = [row["seat_label"] for row in seat_labels]

    return render_template("confirmation.html", booking=booking, seat_list=seat_list)


# ----------------------------------------------------------------
# Simple error handling for unknown pages
# ----------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("No database found. Run 'python init_db.py' first.")
    app.run(debug=True)
