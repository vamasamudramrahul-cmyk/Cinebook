"""
init_db.py
----------
Run this file ONCE to create and populate the CINEBOOK database.

    python init_db.py

It will:
1. Delete any old database file (so you always start fresh).
2. Create all tables using database/schema.sql
3. Insert sample movies, theatres, shows, and seats.

All data below is FICTIONAL SAMPLE DATA created for this learning
project. It does not represent any real cinema, real movie, or
real showtime.
"""

import sqlite3
import os

DB_PATH = os.path.join("database", "cinebook.db")
SCHEMA_PATH = os.path.join("database", "schema.sql")


def create_tables(conn):
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())


def seed_movies(conn):
    movies = [
        # title, genre, language, duration, rating, description, poster_color
        ("The Last Signal", "Sci-Fi / Thriller", "English", 128, "PG-13",
         "A sample sci-fi story: a research crew on a remote station receives "
         "a signal that shouldn't exist. (Fictional sample movie.)", "#2563eb"),
        ("Monsoon Melody", "Romance / Drama", "Hindi", 142, "U",
         "A sample romantic drama about two musicians who meet during monsoon "
         "season. (Fictional sample movie.)", "#db2777"),
        ("Laugh Track", "Comedy", "English", 101, "PG",
         "A sample workplace comedy about a chaotic small-town radio station. "
         "(Fictional sample movie.)", "#f59e0b"),
        ("Iron Circuit", "Action", "English", 135, "PG-13",
         "A sample action film about a retired engineer pulled back for one "
         "last job. (Fictional sample movie.)", "#dc2626"),
        ("Whispering Pines", "Horror / Mystery", "English", 112, "R",
         "A sample horror story set in an isolated mountain town. "
         "(Fictional sample movie.)", "#4b5563"),
        ("Little Chef", "Animation / Family", "English", 96, "U",
         "A sample animated film about a young raccoon who dreams of running "
         "a restaurant. (Fictional sample movie.)", "#16a34a"),
    ]
    conn.executemany(
        """INSERT INTO movies (title, genre, language, duration, rating, description, poster_color)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        movies,
    )


def seed_theatres(conn):
    theatres = [
        ("Screen 1", "CineBook Sample Cinema - Downtown"),
        ("Screen 2", "CineBook Sample Cinema - Downtown"),
        ("Screen 3", "CineBook Sample Cinema - Uptown"),
    ]
    conn.executemany(
        "INSERT INTO theatres (name, location) VALUES (?, ?)", theatres
    )


def seed_shows(conn):
    # A handful of shows spread across movies/theatres/dates/times.
    # (movie_id, theatre_id, show_date, show_time, price)
    shows = [
        (1, 1, "2026-09-16", "10:30", 220.0),
        (1, 2, "2026-09-16", "18:00", 250.0),
        (2, 1, "2026-09-16", "13:00", 200.0),
        (2, 3, "2026-09-17", "20:15", 260.0),
        (3, 2, "2026-09-16", "16:45", 200.0),
        (4, 3, "2026-09-17", "11:00", 230.0),
        (4, 1, "2026-09-17", "21:00", 250.0),
        (5, 2, "2026-09-18", "22:00", 240.0),
        (6, 3, "2026-09-16", "09:30", 180.0),
        (6, 1, "2026-09-18", "15:00", 180.0),
    ]
    conn.executemany(
        """INSERT INTO shows (movie_id, theatre_id, show_date, show_time, price)
           VALUES (?, ?, ?, ?, ?)""",
        shows,
    )


def seed_seats(conn):
    # Give every show a small, easy-to-read seat map: rows A-D, seats 1-6
    # (24 seats per show). Small on purpose - easier to learn from.
    cur = conn.execute("SELECT id FROM shows")
    show_ids = [row[0] for row in cur.fetchall()]

    rows = ["A", "B", "C", "D"]
    seats_per_row = 6

    seat_rows = []
    for show_id in show_ids:
        for row in rows:
            for num in range(1, seats_per_row + 1):
                seat_label = f"{row}{num}"
                seat_rows.append((show_id, seat_label, 0))  # 0 = not booked

    conn.executemany(
        "INSERT INTO seats (show_id, seat_label, is_booked) VALUES (?, ?, ?)",
        seat_rows,
    )


def mark_sample_booked_seats(conn):
    """
    Pre-book a few seats on the first show so the seat-selection
    screen has a realistic mix of free/booked seats to demonstrate.
    """
    conn.execute(
        """UPDATE seats SET is_booked = 1
           WHERE show_id = 1 AND seat_label IN ('A1', 'A2', 'B3')"""
    )


def main():
    os.makedirs("database", exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    create_tables(conn)
    seed_movies(conn)
    seed_theatres(conn)
    seed_shows(conn)
    seed_seats(conn)
    mark_sample_booked_seats(conn)

    conn.commit()
    conn.close()

    print(f"Database created and seeded successfully at {DB_PATH}")


if __name__ == "__main__":
    main()
